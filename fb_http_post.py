#!/usr/bin/env python
# encoding: utf-8

import requests

#r = requests.post("http://123.57.41.242:8090/user", data={'@number': 12524, '@type': 'issue', '@action': 'show'})
r = requests.post("graph.facebook.com", data={'@number': 12524, '@type': 'issue', '@action': 'show'})
print(r.status_code, r.reason)
print(r.text[:300] + '...')
