# !/usr/bin/env python
# coding=utf-8
"""
# -*- coding: UTF-8 -*-
# @date: 2018/6/22 17:46
# @name: buy_instance
# @mail: vickeywu557@qq.com
# @author：vickey-wu
调用阿里云api使用自定义镜像购买服务器
"""

import time
import json
import paramiko
import requests
import commands
from aliyunsdkcore import client
from aliyunsdkcore.request import CommonRequest
from aliyunsdkecs.request.v20140526 import CreateInstanceRequest
from aliyunsdkecs.request.v20140526 import StartInstanceRequest
from aliyunsdkecs.request.v20140526 import AllocatePublicIpAddressRequest


def buy_instance():
    clt = client.AcsClient('xxxxxx', 'xxxxxxxxxxxxx', 'cn-hangzhou')
    # 设置参数
    request = CreateInstanceRequest.CreateInstanceRequest()
    request.set_accept_format('json')
    request.add_query_param('RegionId', 'cn-hangzhou')
    request.add_query_param('SecurityGroupId', 'Gxxxxxxxxxxxxxxx')
    request.add_query_param('InternetMaxBandwidthIn', 1)
    request.add_query_param('InternetMaxBandwidthOut', 1)
    request.add_query_param('Password', 'cqmyg.123')
    # 自定义镜像
    #request.add_query_param('ImageId', 'm-xxxxxxxxxx')
    request.add_query_param('ImageId', 'm-xxxxxxxxxxxxxx')
    # 阿里云默认镜像
    # request.add_query_param('ImageId', 'ubuntu_16_0402_64_20G_alibase_20180409.vhd')
    request.add_query_param('InstanceType', 'ecs.sn1.medium')
    request.add_query_param('SystemDisk.Size', '100')
    request.add_query_param('InstanceName', 'tmp_validate_web_db')

    # 购买实例
    print("购买实例中...")
    response_buy = clt.do_action(request)
    print(response_buy)
    instance_id = json.loads(response_buy)["InstanceId"]

    # 分配公网IP
    time.sleep(3)
    print("分配公网ip中...")
    request_ip = AllocatePublicIpAddressRequest.AllocatePublicIpAddressRequest()
    request_ip.set_accept_format('json')
    request_ip.add_query_param('InstanceId', instance_id)
    response_ip = clt.do_action(request_ip)
    print("已分配IP", response_ip)

    # 启动实例
    print("启动实例中...")
    request_start = StartInstanceRequest.StartInstanceRequest()
    request_start.set_accept_format('json')
    #request_start.add_query_param('InstanceId', "i-bp15xf4ylewns1qav4q3")
    request_start.add_query_param('InstanceId', instance_id)
    response_start = clt.do_action(request_start)
    print(response_start)

    ## 设置自动释放时间
    time.sleep(70)
    request_release = CommonRequest()
    request_release.set_accept_format('json')
    request_release.set_domain('ecs.aliyuncs.com')
    request_release.set_method('POST')
    request_release.set_version('2014-05-26')
    request_release.set_action_name('ModifyInstanceAutoReleaseTime')
    request_release.add_query_param('InstanceId', instance_id)
    # 设置3个小时后自动释放服务器
    release_time_date = commands.getstatusoutput('date -u "+%Y-%m-%dT"')[1]
    tmp_hour = commands.getstatusoutput('date -u "+%H"')[1]
    release_time_hour = str(int(tmp_hour) + 4)
    # 如果小时小于10点，转为数字后会少个0
    if len(release_time_hour) == 1:
        release_time_hour = "0" + release_time_hour
    # 分钟要求是UTC时间并精确到分钟，时间比当前时间至少多2分钟，不然会接口调用失败
    tmp_minute = commands.getstatusoutput('date -u "+%M"')[1]
    release_time_minute = str(int(tmp_minute) + 3)
    # 如果遇到加了3分钟后大于59分的则直接设置分钟为3分钟，小时则加一小时
    if int(release_time_minute) > 59:
        release_time_minute = "03"
        release_time_hour = str(int(release_time_hour) + 1)
        if len(release_time_minute) == 1:
            release_time_minute = "0" + release_time_minute
        if len(release_time_hour) == 1:
            release_time_hour = "0" + release_time_hour
    if len(release_time_minute) == 1:
        release_time_minute = "0" + release_time_minute
    release_time = str(release_time_date) + str(release_time_hour) + ":" + str(release_time_minute) + ":00Z"
    print(release_time)
    # 发送请求
    request_release.add_query_param('AutoReleaseTime', release_time)
    response_release = clt.do_action_with_exception(request_release)
    print response_release
    #return ip


def main():
    buy_instance()


if __name__ == "__main__":
    main()
