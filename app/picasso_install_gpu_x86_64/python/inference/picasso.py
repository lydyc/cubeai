#!/usr/bin/env python
# coding: utf-8
"""
 * Copyright (c) 2019 ZNV.Co.Ltd
 * All rights reserved.
 *
 * @file: licence_server.py
 * @brief: 
 * @version 1.0
 * @date 2019/11/25
"""

from ctypes import *
from .common import _LIB, ServerHandle, logger, parse_argument, covert_image2ctype, TaskType
from collections import namedtuple
import os
import json
import configparser
import subprocess

server_handle_dict = {}

def get_sdk_version():
    """[调用 picasso.so 的 mvGetSDKVersion 函数获取版本号]

    Returns:
        [str]: [picasso sdk 版本字符串]
    """
    get_version = _LIB.mvGetSDKVersion
    get_version.restype = c_char_p
    sdk_version = get_version()
    return str(sdk_version, encoding='utf-8')

def generate_licence():
    """[调用 picasso.so 的 mvGenerateLicence 函数生成密钥/授权码]

    Returns:
        [json or str]: [json失败消息 or 密钥]
    """
    machine_code = c_char_p()
    licence_generator = _LIB.mvGenerateLicence
    licence_generator.restype = c_int
    status = licence_generator(byref(machine_code))
    if status != 0:
        res = {"result": "failed",
               "code": 400,
               "error_message": "GENERATE_LICENCE_ERROR"}
        return json.loads(res)
    res = str(machine_code.value, encoding='utf-8')
    licence_release = _LIB.mvDestroyLicence
    licence_release.restype = c_int
    status = licence_release(machine_code)
    return res


def check_licence(licence_serial):
    """[调用 picasso.so 的 mvCheckLicence 函数校验密钥]

    Args:
        licence_serial ([str]): [base64 编码的密钥串]
    Returns:
        [json or str]: [json失败消息 or 校验结果]
    """
    result = c_char_p()
    licence_checker = _LIB.mvCheckLicence
    licence_checker.restype = c_int
    status = licence_checker(c_char_p(licence_serial.encode('utf-8')), byref(result))
    if status != 0:
        res = {"result": "failed",
               "code": 400,
               "error_message": "SDK_SERVER_ERROR"}
        return json.loads(res)
    res = str(result.value, encoding="utf-8")
    licence_release = _LIB.mvDestroyLicence
    licence_release.restype = c_int
    status = licence_release(result)
    return res


def register_server_list(server_str):
    """[调用 picasso.so 的 mvRegisterServerList 函数获取 SDK 实现的服务列表]

    Args:
        server_str ([str]): [; 分割的服务列表]

    Returns:
        [str]: [服务信息字符串, 版本等信息], e.g. 
        sem_seg_server:sem_seg_server,v2.0.1;coarse_grid_server:coarse_grid_server,v0.1.0;street_violate_server:street_violate_server,v0.2.0
    """
    result = c_char_p()
    server_list_register = _LIB.mvRegisterServerList
    server_list_register.restype = c_int
    status = server_list_register(c_char_p(server_str.encode('utf-8')), byref(result))
    if status <= 0:
        res = "SDK_REGISTER_ERROR"
        return res
    res = str(result.value, encoding="utf-8")
    return res

def init_picasso():
    # #读文件，获取ntp参数,根据开关参数判断是否需要进行NTP时钟同步
    conf = configparser.ConfigParser()
    configfile = "./python/inference/ntp_conf.ini"
    conf.read(configfile)
    if conf.has_section("ntp_switch"):
        switch = int(eval(conf["ntp_switch"]["switch"]))
        if switch == 1:
            curr_dir = os.path.dirname(os.path.abspath(__file__))
            target_script_path = os.path.join(curr_dir,"set_ntp.py")
            child_process = subprocess.Popen(["python",target_script_path])

    """[初始化 picasso SDK, 主动加载配置的模型与服务]
    """
    picasso_init = _LIB.mvPicassoInit
    picasso_init.restype = c_int
    status = picasso_init()
    if status != 0:
        logger.error("Picasso Init Error in Python!")

    # #picasso初始化之后，创建子进程进行NTP时钟同步
    # curr_dir = os.path.dirname(os.path.abspath(__file__))
    # target_script_path = os.path.join(curr_dir,"set_ntp.py")
    # child_process = subprocess.Popen(["python",target_script_path])


def serverCreated(server_id):
    """[检查指定的服务是否已经创建]

    Args:
        server_id ([str]): [服务唯一标识符]
    """
    server_exist = _LIB.mvServerExist
    server_exist.restype = c_int
    status = server_exist(c_char_p(server_id.encode('utf-8')))
    return status == 0

def create_image_server_handle(server_id, licence, model_file, concurrencies, engine_type):
    """[创建/获取静态图片服务句柄]

    Args:
        server_id ([str]): [服务名称]
        licence ([str]): [授权码]
        model_file ([str]): [模型文件，用于覆盖默认模型文件]
        concurrencies ([str]): [引擎的并发]]
        engine_type ([str]): [引擎类型]

    Returns:
        [type]: [description]
    """
    server_handle = POINTER(ServerHandle)()

    if serverCreated(server_id):
        # 已存在返回 None 或者 通过 Get 获取
        logger.info("{} exist".format(server_id))
        return None
    else:
        handle_creator = _LIB.mvCreateServerHandle
        handle_creator.restype = c_int
        status = handle_creator(byref(server_handle), c_char_p(server_id.encode('utf-8')),
                                c_char_p(licence.encode('utf-8')), c_char_p(model_file.encode('utf-8')),
                                c_char_p(concurrencies.encode('utf-8')), c_char_p(engine_type.encode('utf-8')))
        if status != 0:
            server_handle = None
            logger.error("create_server_handle Error!")
        else:
            server_handle_dict[server_id] = server_handle
        return server_handle

