#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @date: 2018/6/28 13:52
# @name: bandwidth
# @mail: vickeywu557@qq.com
# @author：vickey-wu
"""
每天9点临时升级带宽到指定日期时间
"""

import datetime
import os
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import ModifyInstanceNetworkSpecRequest

today = datetime.date.today()
#tomorrow = datetime.date.today()
#tomorrow = datetime.date.today() + datetime.timedelta(days=1)
clt = client.AcsClient('xxxxxxxxxx','xxxxxxxxxxxxxxxxxxx','cn-hangzhou')
# 设置参数
request = ModifyInstanceNetworkSpecRequest.ModifyInstanceNetworkSpecRequest()
request.set_accept_format('json')
request.add_query_param('InstanceId', 'xxxxxxxxxxxxx')
request.add_query_param('StartTime', str(today) + 'T00:50Z ')
request.add_query_param('EndTime', str(today) + 'T11Z')
# startTime 时间要求是UTC时间并精确到分钟，时间比当前时间至少多2分钟，
# 所以当设定定时任务9点执行该脚本时可能已经过了几秒，就不足2分钟，所以设置为2018-06-28T01:03Z分
print str(today)
# request.add_query_param('StartTime', '2018-06-28T03:40Z ')
# 出带宽35M入带宽35M
request.add_query_param('InternetMaxBandwidthIn', 28)
request.add_query_param('InternetMaxBandwidthOut', 28)
# 发起请求
response = clt.do_action(request)
print("modify successfully", response)
