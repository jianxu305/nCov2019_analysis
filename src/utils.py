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
        

set_font('./STFANGSO.TTF')   # for displaying Chinese characters in plots


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
    raw = pd.read_csv(_DXY_DATA_PATH_)
    
    # the original CSV column names are in camel case, change to lower_case convention
    rename_dict = {'updateTime': 'update_time',
                   'provinceName': 'province_name',
                   'cityName': 'city_name',
                   'province_confirmedCount': 'province_confirmed',
                   'province_suspectedCount': 'province_suspected',
                   'province_deadCount': 'province_dead',
                   'province_curedCount': 'province_cured',
                   'city_confirmedCount': 'city_confirmed',
                   'city_suspectedCount': 'city_suspected',
                   'city_deadCount': 'city_dead',
                   'city_curedCount': 'city_cured'
                  }
    data = raw.rename(columns=rename_dict)
    data['update_time'] = pd.to_datetime(data['update_time'])  # original type of update_time after read_csv is 'str'
    data['update_date'] = data['update_time'].dt.date    # add date for daily aggregation, if without to_datetime, it would be a dateInt object, difficult to use
    # display basic info
    print('Last update: ', data['update_time'].max())
    print('Data date range: ', data['update_date'].min(), 'to', data['update_date'].max())
    print('Number of rows in raw data: ', data.shape[0])
    return data   


def aggDaily(df):
    '''Aggregate the frequent time series data into a daily frame, ie, one entry per (date, province, city)'''
    frm_list = []
    drop_cols = ['province_' + field for field in ['confirmed', 'suspected', 'cured', 'dead']]  # these can be computed later
    for key, frm in df.drop(columns=drop_cols).sort_values(['update_date']).groupby(['province_name', 'city_name', 'update_date']):
        frm_list.append(frm.sort_values(['update_time'])[-1:])    # take the latest row within (city, date)
    out = pd.concat(frm_list).sort_values(['update_date', 'province_name', 'city_name'])
    to_names = [field for field in ['confirmed', 'suspected', 'cured', 'dead']]
    out = out.rename(columns=dict([('city_' + d, 'cum_' + d) for d in to_names]))
    out = out.drop(columns=['cum_suspected'])   # the suspected column from csv is not reliable, may keep this when the upstream problem is solved

    #out = remove_abnormal_dates(out)
    out = add_daily_new(out)  # add daily new cases
    out = add_en_location(out)
    #out = out.set_index(['update_date'])
    
    # rearrange columns
    new_col_order = ['update_date', 'province_name', 'province_name_en', 'city_name', 'city_name_en', 'cum_confirmed', 'cum_cured', 'cum_dead', 'new_confirmed', 'new_cured', 'new_dead', 'update_time']
    if len(new_col_order) != len(out.columns):
        raise ValueError("Some columns are dropped: ", set(out.columns).difference(new_col_order))
    out = out[new_col_order]
    return out


def remove_abnormal_dates(df):
    '''
    On some dates, very little provinces have reports (usually happens when just pass mid-night)
    Remove these dates for now.  When I have time, I can fill in previous value
    '''
    if len(df['update_date']) < 2:
        return
    second_last_date, last_date = df['update_date'].iloc[-2:]
    city_count = df.groupby('update_date').agg({'city_name': pd.Series.nunique})
    second_last_count, last_count = city_count['city_name'].iloc[-2:]
    if last_count < second_last_count * .95:   # 95% to give some margin
        print("The last date " + str(last_date) + " is removed due to insufficient cities reporting")
        return df[~df['update_date'] == last_date]
    else:
        return df


def rename_cities(snapshots):
    '''
    Sometimes, for example 2/3/2020, on some time snapshots, the CSV data contains city_name entries such as "南阳", "商丘", but at other time snapshots, it contains "南阳（含邓州）",  and "商丘（含永城）", etc.  They should be treated as the same city
    This results in the aggregation on province level gets too high.
    For now, entries will be ignored if city_name == xxx(xxx), and xxx already in the city_name set
    '''
    dup_frm = snapshots[snapshots['city_name'].str.contains('（')]
    rename_dict = {}
    if len(dup_frm) >= 0:
        rename_dict = dict([(name, name.split('（')[0]) for name in dup_frm['city_name']])
    
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
    
    snapshots['city_name'] = snapshots['city_name'].replace(rename_dict)  # write back
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

    
def add_daily_new(df):
    cols = ['confirmed', 'dead', 'cured']
    daily_new = df.groupby(['province_name', 'city_name']).agg(dict([(n, 'diff') for n in ['cum_' + c for c in cols]]))
    daily_new = daily_new.rename(columns=dict([('cum_' + n, 'new_' + n) for n in cols]))
    df = pd.concat([df, daily_new], axis=1, join='outer')
    return df
    
    
def tsplot_conf_dead_cured(df, figsize=(13,10), fontsize=18, logy=False, title=None):
    fig = plt.figure()
    ax1 = fig.add_subplot(211)
    plot_df = df.groupby('update_date').agg('sum')
    plot_df.plot(y=['cum_confirmed'], style='-*', ax=ax1, grid=True, figsize=figsize, logy=logy, color='black', marker='o')
    ax1.set_ylabel("confirmed", color="black", fontsize=14)

    ax11 = ax1.twinx()
    ax11.bar(x=plot_df.index, height=plot_df['new_confirmed'], color='blue', alpha=0.3)
    ax11.set_ylabel('new_confirmed', color='blue', fontsize=14)
    
    ax2 = fig.add_subplot(212)
    plot_df.plot(y=['cum_dead', 'cum_cured'], style='-o', grid=True, ax=ax2, figsize=figsize, sharex=False, logy=logy)
    ax2.set_ylabel("count")
    
    if title is not None:
        fig.suptitle(title, fontproperties=_FONT_PROP_, fontsize=fontsize)
        
    return fig

    
def cross_sectional_bar(df, date_str, col, groupby='province_name', largestN=0, figsize=(13, 10), fontsize=15, title=None):
    date = pd.to_datetime(date_str)
    df_date = df[df['update_date'] == date]
    group_frm = df_date.groupby(groupby).agg('sum').sort_values(by=col, ascending=True)
    if largestN > 0:
        group_frm = group_frm[-largestN:]  # only plot the first N bars
    fig, ax = plt.subplots()
    group_frm.plot.barh(y=col, grid=True, ax=ax, figsize=figsize)
    ax.set_yticklabels(group_frm.index, fontproperties=_FONT_PROP_, fontsize=fontsize) 
    ax.legend(loc='lower right')
    if title is not None:
        ax.set_title(title, fontproperties=_FONT_PROP_, fontsize=fontsize)  # because there is only one axes, so setting title on ax level, rather than the "suptitle" in figure level looks better
    return fig
    
    
def add_en_location(df):
    '''Add province_name_en, and city_name_en'''
    chn_en = pd.read_csv(_CHN_EN_DICT_, encoding='utf-8')
    translation = dict([t for t in zip(chn_en['Chinese'], chn_en['English'])])
    df['province_name_en'] = df['province_name'].replace(translation)
    df['city_name_en'] = df['city_name'].replace(translation)
    return df