# -*- coding: utf-8 -*-

import os
import platform
import re
import runcommand

from log import logger
logger = logger()


def getAVDs():
    """  获取当前的虚拟设备

    :returns: 返回当前拥有的虚拟设备列表
    :rtype: list
    """
    re_avd = re.compile('^[ ]+Name: ([a-zA-Z0-9_:.-]+)', re.MULTILINE)
    avds = re_avd.findall(runcommand.runCommand("android list avd"))
    return avds


def isDeviceAttached(device):
    """ 判断设备是否在线,

    :param device: 设备的串号
    :type device: string

    :returns: 如果设备在线，返回True，否则返回False
    :rtype: bool
    """
    return device in getAttachedDevices(emulator=True)


def getAttachedDevices(hardware=True, emulator=False, offline=False):
    """ 获取当前PC上连接着的设备。

    :param hardware: 返回的设备中是否包含真实的设备，默认为 ``True``
    :type hardware: bool

    :param emulator:  返回的设备中是否包含模拟器，默认为 ``False``
    :type emulator: bool

    :param offline: 返回的设备中是否包含掉线的设备,默认为 ``False``
    :type offline: bool

    :returns: 根据设置返回设备列表
    :rtype: list
    """
    logger.info("获取当前PC上连接着的设备...")
    adb_devices_output = runcommand.runCommand("adb devices")

    error_string = "command not found"
    if error_string in adb_devices_output:
        raise Exception("未安装adb工具，或者adb环境变量配置错误！！")

    if platform.system().upper() == "Windows".upper():
        adb_devices_output = adb_devices_output.replace("\r\n", "\n")

    logger.debug("output of 'adb devices' command:\n%s" % adb_devices_output)

    re_device = re.compile('^([a-zA-Z0-9_:.-]+)\tdevice$', re.MULTILINE)
    online_devices = re_device.findall(adb_devices_output)

    re_device = re.compile('^(emulator-[0-9]+)\tdevice', re.MULTILINE)
    emulator_devices = re_device.findall(adb_devices_output)

    re_device = re.compile('^([a-zA-Z0-9_:.-]+)\toffline$', re.MULTILINE)
    offline_devices = re_device.findall(adb_devices_output)

    devices_list = []
    if online_devices or emulator_devices or offline_devices:

        # First determine list of online devices (e.g. hardware and/or emulator).
        if hardware and emulator:
            devices_list = online_devices
        elif hardware:
            devices_list = [device for device in online_devices
                       if device not in emulator_devices]
        elif emulator:
            devices_list = emulator_devices

        # Now add offline devices if offline is true
        if offline:
            devices_list = devices_list + offline_devices

    preferred_device = os.environ.get('ANDROID_SERIAL')
    if preferred_device in devices_list:
        devices_list.remove(preferred_device)
        devices_list.insert(0, preferred_device)

    logger.info("当前PC上连接着的设备: %s" % devices_list)
    return devices_list


def restartAdbServer():
    """ 重启adb server
    """
    killAdbServer()
    startAdbServer()


def killAdbServer():
    """ 关闭adb server
    """
    runcommand.runCommand("adb kill-server")


def startAdbServer():
    """ 启动 adb server
    """
    runcommand.runCommand("adb start-server")
