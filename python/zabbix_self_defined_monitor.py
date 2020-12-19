#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
获取linux服务器输入参数argv，根据argv在字典找到对应要监控的接口链接作为参数传入相应的函数验证状态，
如果链接返回参数是正常的则返回1，否则返回0，zabbix前台"报警媒介类型"创建使用脚本dingding.py发送告警信息到钉钉
"""
import json
import urllib2
import re
import requests
import sys


def get_status(interface_url):
    """
    :param interface_url:
    :return:
    """
    pre = re.findall("http://", interface_url)
    if not pre:
        interface_url = "http://" + interface_url
    try:
        response = urllib2.urlopen(interface_url, timeout=5)
    except:
        return 0
    try:
        status = json.loads(response.read())["status"]
        if status == "UP":
            return 1
        else:
            return 0
    except:
        return 0


def main():
    interface_dict = {"link1": "api/link1",
                      "link2": "api/link2",
                      "xml": "api/test.xml",
    # get linux os input arg
    try:
        interface = sys.argv[1]
    except:
        print(0)
        return 0
    if interface != "" and interface in interface_dict.keys():
        if interface == "test" or interface == "test-https":
            status = xml_status(interface_dict[interface])
        else:
            status = get_status(interface_dict[interface])
        print(status)
        return status
    else:
        print(0)
        return 0

if __name__ == '__main__':
    main()
