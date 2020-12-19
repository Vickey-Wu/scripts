#!/usr/bin/python
# -*- coding: utf8 -*-
"""
# @date: 2018/6/22 17:47 
# @name: ali_daily_check.py
# @mail: vickeywu557@qq.com
# @author：vickey-wu
# 获取阿里云服务器告警信息，云服务器和云数据库过期日期，快照备份情况
"""
import os
import json
import time
import requests
import datetime


# pip install aliyun-python-sdk-core
try:
    from aliyunsdkcore import client
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    from aliyunsdkcore.acs_exception.exceptions import ClientException
    from aliyunsdkcore.acs_exception.exceptions import ServerException
except:
    os.system("pip install aliyun-python-sdk-core")
# pip install aliyun-python-sdk-ecs
try:
    from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
    from aliyunsdkecs.request.v20140526 import StopInstanceRequest
    from aliyunsdkecs.request.v20140526 import DescribeSnapshotsRequest
    from aliyunsdkecs.request.v20140526 import ModifyInstanceNetworkSpecRequest
except:
    os.system("pip install aliyun-python-sdk-ecs")
# pip install aliyun-python-sdk-cms
try:
    from aliyunsdkcms.request.v20180308 import ListAlarmHistoryRequest
except:
    os.system("pip install aliyun-python-sdk-cms")


def expire_time(AccessKeyId, AccessKeySecret, RegionId):
    # 获取服务器系统3天后日期
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=3)
    day_sys, month_sys, year_sys = tomorrow.strftime('%d'), tomorrow.strftime('%m'), tomorrow.strftime('%Y')
    #print(day_sys, month_sys, year_sys)
    expire_list = []
    for reg in RegionId:
        # 创建AcsClient实例
        client = AcsClient(AccessKeyId, AccessKeySecret, reg)
        # 创建request，并设置参数
        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_PageSize(100)
        # 发起API请求并显示返回值
        response = client.do_action_with_exception(request)
        #print(response)
        instance = json.loads(response)["Instances"]["Instance"]
        for ins in instance:
            ali_time = ins["ExpiredTime"].split("-")
            #print("alitime", ali_time)
            year_ali, month_ali, day_ali = ali_time[0], ali_time[1], ali_time[2][:2]
            # 如果系统时间与获取到的阿里云服务器过期时间相差小于或等于3天则告警
            if int(day_ali) <= (int(day_sys) + 3) and int(month_ali) <= int(month_sys) and int(year_ali) <= int(year_sys):
                ip = ins["InnerIpAddress"]["IpAddress"]
                # 返回的json中ip可能会为空，为空则用instanceId代替
                if ip == []:
                    ip = ins["InstanceId"]
                expire_time = ins["ExpiredTime"][:10]
                expire_list.append([ip, expire_time])
    # 如果有要过期的服务器则打印列表，没有则不打印
    if expire_list != []:
        return "server would expired: ", expire_list
    else:
        return "there is no expire server now"


def alarm_info(AccessKeyId, AccessKeySecret, RegionId):
    alarm_list, tmp_list = [], []
    client = AcsClient(AccessKeyId, AccessKeySecret, RegionId[0])
    # 设置参数
    request = ListAlarmHistoryRequest.ListAlarmHistoryRequest()
    request.set_accept_format('json')
    # 发起请求
    response = client.do_action(request)
    #print(response)
    # 如果value为running并且state为alarm则为正在告警
    alarms = json.loads(response)["AlarmHistoryList"]["AlarmHistory"]
    if len(alarms):
        for alarm in alarms:
            tmp_list.append(alarm["Name"])
        for alarm in set(tmp_list):
            # 正在告警reponse会返回告警实例包含2个状态为alarm的记录
            # 如果恢复正常会返回第3条状态为OK的记录
            if tmp_list.count(alarm) != 3:
                alarm_list.append([alarm, "alarm"])
    else:
        alarm_list.append(["no alarm"])
    # 返回结果
    return "alarm server: ", alarm_list


