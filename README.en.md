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
data = utils.load_chinese_data()  # 提取 CSV 实时数据
daily_frm = utils.aggDaily(data)  # 整合成每日数据
```

** Best Wishes **
