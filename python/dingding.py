#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import json
import os
import sys
# 这个是钉钉群组的机器人
access_token = '***'


def get_token():
    url_token = 'https://oapi.dingtalk.com/robot/send?access_token=%s' % access_token
    return url_token


# url钉钉群机器人链接 content：要发送的告警信息
def send_notification(url, content):
    '''
    msgtype : 类型
    content : 内容
    '''
    msgtype = 'text'
    values = {
        "msgtype": "text",
        msgtype: {
            "content": content
        },
        "at": {
            "atMobiles": ["18888888888"]
        },
    }
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    values = json.dumps(values)
    res = requests.post(url, values, headers=headers)
    errmsg = json.loads(res.text)['errmsg']
    if errmsg == 'ok':
        return "ok"
    return "fail: %s" % res.text


if __name__ == '__main__':
    url_token = get_token()
    content = '\n'.join(sys.argv[2:])       # 接受传入参数作为发送的信息
    print(sys.argv[2:])
    if not content:
        content = '测试'
    print send_notification(url_token, content)