def snapshot(AccessKeyId, AccessKeySecret, RegionId):
    snapshot_list = [] 
    for reg in RegionId:
        client = AcsClient(AccessKeyId, AccessKeySecret, reg)
        # 查询实例详情的默认参数设置 
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('ecs.aliyuncs.com')
        request.set_method('POST')
        request.set_version('2014-05-26')
        request.set_action_name('DescribeInstances')
        # 自定义添加查询参数 
        request.add_query_param('PageSize', '100') 
        request.add_query_param('RegionId', reg)
        # 发送请求 
        response = client.do_action_with_exception(request)
        instance = json.loads(response)["Instances"]["Instance"]
        for ins in instance:
            # 查询实例快照的api默认参数设置
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('ecs.aliyuncs.com')
            request.set_method('POST')
            request.set_version('2014-05-26')
            request.set_action_name('DescribeSnapshots')
            # 自定义添加查询参数 
            request.add_query_param('RegionId', reg)
            request.add_query_param('InstanceId', ins["InstanceId"])
            # 发送请求 
            response = client.do_action_with_exception(request)
            try:
                snapshot_status = json.loads(response)["Snapshots"]["Snapshot"][0]["Status"]
                if snapshot_status != "accomplished":
                    snapshot_list.append([ins["InstanceId"], "snapshot failed"])
            except:
                snapshot_list.append([ins["InstanceId"], "no snapshot"])

    if snapshot_list != []:
        return snapshot_list
    else:
        return "all snapshot backup successfully"


def rds_mysql(AccessKeyId, AccessKeySecret, RegionId):
    # 获取服务器系统3天后日期
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=3)
    day_sys, month_sys, year_sys = tomorrow.strftime('%d'), tomorrow.strftime('%m'), tomorrow.strftime('%Y')
    # rds实例存放列表
    rds_list = [] 
    for reg in RegionId:
        client = AcsClient(AccessKeyId, AccessKeySecret, reg)
        # 查询实例详情的默认参数设置 
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('rds.aliyuncs.com')
        request.set_method('POST')
        request.set_version('2014-08-15')
        request.set_action_name('DescribeDBInstances')
        # 自定义添加查询参数 
        request.add_query_param('PageSize', '100') 
        request.add_query_param('RegionId', reg)
        # 发送请求 
        response = client.do_action_with_exception(request)
        instance = json.loads(response)["Items"]["DBInstance"]
        print("instance", instance)
        for ins in instance:
            # 查询实例详情的默认参数设置
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('rds.aliyuncs.com')
            request.set_method('POST')
            request.set_version('2014-08-15')
            request.set_action_name('DescribeDBInstanceAttribute')
            # 自定义添加查询参数 
            request.add_query_param('RegionId', reg)
            request.add_query_param('DBInstanceId', ins["DBInstanceId"])
            # 发送请求 
            rds_id = ins["DBInstanceId"]
            response = client.do_action_with_exception(request)
            #print("time", response)
            rds_time = json.loads(response)["Items"]["DBInstanceAttribute"][0]["ExpireTime"]
            #print(rds_time)
            if rds_time != '':
                ali_time = rds_time.split("-")
                #ali_time = ins["ExpiredTime"].split("-")
                year_ali, month_ali, day_ali = ali_time[0], ali_time[1], ali_time[2][:2]
                # 如果系统时间与获取到的阿里云rds过期时间相差小于或等于3天则告警
                if int(day_ali) <= (int(day_sys) + 3) and int(month_ali) <= int(month_sys) and int(year_ali) <= int(year_sys):
                    expire_time = rds_time[:10]
                    rds_list.append([rds_id, expire_time])
            else:
                print("按量db", rds_id)

    # 如果有要过期的rds实例则打印列表，没有则不打印
    #print(rds_list)
    if rds_list != []:
        return "mysql rds would expired: ", rds_list
    else:
        return "no mysql expired"


