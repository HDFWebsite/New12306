
import base64
import json
import os
import re
import time

import requests

from utils.captcha import getCode

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
}

s = requests.session()
s.headers = headers

# 使用代理ip
# while True:
#     try:
#         s.proxies = getProxy()
#         s.get('https://www.12306.cn/index/', timeout=8)
#         break
#     except:
#         print('替换代理ip')
#         pass

s.get('https://www.12306.cn/index/')

s.get('https://kyfw.12306.cn/otn/resources/login.html')
# 1. 获取验证码图片
temp = str(time.time()*1000)[:-4]  # 15421 76058 853
url = 'https://kyfw.12306.cn/passport/captcha/captcha-image64?login_site=E&module=login&rand=sjrand&_={}'.format(temp)
resp = s.get(url)
captcha_img_b64 = json.loads(resp.text)['image']
captcha_img = base64.b64decode(captcha_img_b64)
with open('./captcha_imgs/{}.png'.format(temp), 'wb') as f:
    f.write(captcha_img)

"""获取验证码坐标"""
image_name = temp+'png'
answer_num = getCode(image_name)

os.rename('./captcha_imgs/{}.png'.format(temp),
          './captcha_imgs/{}_{}.png'.format(temp,answer_num))
answer_dict = {
    '1': '37,46,',
    '2': '110,46,',
    '3': '181,46,',
    '4': '253,46,',
    '5': '37,116,',
    '6': '110,116,',
    '7': '181,116,',
    '8': '253,116,',
}
# 2. 校验验证码 # 192,93,37,28
answer = ''
for i in answer_num:
    answer += answer_dict[i]
answer = answer[:-1]
print(answer)

# 发送验证码验证请求
url = 'https://kyfw.12306.cn/passport/captcha/captcha-check?answer={}&rand=sjrand&login_site=E&_={}'.format(answer ,str(time.time()*1000)[:-4])
resp = s.get(url)
print(json.loads(resp.text))

# 发送登录请求 获取uamtk
url = 'https://kyfw.12306.cn/passport/web/login'
data = {
    'username': input('输入12306账号：'),
    'password': input('输入12306密码：'),
    'appid':'otn',
    'answer':answer
}
resp = s.post(url=url, data=data)
print(json.loads(resp.text))
uamtk = json.loads(resp.text)['uamtk']

url = 'https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin'
s.get(url)

# 获取newapptk
url = 'https://kyfw.12306.cn/passport/web/auth/uamtk'
data = {'appid':'otn'}
resp = s.post(url, data=data)
print(json.loads(resp.text))
newapptk = json.loads(resp.text)['newapptk']

# 登录后验证
url = 'https://kyfw.12306.cn/otn/uamauthclient'
data = {'tk': newapptk}
resp = s.post(url, data=data)
print(json.loads(resp.text))

# ?
url = 'https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete'
data = {'_json_att': ''}
resp = s.post(url, data=data)
print(json.loads(resp.text))

# 获取车站编号字符串 station_version=1.9076
# url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9076'
# resp = s.get(url)
# with open('station.js', 'w') as f:
#     f.write(resp.text)

# 获取{城市(车站):编码, ...} 键值对
# from utils.stations import stations_long_str
# stations = {}
# for station in stations_long_str.split('@'):
#     if not station: continue
#     stations[station.split('|')[1]] = station.split('|')[2]
# import json
# with open('./utils/stations_dict.py', 'w', encoding='utf8') as f:
#     f.write('stations_dict = ')
#     json.dump(stations, f, ensure_ascii=False, indent=4)


from utils.stations_dict import stations_dict

# 获取城市(车站)编码
from_station = input('输入出发城市或车站:')
to_station = input('输入到达城市或车站:')
train_date = input('输入出行日期,格式为2018-12-03:')
from_station_code = stations_dict.get(from_station, '')
to_station_code = stations_dict.get(to_station, '')

# 查询车票get : 跟12306-8一样
# log
url = 'https://kyfw.12306.cn/otn/leftTicket/log?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (
train_date, from_station_code, to_station_code)
response = s.get(url)
print(response.text)
# query
# url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2018-12-03&leftTicketDTO.from_station=BJP&leftTicketDTO.to_station=SHH&purpose_codes=ADULT'
url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT' % (
train_date, from_station_code, to_station_code)
response = s.get(url)
# 解析获取trains_list
from utils.parse_trains_infos import parseTrainsInfos
trains_list = parseTrainsInfos(json.loads(response.content)['data']['result'])
from pprint import pprint
print('查询的列车信息如下：')
pprint(trains_list)
# 获取选择的列车
train_info_dict = trains_list[int(input('请输入选中车次的下标：'))]
# 列车信息
secretStr = train_info_dict['secretStr']
leftTicket = train_info_dict['leftTicket']
train_location = train_info_dict['train_location']

# 检查用户是否保持登录成功
url = 'https://kyfw.12306.cn/otn/login/checkUser'
data = {'_json_att': ''}
resp = s.post(url, data=data)
print(json.loads(resp.text))

# 点击预定 : 跟12306-8一样
# post
url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
data = {
    'secretStr': secretStr,
    'train_date': train_date,
    'back_train_date': train_date,
    'tour_flag': 'dc',  # dc 单程 wf 往返
    'purpose_codes': 'ADULT',  # 成人
    'query_from_station_name': from_station,
    'query_to_station_name': to_station,
    'undefined': ''
}
resp = s.post(url, data=data)
print(resp.text)

