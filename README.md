# 2019-nCov coronavirus Data Analysis in Python (新型冠状病毒数据分析）
本项目为2019新型冠状病毒（2019-nCoV）疫情状况的 Python 分析工具。
* 原始数据来源为[丁香园](https://3g.dxy.cn/newh5/view/pneumonia)。 
* CSV 格式数据文件来源: https://github.com/BlankerL/DXY-2019-nCoV-Data CSV 数据文件由网络爬虫获得，每隔一段时间自动更新一次。

### 使用前提

* Pandas
* 如果想要交互使用的话，要先安装 Python Notebook，否则不需要。


### 文件说明
* demo.ipynb 演示如何提取、整合数据，以及基本画图操作
* demo.html 和 demo.pdf 对于没有安装 Python Notebook 的用户，可以用这些文档作为用户手册
* death_rate.ipynb 对武汉、湖北（除武汉）、全国（除湖北）的地区特异性分析
* utils.py 基本使用函数

例如

```
data = utils.load_chinese_data()  # 提取 CSV 实时数据
daily_frm = utils.aggDaily(data)  # 整合成每日数据
```

### 祝一切安好
