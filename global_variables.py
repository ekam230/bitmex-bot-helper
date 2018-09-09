#!/usr/bin/env python3
#--------------------#
# -*- coding: utf-8 -*-
import settings as config
from dump_functions import *
from restapi_functions import *


# Дальше служебное
stop = config.stop
profit = config.profit
delta = config.delta
isTestMode = config.TestMode
taWS = config.toWs
taREST = config.toRest
stop_id = 0
profit_id = 0
order_id = 0
order_status = ''
order_price = 0
order_amount = 0
order_side = ''
order_type = ''
statnum = 0
params = {}
pos_Upnl = 0
pos_Rpnl = 0
pos_Lprice = 0
pos_Mprice = 0
bidPrice = 0
midPrice = 0
askPrice = 0

symbolW = config.symbolW
symbolC = config.symbolC

useMarketProfit = False

#CO - CheckingOrders - структура, в которой будем хранить данные о текущей ситуации
co = {
    #id: price
}
#OTB - OrdersToBuy - список цен ордеров на ПОКУПКУ, отсортированных от самой большой до самой маленькой цены
otb = [
    # price, price, price
]
#OTS - OrdersToSell - список цен ордеров на ПРОДАЖУ, отсортированных от самой маленькой до самой большой цены
ots = [
    # price, price, price
]
inTrade = False
posStarted = False

next_step = 'WAITING_FOR_LIMIT_ORDER'
# next_step = 'WAITING_FOR_ORDER_FILLING'
# next_step = 'WAITING_STOP_AND_PROFIT_ORDERS'
# next_step = 'WAITING_FOR_STOP_ORDER'
# next_step = 'WAITING_FOR_PROFIT_ORDER'
# next_step = 'WAITING_FOR_TRADE_ENDING'
# next_step = 'KILLING_OPPOSIT_ORDER'
