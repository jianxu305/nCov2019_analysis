import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as mfm
font_path = './STFANGSO.TTF'  # for displaying Chinese characters in plots
font_prop = mfm.FontProperties(fname=font_path)

DXY_DATA_PATH = 'https://raw.githubusercontent.com/BlankerL/DXY-2019-nCoV-Data/master/csv/DXYArea.csv'

def load_chinese_data():
    data = pd.read_csv(DXY_DATA_PATH)
    data['updateTime'] = pd.to_datetime(data['updateTime'])  # original type of updateTime after read_csv is 'str'
    data['updateDate'] = data['updateTime'].dt.date    # add date for daily aggregation
    return data


def aggDaily(df):
    '''Aggregate the frequent time series data into a daily frame, ie, one entry per (date, province, city)'''
    frm_list = []
    drop_cols = ['province_' + field for field in ['confirmedCount', 'suspectedCount', 'curedCount', 'deadCount']]  # these can be computed later
    for key, frm in df.drop(columns=drop_cols).sort_values(['updateDate']).groupby(['cityName', 'updateDate']):
        frm_list.append(frm.sort_values(['updateTime'])[-1:])    # take the lastest row within (city, date)
    out = pd.concat(frm_list).sort_values(['updateDate', 'provinceName', 'cityName'])
    to_names = [field for field in ['confirmed', 'suspected', 'cured', 'dead']]
    out = out.rename(columns=dict([('city_' + d + 'Count', d) for d in to_names])).drop(columns=['suspected'])   # the suspected column from csv is not reliable
    return clean(out)


def clean(df):
    '''
    On some dates, very little provinces have reports (usually happens when just pass mid-night)
    Remove these dates for now.  When I have time, I can fill in previous value
    '''
    province_count_frm = df.groupby('updateDate').agg({'provinceName': pd.Series.nunique})
    invalid_ind = province_count_frm[province_count_frm['provinceName'] < 25].index  # 
    return df[~df['updateDate'].isin(invalid_ind)]
    
    
def tsplot_conf_dead_cured(df, title_prefix, figsize=(13,6), fontsize=18, logy=False):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    plot_df = df.groupby('updateDate').agg('sum')
    plot_df.plot(y=['confirmed'], style='-*', grid=True, ax=ax1, figsize=figsize, logy=logy)
    ax2 = fig.add_subplot(212)
    plot_df.plot(y=['dead', 'cured'], style=':*', grid=True, ax=ax2, figsize=figsize, sharex=True, logy=logy)
    title = title_prefix + '确诊、死亡、治愈人数统计'
    if logy:
        title += '（指数）'
    fig.suptitle(title, fontproperties=font_prop, fontsize=fontsize)
    return fig