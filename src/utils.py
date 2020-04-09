import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as mfm
import os
import numpy as np
import datetime


_DXY_DATA_FILE_ = 'https://raw.githubusercontent.com/BlankerL/DXY-2019-nCoV-Data/master/csv/DXYArea.csv'
_JHS_DATA_PATH_ = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/'
_JHS_DATA_START_DATE = '2020-01-22'
_JHS_DATA_START_DATE_NEW = '2020-03-22'  # start to publish new format, more details in location, etc
_CHN_FONT_ = None
_FONT_PROP_ = None
_CHN_EN_DICT_ = '../data/locationDict.csv'

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

    
def load_jhs_raw(verbose=False):
    dr = pd.date_range(_JHS_DATA_START_DATE, datetime.date.today())
    new_date = pd.to_datetime(_JHS_DATA_START_DATE_NEW)
    frm_list_old, frm_list_new = [], []
    for date in dr:
        if verbose:
            print("Reading: " + str(date))
        try:
            frm = pd.read_csv(_JHS_DATA_PATH_ + date.strftime('%m-%d-%Y') + '.csv')
        except:
            continue 

        if date == pd.to_datetime('2020-03-13'):  # somehow this date's CSV contains many data on 3/11
                frm = frm[pd.to_datetime(frm['Last Update']).dt.date == date]
        if date < new_date:
            frm_list_old.append(frm)
        else:
            frm_list_new.append(frm)
    
    frm_old = pd.concat(frm_list_old)
    frm_new = pd.concat(frm_list_new)
    
    # the new frame has more info and different names, convert the old to the new
    frm_old['FIPS'] = np.nan
    frm_old['Admin2'] = ''
    frm_old['Active'] = frm_old['Confirmed'] - frm_old['Deaths'] - frm_old['Recovered']  # a little processing here
    frm_old['Combined_Key'] = frm_old['Province/State'] + ',' + frm_old['Country/Region']
    frm_old = frm_old.rename(columns={"Province/State": "Province_State",
                                     "Country/Region": "Country_Region",
                                     "Last Update": "Last_Update",
                                     "Latitude": "Lat",
                                     "Longitude": "Long_"})
    out = pd.concat([frm_old, frm_new])        
    out['Last_Update'] = pd.to_datetime(out['Last_Update'])
    out['Update_Date'] = out['Last_Update'].dt.date   
    return out

#    out = pd.concat(frm_list, sort=False).drop_duplicates()
#    rename_dict = {'Province/State': 'province/state', 
#                  'Country/Region': 'country/region',
#                  'Confirmed': 'cum_confirmed',
#                   'Deaths': 'cum_dead',
#                   'Recovered': 'cum_cured'  # this is a bit inaccurate
#                  }
#    out = out.rename(columns=rename_dict)
#    out['update_time'] = pd.to_datetime(out['Last Update'])
#    out['update_date'] = out['update_time'].dt.date
#    province = out['province/state']
#    out['province/state'] = out['province/state'].fillna('') # replace NaN province with empty string
#    out['country/region'] = out['country/region'].replace('Others', 'Diamond Princess')
#    out = out.sort_values(['update_date', 'country/region', 'province/state'])
#    out = out.reset_index().drop(columns='index')
#    return out
        

#def jhs_daily(jhs_raw):
#frm_list = []
#location_cols = ['Country_Region', 'Province_State', 'Admin2']
#for key, frm in jhs_raw.groupby(['Update_Date'] + location_cols):
#frm_list.append(frm.sort_values(['Last_Update'])[-1:])    # take the latest row within (city, date)
#out = pd.concat(frm_list).sort_values(['Update_Date'] + location_cols)
#out = add_daily_new(out, group_keys=location_col)
#return out

    
def load_chinese_data():
    ''' This includes some basic cleaning'''
    data = load_chinese_raw()
    return rename_cities(data)


