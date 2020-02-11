import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as mfm
import os
import numpy as np

_DXY_DATA_PATH_ = 'https://raw.githubusercontent.com/BlankerL/DXY-2019-nCoV-Data/master/csv/DXYArea.csv'
_CHN_FONT_ = None
_FONT_PROP_ = None
_CHN_EN_DICT_ = './locationDict.csv'

def set_font(font_file):
    if not os.path.exists(font_file):
        print(font_file + " not found.  If you wish to display Chinese characters in plots, please use set_font() to set the path to the font file.")
    else:
        global _CHN_FONT_, _FONT_PROP_
        _CHN_FONT_ = font_file
        _FONT_PROP_ = mfm.FontProperties(fname=_CHN_FONT_)
    return
        

set_font('C:/Windows/Fonts/STFANGSO.TTF')   # for displaying Chinese characters in plots


def use_chn():
    return _CHN_FONT_ is None


def load_chinese_data():
    ''' This includes some basic cleaning'''
    data = load_chinese_raw()
    return rename_cities(data)


def load_chinese_raw():
    '''
    This provides a way to lookinto the 'raw' data
    '''
    data = pd.read_csv(_DXY_DATA_PATH_)
    data['updateTime'] = pd.to_datetime(data['updateTime'])  # original type of updateTime after read_csv is 'str'
    data['updateDate'] = data['updateTime'].dt.date    # add date for daily aggregation
    # display basic info
    print('Last update: ', data['updateTime'].max())
    print('Data date range: ', data['updateDate'].min(), 'to', data['updateDate'].max())
    print('Number of rows in raw data: ', data.shape[0])
    return data   


def aggDaily(df, clean_dates=True):
    '''Aggregate the frequent time series data into a daily frame, ie, one entry per (date, province, city)'''
    frm_list = []
    drop_cols = ['province_' + field for field in ['confirmedCount', 'suspectedCount', 'curedCount', 'deadCount']]  # these can be computed later
    for key, frm in df.drop(columns=drop_cols).sort_values(['updateDate']).groupby(['provinceName', 'cityName', 'updateDate']):
        frm_list.append(frm.sort_values(['updateTime'])[-1:])    # take the latest row within (city, date)
    out = pd.concat(frm_list).sort_values(['updateDate', 'provinceName', 'cityName'])
    to_names = [field for field in ['confirmed', 'suspected', 'cured', 'dead']]
    out = out.rename(columns=dict([('city_' + d + 'Count', d) for d in to_names])).drop(columns=['suspected'])   # the suspected column from csv is not reliable
    if clean_dates:
        out = remove_abnormal_dates(out)
    return out


def remove_abnormal_dates(df):
    '''
    On some dates, very little provinces have reports (usually happens when just pass mid-night)
    Remove these dates for now.  When I have time, I can fill in previous value
    '''
    province_count_frm = df.groupby('updateDate').agg({'provinceName': pd.Series.nunique})
    invalid_dates = province_count_frm[province_count_frm['provinceName'] < 25].index  # 
    if len(invalid_dates) > 0:
        print("The following dates are removed due to insufficient provinces reported: ", invalid_dates.to_numpy())
    return df[~df['updateDate'].isin(invalid_dates)]


def rename_cities(snapshots):
    '''
    Sometimes, for example 2/3/2020, on some time snapshots, the CSV data contains cityName entries such as "南阳", "商丘", but at other time snapshots, it contains "南阳（含邓州）",  and "商丘（含永城）", etc.  They should be treated as the same city
    This results in the aggregation on province level gets too high.
    For now, entries will be ignored if cityName == xxx(xxx), and xxx already in the cityName set
    '''
    dup_frm = snapshots[snapshots['cityName'].str.contains('（')]
    rename_dict = {}
    if len(dup_frm) >= 0:
        rename_dict = dict([(name, name.split('（')[0]) for name in dup_frm['cityName']])
    
    rename_dict['吐鲁番市'] = '吐鲁番'   # raw data has both 吐鲁番市 and 吐鲁番, should be combined
    rename_dict['虹口'] = '虹口区'
    rename_dict['嘉定'] = '嘉定区'
    rename_dict['浦东'] = '浦东新区'
    rename_dict['黄浦'] = '黄浦区'
    rename_dict['浦东区'] = '浦东新区'
    rename_dict['丰台'] = '丰台区'
    rename_dict['宝山'] = '宝山区'
    rename_dict['徐汇'] = '徐汇区'
    rename_dict['门头沟'] = '门头沟区'
    rename_dict['闵行'] = '闵行区'
    rename_dict['东城'] = '东城区'
    rename_dict['通州'] = '通州区'
    rename_dict['鹤壁市'] = '鹤壁'
    rename_dict['漯河市'] = '漯河'
    rename_dict['陵水县'] = '陵水'
    rename_dict['平凉市'] = '平凉'
    rename_dict['城口县'] = '城口'
    rename_dict['白银市'] = '白银'
    rename_dict['垫江县'] = '垫江'
    rename_dict['天水市'] = '天水'
    rename_dict['丰都县'] = '丰都'
    rename_dict['琼中县'] = '琼中'
    rename_dict['乌海市'] = '乌海'
    rename_dict['吉林市'] = '吉林'
    rename_dict['临汾市'] = '临汾'
    
    rename_dict['第八师石河子市'] = '兵团第八师石河子市'
    rename_dict['第八师石河子'] = '兵团第八师石河子市'
    rename_dict['石河子'] = '兵团第八师石河子市'
    rename_dict['第八师'] = '兵团第八师石河子市'
    rename_dict['呼伦贝尔牙克石市'] = '呼伦贝尔牙克石'
    rename_dict['酉阳县'] = '酉阳'
    rename_dict['通辽市经济开发区'] = '通辽'
    rename_dict['第九师'] = '兵团第九师'
    rename_dict['西双版纳州'] = '西双版纳'
    rename_dict['澄迈县'] = '澄迈'
    rename_dict['奉节县'] = '奉节'
    rename_dict['石柱县'] = '石柱'
    
    rename_dict['待明确'] = '待明确地区'
    rename_dict['未明确地区'] = '待明确地区'
    rename_dict['未知'] = '待明确地区'
    rename_dict['未知地区'] = '待明确地区'
    
    snapshots['cityName'] = snapshots['cityName'].replace(rename_dict)  # write back
    return snapshots


