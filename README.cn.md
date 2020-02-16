# 2019-nCov 新型冠状病毒 Python 数据分析
## 简体中文 | [English](README.md)


### 使用前提

* Pandas
* 如果想要交互使用，又不能使用 Google Colab 的话，要先安装 Python Notebook。


### 文件说明
* [coronavirus_demo_colab.ipynb](./src/coronavirus_demo_colab.ipynb): Google Colab 上的演示如何提取、整合数据，以及基本时序、横向分析作图
* [demo.ipynb](./src/demo.ipynb): 传统 Python Notebook 上演示如何提取、整合数据，以及基本时序、横向分析作图
* [demo.en.ipynb](./src/demo.ipynb): demo.ipynb 的英文版
* demo.html 和 demo.pdf: 对于没有安装 Python Notebook 的用户，可以用这些文档作为用户手册
* death_rate.ipynb: 对新型冠状病毒死亡率的分析
* utils.py: 基本使用函数

例如

```
data = utils.load_chinese_data()  # 提取 CSV 实时数据
daily_frm = utils.aggDaily(data)  # 整合成每日数据
utils.tsplot_conf_dead_cured(daily_frm)  # 画全国确诊、死亡、治愈时间序列图
```


### 数据来源
* 原始数据来源为[丁香园](https://3g.dxy.cn/newh5/view/pneumonia)。 
* CSV 格式数据文件来源: https://github.com/BlankerL/DXY-2019-nCoV-Data CSV 数据文件由网络爬虫获得，每隔一段时间自动更新一次。


### 祝一切安好 