def load_chinese_raw():
    '''
    This provides a way to lookinto the 'raw' data
    '''
    raw = pd.read_csv(_DXY_DATA_FILE_)
    
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
    drop_cols += ['provinceEnglishName', 'cityEnglishName', 'province_zipCode']
    for key, frm in df.drop(columns=drop_cols).sort_values(['update_date']).groupby(['province_name', 'city_name', 'update_date']):
        frm_list.append(frm.sort_values(['update_time'])[-1:])    # take the latest row within (city, date)
    out = pd.concat(frm_list).sort_values(['update_date', 'province_name', 'city_name'])
    to_names = [field for field in ['confirmed', 'suspected', 'cured', 'dead']]
    out = out.rename(columns=dict([('city_' + d, 'cum_' + d) for d in to_names]))
    out = out.rename(columns={'city_zipCode': 'zip_code'})
    out = out.drop(columns=['cum_suspected'])   # the suspected column from csv is not reliable, may keep this when the upstream problem is solved

    #out = remove_abnormal_dates(out)
    out = add_daily_new(out)  # add daily new cases
    out = add_en_location(out)
    #out = out.set_index(['update_date'])
    
    # rearrange columns
    new_col_order = ['update_date', 'province_name', 'province_name_en', 'city_name', 'city_name_en', 'zip_code', 'cum_confirmed', 'cum_cured', 'cum_dead', 'new_confirmed', 'new_cured', 'new_dead', 'update_time']
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
    rename_dict['大兴'] = '大兴区'
    rename_dict['怀柔'] = '怀柔区'
    rename_dict['昌平'] = '昌平区'
    rename_dict['朝阳'] = '朝阳区'
    rename_dict['海淀'] = '海淀区'
    rename_dict['石景山'] = '石景山区'
    rename_dict['西城'] = '西城区'
    rename_dict['顺义'] = '顺义区'
    rename_dict['武汉来京人员'] = '外地来京人员'
    rename_dict['不明地区'] = '待明确地区'
    
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



def diff0(x):
    '''similar to numpy.diff, but assumes the first element to be zero, so outputs the same length
    '''
    return np.diff(np.hstack([0, x]))


def add_daily_new(df, group_keys=['province_name', 'city_name'], diff_cols=['cum_confirmed', 'cum_dead', 'cum_cured'], date_col='update_date'):
    '''
    >>> df = pd.DataFrame({'update_date': [1, 2, 2, 3, 3], 
    ...     'city_name': ['A', 'A', 'B', 'A', 'B'], 
    ...     'cum_confirmed': [1, 2, 1, 4, 5],
    ...     'cum_dead': [0, 0, 0, 1, 1],
    ...     'cum_cured': [0, 0, 0, 0, 1]})
    >>> result = add_daily_new(df, group_keys=['city_name'])
    >>> print(result)
       update_date city_name  cum_confirmed  cum_dead  cum_cured  new_confirmed  new_dead  new_cured
    0            1         A              1         0          0            NaN       NaN        NaN
    1            2         A              2         0          0            1.0       0.0        0.0
    2            2         B              1         0          0            1.0       0.0        0.0
    3            3         A              4         1          0            2.0       1.0        0.0
    4            3         B              5         1          1            4.0       1.0        1.0
    '''
    cols = ['confirmed', 'dead', 'cured']
    # Do NOT use the Pandas 'diff'.  Because it will result in the first element being NA. 
    # So if a city appears in a later date, its first "new_" will be NA (wrong), instead of the first  element (correct)
    daily_new = df.groupby(group_keys)[diff_cols].transform(diff0)
    
    new_cols = []
    for col in diff_cols:
        if 'cum_' in col:
            new_cols.append(col.replace('cum', 'new'))
        else:
            new_cols.append('new_' + col)
         
    daily_new = daily_new.rename(columns=dict(zip(diff_cols, new_cols)))
    df = pd.concat([df, daily_new], axis=1, join='outer')
 
    # However, on the first "data date", the "new_" should be NA, because the previous date data is unknown
    first_data_date = df[date_col].min()
    df[new_cols] = df[new_cols].where(df[date_col] != first_data_date, np.nan)
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
    if date_str is not None:
        df_date = df[df['update_date'] == date]
    else:
        df_date = df
        
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
        

def add_moving_average(df, group_col, win_size):
    ma = df.reset_index(group_col).groupby(group_col)['new_confirmed', 'new_dead'].rolling(win_size, min_period=1).mean()
    df['new_confirmed_MA'] = ma['new_confirmed']
    df['new_dead_MA'] = ma['new_dead']
    return df
    

def get_Json_obj():
    import json
    import urllib.request
    
    url = "https://coronavirus-tracker-api.herokuapp.com/all"
    data = urllib.request.urlopen(url).read().decode()
    # parse json object
    obj = json.loads(data)
    return obj


