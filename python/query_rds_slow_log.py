#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @date: 2020/03/18 16:11
# @name: query_rds_slow_logs
# @mail: vickeywu557@qq.com
# @author：vickey-wu
"""
获取前一天的慢日志明细
阿里云api：https://api.aliyun.com/?spm=5176.229977.1222527.6.3de4501cDVmmRU#/?product=Rds&version=2014-08-15&api=DescribeSlowLogRecords&params={%22RegionId%22:%22default%22,%22DBInstanceId%22:%22rm-bp1t1e49k3c1ejr06%22,%22StartTime%22:%222020-03-16T16:00Z%22,%22EndTime%22:%222020-03-17T16:00Z%22,%22DBName%22:%22vickey-wu%22,%22PageSize%22:%22100%22}&tab=DEMO&lang=JAVA
"""

from __future__ import division

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkrds.request.v20140815.DescribeSlowLogRecordsRequest import DescribeSlowLogRecordsRequest

from dingding import Dingding
import datetime
import os
import json
import math


def get_data(page=1, size=100):
    client = AcsClient('xxxx','xxxxxxxx','cn-hangzhou')
    
    request = DescribeSlowLogRecordsRequest()
    request.set_accept_format('json')
    
    today = datetime.date.today()
    day_before_yesterday = str(datetime.date.today() + datetime.timedelta(days=-2))
    yesterday = str(datetime.date.today() + datetime.timedelta(days=-1))
    
    # 测试
    request.set_DBInstanceId("rm-xxxxxxxxx")
    #request.set_StartTime("2020-03-16T16:00Z")
    #request.set_EndTime("2020-03-17T16:00Z")
    request.set_StartTime(day_before_yesterday + "T16:00Z")
    request.set_EndTime(yesterday + "T16:00Z")
    request.set_DBName("vickey-wu")
    request.set_PageSize(size)
    request.set_PageNumber(page)
    
    response = client.do_action_with_exception(request)
    response = json.loads(response)
    return response


def main():
    # 获取阿里云原始数据
    response = get_data()
    total_records_list = response['Items']['SQLSlowRecord']
    total_records = response['TotalRecordCount']
    #print('总记录数: ', total_records)

    # 计算总共有多少页,默认一页100条
    page, size = 1, 100
    page_nums = int(math.ceil(total_records / size))

    # 获取所有页的慢日志
    for p in range(2, page_nums + 1):
        next_page_response = get_data(page=p, size=size)
        next_page_items = next_page_response['Items']['SQLSlowRecord']
        total_records_list.extend(next_page_items)
    
    # 过滤掉非vickey-wu用户的慢日志
    filter_records_list =  [r for r in total_records_list if 'vickey-wu' in r['HostAddress']]

    # 去重相同的查询语句
    unique_key = set(r['SQLText'] for r in filter_records_list)

    # 获取排序后最慢的top 10慢日志
    top_slow_records = []
    for k in unique_key:
        items_dict = {'SQLText':'', 'QueryTimes': '', 'RequestTimes': 0}
        items_dict['SQLText'] = k
        for raw_key in filter_records_list:
            items_dict['QueryTimes'] = raw_key['QueryTimes']
            if raw_key['SQLText'] == k:
                items_dict['RequestTimes'] += 1
        top_slow_records.append(items_dict)

    sorted_top_records = sorted(top_slow_records, reverse=True, key=lambda x: x['RequestTimes'])

    # 将慢日志发送到钉钉群
    access_token = 'xxxxxxxxxxxxxxxx'
    for i in sorted_top_records[:10]:
        ding = Dingding(access_token, '查询时间(秒), 慢日志语句, 查询次数:\n' + str(i))
        ding.send_dingding()


if __name__ == '__main__':
    main()
