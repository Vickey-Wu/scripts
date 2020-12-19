#!/usr/bin/python
#-*- coding:utf-8 -*-
from qcloudsms_py import SmsVoicePromptSender
from qcloudsms_py.httpclient import HTTPError

phone_numbers = ["1888888888"]
result = ''
vpsender = SmsVoicePromptSender('88888', '****')
try:
    result = vpsender.send("86", phone_numbers[0], 2, "服务器异常, 及时处理", 2)
except HTTPError as e:
    print(e)
except Exception as e:
    print(e)

print(result['errmsg'])
