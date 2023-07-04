# -*- encoding: utf-8 -*-
"""
@File    :   convert_adf_to_tif.py   
@License :   (C)Copyright 2022-2022
 
@Modify Time      @Author      @Version
------------      -------      --------
2023/6/23 12:25   Du ShaoJie   2.0
---------------------------------------
@Description
------------
1. 将adf格式的栅格数据合并为tif格式
2. 将合并后的数据按照每一块1经度和1纬度的大小进行切割，并保存到本地
3. 切割后的文件的命名规则：
    NDVI_N{}_E{}.tif
    N{}表示纬度，E{}表示经度
    该经纬度为切割后的tif文件的左上角的经纬度



"""

import os
from osgeo import gdal
import numpy as np
import concurrent.futures


# 获取文件夹中所有以ndvi开头的文件夹
def get_ndvi_folder(path):
    """
    获取文件夹中所有以ndvi开头的文件夹
    :param path: 文件夹路径
    :return: 以ndvi开头的文件夹列表
    """
    # 获取文件夹中的所有文件夹
    for root, dirs, files in os.walk(path):
        # 以ndvi开头的文件夹列表
        ndvi_folder_list = []
        for folder in dirs:
            if folder.startswith('ndvi'):
                ndvi_folder_list.append(folder)
        return ndvi_folder_list


# 创建临时文件夹
def create_folder(save_path, folder_name):
    path = os.path.join(save_path, folder_name)
    if not os.path.exists(path):
        os.mkdir(path)
    return path


# 读取adf文件并将其转换为tif格式保存到临时文件夹中
def read_adfs(adf_paths, ndvi_folder):
    # 处理左边区域
    left_adf_path = os.path.join(adf_paths[0], ndvi_folder, 'w001001.adf')
    left_tif = gdal.Open(left_adf_path)

    # 处理中间区域
    middle_adf_path = os.path.join(adf_paths[1], ndvi_folder, 'w001001.adf')
    middle_tif = gdal.Open(middle_adf_path)

    # # 处理右边区域
    right_adf_path = os.path.join(adf_paths[2], ndvi_folder, 'w001001.adf')
    right_tif = gdal.Open(right_adf_path)
    return [left_tif, middle_tif, right_tif]


# 生成用于切割tif数据的标准范围
def create_standard_extent():
    # 指定经度范围
    longitude = [60, 150]
    # 指定纬度范围
    latitude = [5, 55]
    # 生成用于切割tif数据的标准范围
    standard_extent = [longitude[0], latitude[0], longitude[1], latitude[1]]
    return standard_extent


# 将vrt格式的栅格数据切割到标准范围
def resample_vrt_to_standard_extent(vrt, standard_extent):
    # 获取vrt的投影信息
    input_proj = vrt.GetProjection()

    # 设定options参数:以VAT格式保存在内存中，然后以无损压缩格式导出
    options = gdal.WarpOptions(srcSRS=input_proj, dstSRS=input_proj, format='VRT',
                               outputBounds=standard_extent, width=90090, height=50050,
                               resampleAlg=gdal.gdalconst.GRA_NearestNeighbour,
                               dstNodata=None, multithread=True)
    clipped_vrt = gdal.Warp('', vrt, options=options)
    return clipped_vrt


# 根据经纬度数据生成保存的文件名字
def create_file_name(i, j):
    lat_name = str(55 - i).zfill(2)
    lon_name = str(60 + j).zfill(3)
    out_name = "NDVI_N{}_E{}.tif".format(lat_name, lon_name)
    return out_name


# 写入数据到本地指定路径
def save_data_to_local(data, outputfile, geotransform, proj, offset_x, offset_y,
                       computed_xsize, computed_ysize):
    # 创建输出文件
    target_ds = gdal.GetDriverByName('GTiff').Create(outputfile, computed_xsize,
                                                     computed_ysize, 1, gdal.GDT_Int16,
                                                     options=["TILED=YES",
                                                              "COMPRESS=LZW"])
    # 设置地理参照和投影信息
    new_geotransform = list(geotransform)
    new_geotransform[0] = geotransform[0] + offset_x * geotransform[1]
    new_geotransform[3] = geotransform[3] + offset_y * geotransform[5]
    target_ds.SetGeoTransform(new_geotransform)
    target_ds.SetProjection(proj)
    target_ds.GetRasterBand(1).WriteArray(data)
    target_ds.FlushCache()
    del target_ds  # 关闭输出文件