def rds_redis(AccessKeyId, AccessKeySecret, RegionId):
    # 获取服务器系统3天后日期
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=3)
    day_sys, month_sys, year_sys = tomorrow.strftime('%d'), tomorrow.strftime('%m'), tomorrow.strftime('%Y')
    # rds实例存放列表
    rds_list = [] 
    for reg in RegionId:
        client = AcsClient(AccessKeyId, AccessKeySecret, reg)
        # 查询实例详情的默认参数设置 
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('r-kvstore.aliyuncs.com')
        request.set_method('POST')
        request.set_version('2015-01-01')
        request.set_action_name('DescribeInstances')
        # 自定义添加查询参数 
        request.add_query_param('RegionId', reg)
        request.add_query_param('PageSize', '50') 
        # 发送请求 
        response = client.do_action_with_exception(request)
        instance = json.loads(response)["Instances"]["KVStoreInstance"]
        for ins in instance:
            # 查询实例详情的默认参数设置
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('r-kvstore.aliyuncs.com')
            request.set_method('POST')
            request.set_version('2015-01-01')
            request.set_action_name('DescribeInstanceAttribute')
            # 自定义添加查询参数 
            request.add_query_param('RegionId', reg)
            request.add_query_param('InstanceId', ins["InstanceId"])
            # 发送请求 
            response = client.do_action_with_exception(request)
            try:
                rds_time = json.loads(response)["Instances"]["DBInstanceAttribute"][0]["EndTime"]
                ali_time = rds_time.split("-")
                #ali_time = ins["ExpiredTime"].split("-")
                year_ali, month_ali, day_ali = ali_time[0], ali_time[1], ali_time[2][:2]
                # 如果系统时间与获取到的阿里云rds过期时间相差小于或等于3天则告警
                if int(day_ali) <= (int(day_sys) + 3) and int(month_ali) <= int(month_sys) and int(year_ali) <= int(year_sys):
                    rds_id = ins["InstanceId"]
                    expire_time = rds_time[:10]
                    rds_list.append([rds_id, expire_time])
            except Exception as e:
                print(response)
                print("按量付费实例无到期时间", ins, e)

    # 如果有要过期的rds实例则打印列表，没有则不打印
    #print(rds_list)
    if rds_list != []:
        return "redis rds would expired: ", rds_list
    else:
        return "no redis rds expired"


def dingding(access_token, content):
    token_url = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % access_token

    msgtype = 'text'
    values = {
        "msgtype": "text",
        msgtype: {
            "content": content
        },
        "at": {
            #"atMobiles": ["+86-1888888888"]
            "atMobiles": ["+86-188888888"]
        },
    }
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    values = json.dumps(values)
    res = requests.post(token_url, values, headers=headers)
    errmsg = json.loads(res.text)['errmsg']
    if errmsg == 'ok':
        return "ok"
    return "fail: %s" % res.text


def main():
    # acess list format ["AccessKeyId", "AccessKeySecret"] https://bbs.aliyun.com/read/543178.html
    access_list = [["xxxxxxx", "xxxxxxxxxxxxxxxx"],["xxxxxxxxx", "xxxxxxxxxxxxxxxxxxxxx"]]
    RegionId = ["cn-hangzhou", "cn-shenzhen", "cn-hongkong"]
    # dingdingbot access_token
    access_token = 'xxxxxxxxxxxxx'

    for i in range(len(access_list)):
        AccessKeyId = access_list[i][0]
        AccessKeySecret = access_list[i][1]

        expire_information = expire_time(AccessKeyId, AccessKeySecret, RegionId)
        alarm_information = alarm_info(AccessKeyId, AccessKeySecret, RegionId)
        snapshot_information = snapshot(AccessKeyId, AccessKeySecret, RegionId)
        mysql_information = rds_mysql(AccessKeyId, AccessKeySecret, RegionId)
        redis_information = rds_redis(AccessKeyId, AccessKeySecret, RegionId)
        content = [expire_information, alarm_information, snapshot_information, mysql_information, redis_information]
        dingding(access_token, content)


if __name__ == "__main__":
    main()
