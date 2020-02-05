# 2019-nCov noval coronavirus Data analysis in Python
[简体中文](README.md) | English

* Original Data from [Ding Xiang Yuan](https://3g.dxy.cn/newh5/view/pneumonia)。 
* CSV format data from: https://github.com/BlankerL/DXY-2019-nCoV-Data CSV data file is updated frequently by [2019-nCoV Infection Data Realtime Crawler](https://github.com/BlankerL/DXY-2019-nCoV-Crawler).

### Prerequisite

* Pandas
* If you need interactive analysis, you need to install Python Notebook first.  Otherwise it's not needed.


### Description
* demo.ipynb: Demostrating how to extract / aggregate / slice data, and basic time series / cross-sectional plotting 
* demo.html, demo.pdf: For those who doon't have Python Notebook, these two files serve as demo.ipynb for demonstration purpose
* death_rate.ipynb: An example analysis of the heterogeneity of death rate across different regions
* utils.py: Utility functions

Some Examples:

```
data = utils.load_chinese_data()  # obtain CSV real time data
daily_frm = utils.aggDaily(data)  # aggregate to daily data
utils.tsplot_conf_dead_cured(daily_frm, title_prefix='Whole Country')  # Time Series plot of the Confirmed, dead, cured count of the whole country
```

** Best Wishes **