def stack_frames_by_date(df, date_col, cat_col, val_col='positive_rate'):
    df = df.sort_values(by=date_col, ascending=True)
    dates = df[date_col].unique()
    frm = None
    for date in dates:
        x = df[df[date_col] == date][[cat_col, val_col]]
        subfrm = x.set_index(cat_col).rename(columns=dict([(val_col, str(date))]))
        if frm is None:
            frm = subfrm
        else:
            frm =pd.concat([frm, subfrm], axis=1)
    return frm
            

def IL_death_demographic_early():
    '''On or before 2020-03-27, IDPH release death demographics in a more random format, so manual input here'''
    dates, counties, counts, sexes, ages, references = [], [], [], [], [], []

    dates.append(pd.to_datetime('2020-03-17'))
    counties.append('Cook')
    counts.append(1)
    sexes.append('female')
    ages.append(60)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-first-illinois-coronavirus-disease-death')

    dates.append(pd.to_datetime('2020-03-19'))
    counties.append('Will')
    counts.append(1)
    sexes.append('male')
    ages.append(40)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-deaths-three-more-individuals-illinois-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-19'))
    counties.append('Cook')
    counts.append(1)
    sexes.append('female')
    ages.append(80)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-deaths-three-more-individuals-illinois-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-19'))
    counties.append('Sangamon')
    counts.append(1)
    sexes.append('female')
    ages.append(70)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-deaths-three-more-individuals-illinois-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-20'))
    counties.append('Cook')
    counts.append(1)
    sexes.append('female')
    ages.append(70)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-163-new-cases-coronavirus-disease')
    
    dates.append(pd.to_datetime('2020-03-21'))
    counties.append('Cook')
    counts.append(1)
    sexes.append('male')
    ages.append(70)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-168-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-22'))
    counties.append('Cook')
    counts.append(2)   # 1 cook county, 1 Chicago
    sexes.append('male')
    ages.append(80)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-296-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-22'))
    counties.append('McLean')
    counts.append(1)   # 1 cook county, 1 Chicago
    sexes.append('female')
    ages.append(70)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-296-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-23'))
    counties.append('Cook')
    counts.append(2)   
    sexes.append('male')
    ages.append(80)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-236-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-23'))
    counties.append('Cook')
    counts.append(1)   
    sexes.append('male')
    ages.append(90)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-236-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-24'))
    counties.append('Cook')  # chicago
    counts.append(1)   
    sexes.append('male')
    ages.append(50)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-250-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-24'))
    counties.append('Cook')  
    counts.append(2)   
    sexes.append('unknown')  # the news only says "two Cook County residents both in their 60s", did not specify sex
    ages.append(60)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-250-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-24'))
    counties.append('DuPage')  
    counts.append(1)   
    sexes.append('female')
    ages.append(90)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-250-new-cases-coronavirus-disease')
    
    dates.append(pd.to_datetime('2020-03-25'))
    counties.append('Kane')  
    counts.append(1)   
    sexes.append('male')
    ages.append(90)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-330-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-25'))
    counties.append('Cook')  
    counts.append(1)   
    sexes.append('male')
    ages.append(60)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-330-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-25'))
    counties.append('Will')  
    counts.append(1)   
    sexes.append('female')
    ages.append(50)
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-330-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-26'))
    counties.append('unknown')  
    counts.append(1)   
    sexes.append('male')
    ages.append(50)
    references.append('http://dph.illinois.gov/news/public-health-officials-announce-673-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-26'))
    counties.append('unknown')  
    counts.append(2)   
    sexes.append('male')
    ages.append(60)
    references.append('http://dph.illinois.gov/news/public-health-officials-announce-673-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-26'))
    counties.append('unknown')  
    counts.append(2)   
    sexes.append('female')
    ages.append(60)
    references.append('http://dph.illinois.gov/news/public-health-officials-announce-673-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-26'))
    counties.append('unknown')  
    counts.append(1)   
    sexes.append('male')
    ages.append(70)
    references.append('http://dph.illinois.gov/news/public-health-officials-announce-673-new-cases-coronavirus-disease')

    dates.append(pd.to_datetime('2020-03-26'))
    counties.append('unknown')  
    counts.append(1)   
    sexes.append('female')
    ages.append(90)
    references.append('http://dph.illinois.gov/news/public-health-officials-announce-673-new-cases-coronavirus-disease')
    
    dates.append(pd.to_datetime('2020-03-27'))
    counties.append('unknown')  
    counts.append(8)   
    sexes.append('unknown')
    ages.append('unknown')
    references.append('http://www.dph.illinois.gov/news/public-health-officials-announce-488-new-cases-coronavirus-disease')
    
    out = pd.DataFrame(data={'Date' : dates, 'County': counties, 'Count': counts, 'Sex': sexes, 'Age_bracket': ages, 'Reference': references})
    return out
    
    
