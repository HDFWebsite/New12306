# THE WINTER IS COMING! the old driver will be driving who was a man of the world!
# -*- coding: utf-8 -*- python 3.6.7, create time is 18-12-6 下午9:33 GMT+8

import requests

def getProxy():
    url = 'http://www.hdfwebsite.club:8080/proxy'
    resp = requests.get(url)
    return {'https':resp.text}
