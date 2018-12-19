# THE WINTER IS COMING! the old driver will be driving who was a man of the world!
# -*- coding: utf-8 -*- python 3.6.7, create time is 18-12-6 下午9:07 GMT+8

# coding:utf-8

import datetime


def parseDate(train_date):
    """
    :param train_date: '2017-12-12'
    :return:
    """
    week_name = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    month_name = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    y, m, d = map(int, train_date.split("-"))
    weekday = datetime.datetime(y, m, d).weekday()
    # Fri Nov 24 2017 00:00:00 GMT+0800 (中国标准时间)
    return "{0} {1} {2} {3} 00:00:00 GMT+0800 (中国标准时间)".format(week_name[weekday], month_name[m - 1], d, y)
