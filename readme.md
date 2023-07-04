<a name="XbQTy"></a>
# 1. 总览
<a name="Fmi9u"></a>
## 1.1 作者信息
@ Author: Du Shaojie<br />@ Email: dusjmail@foxmail.com
<a name="Ehqsy"></a>
## 1.2 脚本功能：

1. 将adf格式的栅格数据合并，并转换为tif格式。
2. 将转换后的数据按照每一块1经度和1纬度的大小进行切割，保存到本地。
<a name="cwzWa"></a>
## 1.3 输出文件命名规则
切割后的文件的命名规则：<br />NDVI_N{}_E{}.tif<br />N{}表示纬度，E{}表示经度<br />该经纬度为切割后的tif文件的左上角的的像元的左上角的经纬度。
<a name="P6kZm"></a>
# 2. 环境配置
<a name="UBETj"></a>
## 2.1 安装python

1. 从官方下载[地址](https://www.python.org/downloads/)中下载python安装包，下载完毕后安装到本地计算机。
<a name="cFN96"></a>
## 2.2 下载code文件夹

1. 将github上的code文件夹下载到本地
<a name="HjYv2"></a>
## 2.3 安装扩展库

1. 打开系统终端，终端打开方式见[链接](https://www.xitongtang.com/class/qita/30216.html)，打开后将路径切换到code文件夹下的requirements.txt文件所在路径。

   假如requirements.txt文件所在的文件夹路径为：D:\programs\code<br />则在终端中输入一下语句：<br />cd D:\programs\code<br />然后点击回车，此时路径完成切换。

2. 切换路径后，继续在终端中输入如下命令行：

   pip install requirements.txt<br />等待片刻即可完成安装。安装完成后不要关闭终端。
<a name="Nzk1G"></a>
## 2.4 配置PROJ_LIB环境变量

1. 进入python的安装文件夹，依次按照以下路径寻找proj.db文件：

   你的python安装的文件路径\Lib\site-packages\pyproj\proj_dir\share\proj

2. 右键复制该文件的路径（比如D:\programs\python310\Lib\site-packages\pyproj\proj_dir\share\proj）
3. 将该路径添加到Windows的环境变量中，环境变量添加方法见[链接](https://blog.csdn.net/xue_nuo/article/details/114793534)
4. 在添加环境变量窗口填入环境变量名和对应的路径：

   环境变量名：PROJ_LIB<br />环境变量路径：你的python安装的文件路径\Lib\site-packages\pyproj\proj_dir\share\proj

<a name="cgSf4"></a>
# 3. 使用步骤

1. 在打开的终端中输入一下命令行：

   python covert_adf_to_tif.py  

2. 出现如下提示：

   请输入数据源根目录：<br />G:\月100M植被指数  （修改为自己的数据源文件夹路径）<br />请输入切割后的文件保存的根目录，若文件不存在将自动创建：<br />E:\NDVI（修改为自己的文件夹路径）
