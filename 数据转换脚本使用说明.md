<a name="XbQTy"></a>
# 总览
<a name="Fmi9u"></a>
## 作者信息
@ Author: Du Shaojie<br />@ Email: dusjmail@foxmail.com
<a name="Ehqsy"></a>
## 说明：

1. 将adf格式的栅格数据合并，并转换为tif格式
2. 将合并后的数据按照每一块1经度和1纬度的大小进行切割，保存到本地
3. 切割后的文件的命名规则：<br />NDVI_N{}_E{}.tif<br />N{}表示纬度，E{}表示经度<br />该经纬度为切割后的tif文件的左上角的经纬度
<a name="P6kZm"></a>
# 需要安装的包：
以下扩展库基于python3.11版本
<a name="WdlM5"></a>
## GDAL
地理数据处理库gdal<br />版本：gdal=3.6.2<br />安装方法：<br />conda 安装：conda install gdal=3.6.2<br />pip安装：pip install gdal=3.6.2
<a name="AZnBn"></a>
## Numpy
数值计算库numpy<br />版本：numpy=1.24.3<br />安装方法：<br />conda 安装：conda install numpy=1.24.3<br />pip安装：pip install numpy=1.24.3
<a name="p4WL8"></a>
## PyProj
地理数据投影库pyproj<br />版本：pyproj=3.5.0<br />安装方法：<br />conda 安装：conda install pyproj=3.5.0<br />pip安装：pip install pyproj=3.5.0<br />安装完毕后需要将代码文件中第30行按照如下方式更改：<br />envs_path=r'自己的python环境路径'
<a name="XPaIh"></a>
# 使用步骤

1. 下载covert_adf_to_tif.py文件
2. 基于pycharm或者其他代码编辑器打开该文件
3. 按照第2节中的要求安装软件包并修改第30行路径
4. 在函数中设置自己的数据源根目录和保存根目录
5. 点击运行即可