def combine_daily(df):
    # the following should be "combined", rather than "replaced", but only impacts low count province.  Ignore for now
    rename_dict['包头市东河区'] = '包头'
    rename_dict['包头市昆都仑区'] = '包头'   
    rename_dict['锡林郭勒'] = '锡林郭勒盟'   #combine all these into one "city"
    rename_dict['锡林郭勒盟二连浩特'] = '锡林郭勒盟'
    rename_dict['锡林郭勒盟锡林浩特'] = '锡林郭勒盟'
    rename_dict['阿克苏'] = '阿克苏地区'
    rename_dict['鄂尔多斯东胜区'] = '鄂尔多斯'
    rename_dict['赤峰市松山区'] = '赤峰'
    rename_dict['赤峰市林西县'] = '赤峰'
    # do something when I have time
    return

    
def add_dailyNew(df):
    cols = ['confirmed', 'dead', 'cured']
    daily_new = df.groupby('cityName').agg(dict([(n, 'diff') for n in cols]))
    daily_new = daily_new.rename(columns=dict([(n, 'dailyNew_' + n) for n in cols]))
    df = pd.concat([df, daily_new], axis=1, join='outer')
    return df
    
    
def tsplot_conf_dead_cured(df, title_prefix='', figsize=(13,10), fontsize=18, logy=False, en=False):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    plot_df = df.groupby('updateDate').agg('sum')
    plot_df.plot(y=['confirmed'], style='-*', ax=ax1, grid=True, figsize=figsize, logy=logy, color='black', marker='o')
    ax1.set_ylabel("confirmed", color="black", fontsize=14)
    if 'dailyNew_confirmed' in df.columns:
        ax11 = ax1.twinx()
        ax11.bar(x=plot_df.index, height=plot_df['dailyNew_confirmed'], alpha=0.3, color='blue')
        ax11.set_ylabel('dailyNew_confirmed', color='blue', fontsize=14)
    ax2 = fig.add_subplot(212)
    plot_df.plot(y=['dead', 'cured'], style=':*', grid=True, ax=ax2, figsize=figsize, sharex=False, logy=logy)
    ax2.set_ylabel("count")
    if en:
        title = title_prefix + ' Count of confirmed, dead, and cured'
    else:
        title = title_prefix + '累计确诊、死亡、治愈人数'
    fig.suptitle(title, fontproperties=_FONT_PROP_, fontsize=fontsize)
    return fig


def tsplot_conf_dead_cured_en(df, title_prefix='', figsize=(13,10), fontsize=18, logy=False):
    return tsplot_conf_dead_cured(df, title_prefix=title_prefix, figsize=figsize, fontsize=fontsize, logy=logy, en=True)

    
def cross_sectional_bar(df, date_str, col, title='', groupby='provinceName', largestN=0, figsize=(13, 10), fontsize=15, en=False):
    date = pd.to_datetime(date_str)
    df_date = df[df['updateDate'] == date]
    group_frm = df_date.groupby(groupby).agg('sum').sort_values(by=col, ascending=True)
    if largestN > 0:
        group_frm = group_frm[-largestN:]  # only plot the first N bars
    ax = group_frm.plot.barh(y=col, grid=True, figsize=figsize)
    ax.set_yticklabels(group_frm.index, fontproperties=_FONT_PROP_) 
    ax.set_title(date_str + '  ' + title, fontproperties=_FONT_PROP_, fontsize=fontsize)
    ax.legend(loc='lower right')
    return ax
    
    
def cross_sectional_bar_en(df, date_str, col, title='', groupby='provinceName', largestN=0, figsize=(13, 10), fontsize=15):
    return cross_sectional_bar(df, date_str, col, title=title, groupby=groupby, largestN=largestN, figsize=figsize, fontsize=fontsize, en=True)
    
    
def add_en_location(df):
    '''Add provinceName_en, and cityName_en'''
    chn_en = pd.read_csv(_CHN_EN_DICT_, encoding='utf-8')
    translation = dict([t for t in zip(chn_en['Chinese'], chn_en['English'])])
    df['provinceName_en'] = df['provinceName'].replace(translation)
    df['cityName_en'] = df['cityName'].replace(translation)
    return df