def parse_IL_death_demographic(date_range):
    import requests
    from bs4 import BeautifulSoup
    IDPH_BASE = 'http://www.dph.illinois.gov'
    IDPH_NEWS_LINK_BASE = IDPH_BASE + '/news/2020'
    
    early_demographic = IL_death_demographic_early()
    early_demographic = early_demographic[early_demographic['Date'].between(date_range[0], date_range[-1], inclusive=True)]
    
    START_DEATH_DEMOGRAPHIC_DATE = pd.to_datetime('2020-03-28')
    
    headers = requests.utils.default_headers()
    headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

    months = np.unique([d.month for d in date_range])
    months = np.sort(months)[::-1]  # descending
    dates, counties, counts, sexes, ages, references = [], [], [], [], [], []
    for month in months:
        req = requests.get(IDPH_NEWS_LINK_BASE + str(month).zfill(2), headers)
        soup = BeautifulSoup(req.content, 'html.parser')
        for elm in soup.find_all('div', {'class', 'views-field views-field-created'}):
            date_str = elm.span.get_text()
            date = pd.to_datetime(date_str)
            if date not in date_range:
                continue
            elif date < START_DEATH_DEMOGRAPHIC_DATE:
                continue
            detail_link = IDPH_BASE + elm.parent.find('span', {'class': 'field-content'}).a.get('href')  # use the "read-more >>" link, otherwise the main page may be incomplete
            detail_req = requests.get(detail_link, headers)
            detail_soup = BeautifulSoup(detail_req.content, 'html.parser')
            news = detail_soup.find('div', {'class': 'field-item even'})
            for ll in news.ul.find_all('li'):
                part1, part2 = ll.text.split(':')
                county = part1.split(' County')[0]
                entries = part2.split(',')
                for entry in entries:
                    if entry == '':
                        continue
                    sl = entry.split(' ')
                    sl = [s for s in sl if s != '']
                    if len(sl) == 2:
                        if sl[0].isnumeric():
                            sl.append('unknown')
                        else:
                            sl = ['1'] + sl
                    if sl[0].isnumeric():
                        count = int(sl[0])
                    else:
                        count = 1
                    
                    if sl[0] == 'infant' and len(sl) == 1:
                        sex = 'unknown'
                        age = 0
                    else:
                        sex = sl[1]
                        if sex[-1] == 's':  # 'males' or 'females', get rid off the plural
                            sex = sex[:-1]
                        if len(sl) > 2:  # when sex == 'incomplete', it doesn't have the next entry
                            if sl[2] == 'unknown':
                                age = 'unknown'                            
                            elif sl[2][-1].isnumeric():
                                age = int(sl[2])
                            elif sl[2][-2].isnumeric():
                                age = int(sl[2][:-1])
                            else:
                                age = int(sl[2][:-2])   # sometimes ends as 's.', or '\'s'
                        else:
                            age = np.nan
                    dates.append(date)
                    counties.append(county)
                    counts.append(count)
                    sexes.append(sex)
                    ages.append(age)
                    references.append(detail_link)
                    if len(sl) >= 5 and sl[4] == 'incomplete':  # append incomplete entry, something like "(5 incomplete data)""
                        dates.append(date)
                        counties.append(county)
                        counts.append(int(sl[3].split('(')[1]))
                        sexes.append('unknown')
                        ages.append('unknown')
                        references.append(detail_link)                        
                        
    out = pd.DataFrame(data={'Date' : dates, 'County': counties, 'Count': counts, 'Sex': sexes, 'Age_bracket': ages, 'Reference': references})
    out = pd.concat([out, early_demographic]).sort_values(by='Date')
    return out
    
    
def parse_IL_county_current_data():
    link = 'https://coronavirus.illinois.gov/s/county-map'
    headers = requests.utils.default_headers()
    headers.update({ 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'})

    
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()