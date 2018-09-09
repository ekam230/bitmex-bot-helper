#!/usr/bin/env python3
#--------------------#
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import playsound
import platform

# Подключаем главный исполнительный модуль
from bitmex_helper import *

#=================================================================================================================
def Main():

    writeWelcomeMessage()

    while True:
        curPos = positionManager()

        isPos = curPos['isPos']
        # inTrade = curPos['inTrade']
        # posStarted = curPos['posStarted']
        next_step = curPos['next_step']

        if isPos == True and (next_step == 'WAITING_FOR_STOP_ORDER' or next_step == 'WAITING_FOR_PROFIT_ORDER'):
            waitStopAndProfitOrders(curPos['posInfo'])
        elif isPos == True and next_step == 'WAITING_FOR_TRADE_ENDING':
            waitTradeEnd()
        elif isPos == False and next_step == 'KILLING_OPPOSIT_ORDER':
            killOppositeOrders()
        elif isPos == False and next_step == 'WAITING_FOR_NEW_POSITION':
            # уходим на новый круг
            k = 1
        else:
             #dump(red('Main():'),'Что-то пошло не так...')
             # dump(red('ЖДЕМ-с...'),'Мы просто все еще НЕ в сделке...')
             if next_step != 'KILLING_OPPOSIT_ORDER':
                 # мы, очевидно, вышли из позиции ВСТРЕЧНЫМ ордером и наши СТОП и ТЕЙК остались висеть
                 next_step = 'KILLING_OPPOSIT_ORDER'
             # time.sleep(5)
             k = 0

#--- End of main() ---#

#=================================================================================================================
try:
    # Многократный (циклический) вызов  - основной цикл программы
    #---
    Main()


    #---
except KeyboardInterrupt as e:
    dump(grey('--------------------------'))
    dump(yellow('Остановка по требованию ;-)'))
    dump(grey('----------------------------'))
except ccxt.DDoSProtection as e:
    print(type(e).__name__, e.args, 'DDoS Protection (ignoring)')
except ccxt.RequestTimeout as e:
    print(type(e).__name__, e.args, 'Request Timeout (ignoring)')
except ccxt.ExchangeNotAvailable as e:
    print(type(e).__name__, e.args, 'Exchange Not Available due to downtime or maintenance (ignoring)')
except ccxt.AuthenticationError as e:
    print(type(e).__name__, e.args, 'Authentication Error (missing API keys, ignoring)')
