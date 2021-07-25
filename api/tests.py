# import time
#
#
# def formatTimeToStamp(formatTime):
#     return int(time.mktime(time.strptime(formatTime, "%Y-%m-%d %H:%M:%S")))
#
#
# def timeSub(startTime, endTIme):
#     return formatTimeToStamp(endTIme) - formatTimeToStamp(startTime)
#
#
# # print(timeSub('2020-12-16 15:20:45','2020-12-16 15:33:45'))
#
# from faker import Faker  # 1
#
# fake = Faker(locale='zh_CN')  # 2
#
# print(fake.name())  # 3
#
# print(fake.address())

import re
#
# str_test = "/api/v1/dsyncDataSource?name=${aaa}&type=&ip=&pageNum=${XXX}&pageSize=20"
#
# a = re.sub('\$\{\w+\}','啊啊啊啊啊啊啊啊啊啊啊啊啊啊',str_test)
#
# b = re.findall('\$\{\w+\}', str_test)
# value = '''{
#   "code": "${code}",
#   "message": "${message}",
#   "testkey": "${message}"
# }'''
# replaceValue = 'success'
# var = "${message}"
# value = re.sub('(\$\{' + var[2:-1] + '\})', replaceValue, value)
# value1 = value.replace(var, replaceValue)
# c = re.sub('(\$\{aaa\})','啊啊啊啊啊啊啊啊啊啊啊啊啊啊',str_test)
#
# d = re.findall('(\$\{aaa\})', str_test)
#
# print(a)
# print(b)
# print(c)
# print(d)
# import jsonpath
# a = {
#     "a":"v",
#     "d":[{"b":"b"},{"c":"c"}]
# }
#
# a = jsonpath.jsonpath(a,"$.d.")
# print(a)
# res = {"çsss":"wehweh"}
# value = {
#     "a":"b",
#     "c":[{
#         "d":"e"
#     },{
#         "f":"g"
#     }]
# }
# c = '["a"]'
# exec ("value" + c + " = %s" %res)
# print(value)
# print(type(value))

# from django_redis import get_redis_connection
#
# redisConnect = get_redis_connection('default')
# a = redisConnect.ttl("publicParams3")
# print(a)


# from apscheduler.schedulers.background import BackgroundScheduler
# import time
#
# scheduler1 = BackgroundScheduler()
# def job1():
#     print(1111)
#     a = scheduler1.get_jobs()
#     print(a)
#     return
#
# scheduler1.add_job(job1, 'cron', year='*', month='*', day='*', week='*',
#                    day_of_week='*', hour='*', minute="0/1", second='0',id="111",
#                    start_date = "2017-10-30",end_date='2020-12-30 09:51:00')

# scheduler1.add_job(job1, 'date', run_date=time.struct_time(tm_year=2020, tm_mon=12, tm_mday=30, tm_hour=0, tm_min=10, tm_sec=5, tm_wday=2, tm_yday=365, tm_isdst=0))

# scheduler1.start()
#
# print(111)
# while True:
#     pass


# import time
# a = time.time() + 10
# timeArray = time.localtime(a)
# otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
# print(otherStyleTime)   # 2013--10--10 23:40:00


# from collections import Counter
# List = [1,2,1,2,"python","python"]
# print(Counter(List))
# list = dict(Counter(List))
# print(list)
# data1 = []
# for key,value in list.items():
#     data = []
#     data.append(key)
#     data.append(value)
#     data1.append(data)
# print(data1)

# url = "http://192.168.239.7:9143/zbsb/department"
#
# a = "/"+"/".join(url.split("/")[3::])
#
# print(a)