def destroy_server_handle(server_id):
    handle_destroy = _LIB.mvDestroyServerHandle
    handle_destroy.restype = c_int
    status = handle_destroy(server_handle_dict[server_id])

def inference(server_id, image_data, lens, num, img_name, c_rect, c_rect_len, task_type,reverse_rect):
    result_str = c_char_p()
    inference = _LIB.mvServerInference
    
    inference.restype = c_int
    status = inference(c_char_p(server_id.encode('utf-8')), task_type, byref(image_data),
                        byref(lens), num, byref(img_name), byref(result_str), c_rect, c_rect_len,reverse_rect)
    res = str(result_str.value, encoding='utf-8')
    if status != 0:
        logger.error("Inference Error: {}".format(res))
    status = destroy_result(result_str)
    if status != 0:
        logger.error("Destroy Result Error!")
    return res


def inferenceV2(image_data, lens, num, img_name, c_rect, c_rect_len, task_type,reverse_rect):
    result_str = c_char_p()
    inference = _LIB.mvServerInferenceV2
    
    inference.restype = c_int
    status = inference(c_char_p(task_type.encode('utf-8')), byref(image_data),
                       byref(lens), num, byref(img_name), byref(result_str), c_rect, c_rect_len,reverse_rect)
    
    if  str(task_type).count("rgb_ir_person_server") > 0:
        tmparr = str(result_str.value, encoding='utf-8').split(",null")
        tmpstr = tmparr[0]+tmparr[-1]
        res = tmpstr
    else :
        res = str(result_str.value, encoding='utf-8')
    if status != 0:
        logger.error("Inference Error: {}".format(res))
    status = destroy_result(result_str)
    if status != 0:
        logger.error("Destroy Result Error!")
    return res

def object_filter_inference(image_data, lens, num, img_name, rect_id_str, task_type, c_iou_range, c_iou_range_len):
    """[目标过滤,主要使用行人小模型推理结果和传入的检测结果做iou计算]
    Args:
        image_data ([c_char_p]): [图像数据]
        lens ([c_int]): [图像数据长度]
        num ([c_int]): [图像个数]
        img_name ([c_char_p]): [图像名称]
        rect_id_str ([str]): [传入的检测结果信息]
        task_type ([str]): [算法服务]
        c_iou_range ([c_float]): [过滤阈值]
        c_iou_range_len ([int]): [阈值个数]
    Returns:
        res ([str]): [处理结果数据]
    """
    result_str = c_char_p()
    inference = _LIB.mvObjectFilterInference

    inference.restype = c_int
    status = inference(c_char_p(task_type.encode('utf-8')), byref(image_data), byref(lens), \
                num, byref(img_name), c_char_p(rect_id_str.encode('utf-8')), byref(c_iou_range), \
                c_iou_range_len, byref(result_str))
    # 获取返回结果数据
    res = str(result_str.value, encoding='utf-8')
    return res

def destroy_result(res_str):
    destroy_res = _LIB.mvDestroyResult
    destroy_res.restype = c_int
    status = destroy_res(res_str)
    return status


def covert_c_rect(rect_list):
    """
    covert rect list to C type array
    :param rect_list:
    :return: rect array & rect num
    """
    if rect_list is None or len(rect_list) == 0:
        rect = [-1, -1, -1, -1]
        c_rect_len = 0
    else:
        rect = []
        for i in rect_list:
            for j in i:
                rect.append(j)
        c_rect_len = len(rect)
    c_rect = (c_int * len(rect))(*rect)
    return c_rect, c_rect_len


def pt_feature_extract(server_id, image_stream, name_list, rect_p, task_type):
    if len(image_stream) <= 0:
        res = '{"result": "failed", "code": 400, "error_message": "WITHOUT_FILE"}'
        return res

    c_rect, c_rect_len = covert_c_rect(rect_p)

    image_data, lens, num, img_name = covert_image2ctype(image_stream, name_list)
    result_str = c_char_p()

    # 参数传入字符串task_type转换为类
    # type = TaskType.from_str(task_type)

    object_detector = _LIB.mvServerInferenceV2
    object_detector.restype = c_int
    task_type_combine = server_id + ":" + task_type
    status = object_detector(c_char_p(task_type_combine.encode('utf-8')), byref(image_data),
                             byref(lens), num, byref(img_name), byref(result_str), c_rect, c_rect_len)
    res = str(result_str.value, encoding='utf-8')
    status = destroy_result(result_str)
    if status != 0:
        logger.error("Destroy Result Error!")
    return res

def pt_feature_match(server_id, feature1, feature2, task_type):
    result_str = c_char_p()
    feat_match = _LIB.mvFeatureProcess
    feat_match.restype = c_int
    status = feat_match(c_char_p(server_id.encode('utf-8')), c_char_p(feature1.encode('utf-8')), c_char_p(feature2.encode('utf-8')), byref(result_str))

    res = str(result_str.value, encoding='utf-8')
    status = destroy_result(result_str)
    if status != 0:
        logger.error("Destroy Result Error!")
    return res