def clip_vrt_to_one_degree(input_vrt, save_path):
    band = input_vrt.GetRasterBand(1)  # 获取波段信息
    xsize = band.XSize  # 获取影像的列数
    ysize = band.YSize  # 获取影像的行数
    # 获取影像的经纬度范围

    block_xsize = 1001  # 计算每个块的列数
    block_ysize = 1001  # 计算每个块的行数

    geotransform = input_vrt.GetGeoTransform()  # 获取地理参照信息
    proj = input_vrt.GetProjection()  # 获取投影信息
    # 创建一个线程池，指定最大线程数为12
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        # 遍历影像，分割出每一小块（行列数都为1001）进行保存
        for i in np.arange(49, -1, -1):
            for j in np.arange(0, 90, 1):
                # 根据经纬度数据生成保存的文件名字，名字中的经纬度为每个小块的左上角经纬度
                out_name = create_file_name(i, j)
                clipped_tif_save_path = os.path.join(save_path, out_name)
                # 如果文件已经存在，则跳过
                if not os.path.exists(clipped_tif_save_path):
                    # 计算每个小块的起始点和终止点
                    offset_x = j * block_xsize
                    offset_y = i * block_ysize
                    computed_xsize = min(block_xsize, xsize - offset_x)
                    computed_ysize = min(block_ysize, ysize - offset_y)
                    data = band.ReadAsArray(int(offset_x), int(offset_y), computed_xsize,
                                            computed_ysize)
                    executor.submit(save_data_to_local, data, clipped_tif_save_path,
                                    geotransform, proj, offset_x, offset_y,
                                    computed_xsize, computed_ysize)
        # 关闭原始影像文件
        input_vrt.FlushCache()
        del input_vrt


def write_txt(ndvi_folder_name):
    with open("processed_folder_list.txt", "a") as f:
        f.write(ndvi_folder_name + "\n")
    # 将已经处理好的文件夹的名称列表写入txt文件中
    print("已经处理完{}文件夹".format(ndvi_folder_name))


# 处理单个文件的函数
def covert_single_file(adf_paths, ndvi_folder_name, root_save_path):
    # 读取三个区域adf文件夹中的所有栅格数据
    tif_list = read_adfs(adf_paths, ndvi_folder_name)

    # 将三个区域的栅格数据进行镶嵌
    merged_vrt = gdal.BuildVRT('', tif_list)

    # 获取栅格数据的标准范围(纬度 = [5, 55],经度 = [60, 150])
    standard_extent = create_standard_extent()

    # 将镶嵌后的栅格数据进行重采样到标准范围
    resampled_vrt = resample_vrt_to_standard_extent(merged_vrt, standard_extent)

    # 新建一个文件夹用于保存当前处理的ndvi文件夹中的栅格数据
    save_path = create_folder(root_save_path, ndvi_folder_name)

    # 将重采样后的栅格数据进行裁剪，裁剪为长宽都为1度的栅格数据，并且保存到本地
    clip_vrt_to_one_degree(resampled_vrt, save_path)

    # 将已经处理好的文件夹的名称写入txt文件中，防止重复处理
    write_txt(ndvi_folder_name)

    del tif_list


# 获取已经处理好的文件夹的名称列表
def get_processed_folder_list():
    # 如果txt文件存在，则读取txt文件中的内容
    if os.path.exists("processed_folder_list.txt"):
        with open("processed_folder_list.txt", "r") as f:
            processed_folder_list = f.readlines()
            processed_folder_list = [i.strip() for i in processed_folder_list]
    else:
        processed_folder_list = []
    return processed_folder_list


# 获取需要处理的adf文件夹的名称
def get_adf_folders_for_process(adf_paths):
    # 获取adf左边区域中以ndvi开头的文件夹,返回存放所有adf文件夹列表
    all_ndvi_folders = get_ndvi_folder(adf_paths[0])
    # 获取已经处理好的文件夹的名称列表
    processed_ndvi_folders = get_processed_folder_list()
    # 设置一个列表存放需要处理的文件夹的名称
    ndvi_folders_for_process = [i for i in all_ndvi_folders if
                                i not in processed_ndvi_folders]
    return ndvi_folders_for_process


def convert_adf_to_tif(root_source_path, root_save_path):
    """
    将根目录下的所有adf格式的栅格数据转换为tif格式,并按照经纬度进行裁剪
    最后将裁剪后的栅格数据保存到本地指定根路径下
    :param root_source_path: adf文件夹的根目录
    :param root_save_path: 裁剪后的栅格数据保存的根目录
    :return:
    """
    # 如果数据要保存的文件夹不存在，则创建
    if not os.path.exists(root_save_path):
        os.mkdir(root_save_path)
    # 获取adf文件夹路径
    adf_paths = get_adf_folders_path(root_source_path)
    # 获取需要处理的adf文件夹名称,已经处理好的文件夹名称存放在processed_folder_list.txt中，后续就不再处理
    ndvi_folders_for_process = get_adf_folders_for_process(adf_paths)
    for ndvi_folder in ndvi_folders_for_process:
        covert_single_file(adf_paths, ndvi_folder, root_save_path)


def get_adf_folders_path(root_path):
    # adf文件左中右三个区域的数据路径
    left_path = os.path.join(root_path, 'PV_S5_TOC_NDVI1T')
    middle_path = os.path.join(root_path, 'PV_S5_TOC_NDVI2T')
    right_path = os.path.join(root_path, 'PV_S5_TOC_NDVI3T')
    adf_paths = [left_path, middle_path, right_path]
    return adf_paths


def get_args():
    root_source_path = input('请输入NDVI数据源存放的文件夹：\n')
    # 检查输入的文件夹是否存在
    while not os.path.exists(root_source_path):
        root_source_path = input('输入的文件夹不存在，请重新输入:\n')

    root_save_path = input(
        '请输入切割后的GeoTiff文件保存的文件夹，若文件夹不存在将自动创建：\n')

    return root_source_path, root_save_path


if __name__ == '__main__':
    root_source_path, root_save_path = get_args()
    convert_adf_to_tif(root_source_path, root_save_path)