# 订单初始化 获取REPEAT_SUBMIT_TOKEN key_check_isChange
url = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
data = {'_json_att': ''}
response = s.post(url, data=data)
repeat_submit_token = re.search(r"var globalRepeatSubmitToken = '([a-z0-9]+)';", response.content.decode()).group(1)
key_check_isChange = re.search("'key_check_isChange':'([A-Z0-9]+)'", response.content.decode()).group(1)

# 获取用户信息
# 需要 REPEAT_SUBMIT_TOKEN
# post
url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
data = {'_json_att': '',
        'REPEAT_SUBMIT_TOKEN': repeat_submit_token}
response = s.post(url, data=data)

# 解析并构造乘客信息列表
from utils.parse_passenger import parsePassenger
passenger_list = parsePassenger(json.loads(response.content))
print('获取乘客信息有：')
pprint(passenger_list)
passenger_info_dict = passenger_list[int(input('输入要购票的乘车人的下标'))]
# 坐席类型
from utils.parse_seat_type import seat_type_dict
try:
    seat_type = seat_type_dict[input('请输入要购买的坐席类型的拼音，如果输入错误，将强行购买无座，能回家就行了，还要tm什么自行车！：')]
except:
    seat_type = seat_type_dict['wuzuo']
# 乘客信息
passengerTicketStr = '%s,0,1,%s,%s,%s,%s,N' % (
    seat_type, passenger_info_dict['passenger_name'],
    passenger_info_dict['passenger_id_type_code'],
    passenger_info_dict['passenger_id_no'],
    passenger_info_dict['passenger_mobile_no'])
oldPassengerStr = '%s,%s,%s,1_' % (
    passenger_info_dict['passenger_name'],
    passenger_info_dict['passenger_id_type_code'],
    passenger_info_dict['passenger_id_no'])

# 检查选票人信息
url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
data = {
    'cancel_flag': '2',  # 未知
    'bed_level_order_num': '000000000000000000000000000000',  # 未知
    'passengerTicketStr': passengerTicketStr.encode('utf-8'), # O,0,1,靳文强,1,142303199512240614,18335456020,N
    'oldPassengerStr': oldPassengerStr.encode('utf-8'), # 靳文强,1,142303199512240614,1_
    'tour_flag': 'dc',  # 单程
    'randCode': '',
    'whatsSelect': '1',
    '_json_att': '',
    'REPEAT_SUBMIT_TOKEN': repeat_submit_token
}
resp = s.post(url, data=data)
print(resp.text)

# 提交订单,并获取排队人数,和车票的真是余数
url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
from utils.parse_date import parseDate
data = {
    'train_date': parseDate(train_date),  # Fri Nov 24 2017 00:00:00 GMT+0800 (中国标准时间)
    'train_no': train_info_dict['train_no'],  # 6c0000G31205
    'stationTrainCode': train_info_dict['stationTrainCode'],  # G312
    'seatType': seat_type,  # 席别
    'fromStationTelecode': train_info_dict['from_station'],  # one_train[6]
    'toStationTelecode': train_info_dict['to_station'],  # ? one_train[7]
    'leftTicket': train_info_dict['leftTicket'],  # one_train[12]
    'purpose_codes': '00',
    'train_location': train_info_dict['train_location'],  # one_train[15]
    '_json_att': '',
    'REPEAT_SUBMIT_TOKEN': repeat_submit_token
}
resp = s.post(url, data=data)
print(resp.text)
print('此时排队买票的人数为：{}'.format(json.loads(resp.text)['data']['count']))
ticket = json.loads(resp.text)['data']['ticket']
print('此时该车次的余票数量为：{}'.format(ticket))
if ticket == '0':
    print('没有余票，购票失败')

# 确认订单,进行扣票 需要 key_check_isChange
url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
data = {
    'passengerTicketStr': passengerTicketStr.encode('utf-8'),
    'oldPassengerStr': oldPassengerStr.encode('utf-8'),
    'randCode': '',
    'purpose_codes': '00',
    'key_check_isChange': key_check_isChange,
    'leftTicketStr': leftTicket,
    'train_location': train_location,  # one_train[15]
    'choose_seats': '',  # 选择坐席 ABCDEF 上中下铺 默认为空不选
    'seatDetailType': '000',
    'whatsSelect': '1',
    'roomType': '00',
    'dwAll': 'N',  # ?
    '_json_att': '',
    'REPEAT_SUBMIT_TOKEN': repeat_submit_token
}
resp = s.post(url, data=data)
print(json.loads(resp.text))
if json.loads(resp.text)['status'] == False or json.loads(resp.text)['data']['submitStatus'] == False:
    print('扣票失败')

# 排队等待 返回waittime:4秒后发送  获取 requestID 和 orderID
# url = '/otn/confirmPassenger/queryOrderWaitTime?random=1543748214387&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=6bf02180d74427603d4e0eb8add9a4a5'
timestamp = str(int(time.time() * 1000))
url = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=%s&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=%s' % (
timestamp, repeat_submit_token)
response = s.post(url, data=data)
resp = s.post(url, data=data)
print(resp.text)

orderID = json.loads(resp.text)['data']['orderId']


# 订单结果
url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
data = {
    'orderSequence_no': orderID,
    '_json_att': '',
    'REPEAT_SUBMIT_TOKEN': repeat_submit_token
}
resp = s.post(url, data=data)
print(resp.text)