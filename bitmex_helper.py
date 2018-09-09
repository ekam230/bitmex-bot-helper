#!/usr/bin/env python3
#--------------------#
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import playsound
import platform

# Подключаем базовую конфигурацию
from global_variables import *
from dump_functions import *
from restapi_functions import *

#print('taREST: ', config.toRest)
#print('taREST: ', taREST)

#=========================================================================
""" Проверяем наличие реального ордера на бирже по имеющемуся у нас ID """
#=========================================================================
def ordersCheck(id):
    #orders = getOrders_WS()
    orders = getOpenOrders_REST(symbolC, taREST)
    if orders != '':
        # если есть хотя бы один ордер - проверим по нужному нам ID
        #checked_orders = [o for o in orders if o['idorderID'] == id]
        checked_orders = [o for o in orders if o['id'] == id]
        # в идеале должно возвращаться ровно ОДНО значение
        num = len(checked_orders)
        if num == 1:
            # Ордер найден - все ок
            return True
        else:
            # при любом другом раскладе - то ли их НОЛЬ то ли их НЕСКОЛЬКО (такого быть не может, конечно!!!)
            return False
    else:
        # значит нет вообще никаких ордеров - ну и нашего проверяемого тоже, соответственно, НЕТ
        return False

#--- End of ordersCheck() ---#

#===============================================
""" Создаем СТОП-ордер с нужными параметрами """
#===============================================
def makeStopOrder(size, stop_price, limit_price, side):
   global stop_id
   global next_step
   global inTrade

   #stop_id = isOrderByParams_WS('StopLimit', side, size, limit_price)
   #stop_id = isOrderByParams_REST(symbolC, 'StopLimit', side, size, limit_price, taREST)
   stop_id = 0
   if stop_id == 0 and size != 0:
       # будем создавать новый СТОП только в том случае, если у нас при этом не возникнут ДУБЛИ!!!
       stop_id = newStopOrder_REST(symbolC, size, stop_price, limit_price, side, taREST)
       if stop_id != 0:
           # если ордер отправлен удачно - мы в сделке!
           return True
       else:
           inTrade = False
           return False
   elif stop_id == 0:
       # ну просто ждем, когда размер обновится
       r = 1
       return False

   else:
       dump(red(bold('Точно такой же СТОП-ордер уже есть! Не будем создавать ДУБЛЬ!')))
       next_step = 'WAITING_FOR_PROFIT_ORDER'
       inTrade = True
       return False
#--- End of makeStopOrder() ---#

#=================================================
""" Создаем ПРОФИТ-ордер с нужными параметрами """
#=================================================
def makeProfitOrder(size, limit_price, side):
   global profit_id
   global next_step
   global inTrade

   #profit_id = isOrderByParams_WS('Limit', side, size, limit_price)
   #profit_id = isOrderByParams_REST(symbolC, 'Limit', side, size, limit_price, taREST)
   profit_id = 0
   if profit_id == 0 and size != 0:
       # будем создавать новый ПРОФИТ только в том случае, если у нас при этом не возникнут ДУБЛИ!!!
       profit_id = newProfitOrder_REST(symbolC, size, limit_price, side, taREST)
       #profit_id = newLimitOrder_REST(symbolC, size, limit_price, side, taREST)
       if profit_id != 0:
           # если ордер отправлен удачно - мы в сделке!
           return True
       else:
           inTrade = False
           return False
   elif profit_id == 0:
       # ну просто ждем, когда размер обновится
       return False
   else:
       dump(red(bold('Точно такой же ПРОФИТ-ордер уже есть! Не будем создавать ДУБЛЬ!')))
       next_step = 'WAITING_FOR_TRADE_ENDING'
       inTrade = True
       return False
#--- End of makeProfitOrder() ---#

#===================================================
""" Изменяем СТОП ордер под новый размер позиции """
#===================================================
def fixStopOrder(id, sizeS, priceS, limitS, side):
   #dump('Меняем Стоп Ордер: id=', id, ' size=', sizeS, ' price=', priceS, ' limit=', limitS)
   dump('Меняем   СТОП Ордер:', 'size=', green(str(sizeS)), 'price=', green(str(priceS)), 'limit=', green(str(limitS)))
   editOrder_REST(id, symbolC, 'StopLimit', side, priceS, limitS, sizeS, taREST)
   return 1
#--- End of fixStopOrder() ---#

#=====================================================
""" Изменяем ПРОФИТ ордер под новый размер позиции """
#=====================================================
def fixTakeOrder(id, sizeT, priceT, side):
   #dump('Меняем Профит Ордер: id=', id, ' size=', sizeT, ' price=', priceT)
   dump('Меняем ПРОФИТ Ордер:', 'size=', green(str(sizeT)), 'price=', green(str(priceT)))
   editOrder_REST(id, symbolC, 'Limit', side, priceT, priceT, sizeT, taREST)
   return 1
#--- End of fixTakeOrder() ---#

#==============================================================================
""" Проверяем наличие новых ПОЗИЦИЙ и реагируем на их ОТКРЫТИЕ или ЗАКРЫТИЕ """
#==============================================================================
def positionManager():
   global inTrade
   global next_step
   global stop_id
   global profit_id
   global posStarted

   # Мы просто проверяем наличие позиции и если она есть - по ее цене и количеству контрактов
   # выставляем ПРАВИЛЬНЫЙ стоп и профит. Остальное нас не парит вовсе!
   # При выставлении стопа и профита надо ОБЯЗАТЕЛЬНО проверить на ДУБЛИКАТЫ

   #pos = getPositionParameters_WS()
   pos = getPositionParameters_REST(symbolW, taREST)
   isPos = False

   if pos != '' and posStarted == False:
       # мы только что ОБНАРУЖИЛИ открытую позицию
       posStarted = True
       dump(bold(green('Обнаружена ОТКРЫТАЯ позиция!!!')))
       #print('price', pos['pos_price'], ' || side', pos['pos_side'], ' || size', pos['pos_size'], ' || rPnL ', pos['pos_Rpnl'], ' || uPnL ', pos['pos_Upnl'], ' || Mark', pos['pos_Mprice'], ' || Bid', pos['bidPrice'], ' || Mid', pos['midPrice'], ' || Ask', pos['askPrice'],)
       print('price', pos['pos_price'], ' || side', pos['pos_side'], ' || size', pos['pos_size'], ' || rPnL ',  pos['pos_Rpnl'], ' || uPnL ', pos['pos_Upnl'], ' || Mark', pos['pos_Mprice'])
       dump(grey('=*=*=*=*=*=*=*=*=*='))
       #time.sleep(1)
       if platform.system() == 'Darwin':
           os.system('afplay _sounds/3glasses.mp3')
       elif platform.system() == 'Windows':
           playsound.playsound('_sounds/3glasses.mp3', True)
       else:
           sound = 0

       next_step = 'WAITING_FOR_STOP_ORDER'

       # -> Позиция-то у нас точно ЕСТЬ!
       isPos = True

   elif pos != '' and posStarted == True and stop_id != 0 and profit_id != 0:
       # мы сидим в позиции уже не первый поврот нашего круга-цикла
       # и отслеживаем ее возможные изменения
       # Например, сравниваем размер позиции с размерами стопа и профита и если что - фиксим!
       #stopL = checkOrderById_WS(stop_id)
       stopL = checkOrderById_REST(stop_id, symbolC, taREST)
       isExit = False # вышли бы мы уже при прежнем подходе или нет???

       if stopL == '':
           next_step = 'WAITING_FOR_STOP_ORDER'
           isPos = True   # - так будет перевыставляться ордер!
           isExit = True
       else:
           isExit = False

       #takeP = checkOrderById_WS(profit_id)
       takeP = checkOrderById_REST(profit_id, symbolC, taREST)
       if takeP == '':
           next_step = 'WAITING_FOR_PROFIT_ORDER'
           isPos = True   # - так будет перевыставляться ордер!
           isExit = True
       else:
           isExit = False

       if isExit != True:
           sizeP = pos['pos_size']
           sizeS = stopL['order_amount']
           sizeT = takeP['order_amount']

           priceP = pos['pos_price']
           priceS = stopL['order_price']
           priceT = takeP['order_price']

           # чтобы избежать вот таких ошибок
           # bitmex {"error":{"message":"Invalid price tickSize","name":"HTTPError"}}
           # опять используем хитрость вида "умножить на 2, округлить до целого, разделить на 2"
           priceP = round(2 * priceP) / 2
           priceS = round(2 * priceS) / 2
           priceT = round(2 * priceT) / 2

           sideP = pos['pos_side']
           if sideP.upper() == 'BUY':
               # мы вошли в ЛОНГ - значит на закрытие оба ордера должны быть в ШОРТ!
               close_side = 'sell'
               stop_price = priceP - stop
               limitS = stop_price - delta
               profit_price = priceP + profit
           else:
               # мы вошли в ШОРТ - значит на закрытие оба ордера должны быть в ЛОНГ!
               close_side = 'buy'
               stop_price = priceP + stop
               limitS = stop_price + delta
               profit_price = priceP - profit

           # ===
           # Будем менять размеры закрывающих ордеров ТОЛКЬО при увеличении размера позиции!!! НЕ ПРИ ЕЕ УМЕНЬШЕНИИ!!!
           # ===
           #if sizeP == sizeS and limitS == priceS:
           if sizeP <= sizeS:
               s = 1
           else:
               #print('sizeP=',sizeP, ' sizeS=', sizeS, ' || priceP=', priceP, ' priceS=', priceS, ' limitS=', limitS)
               fixStopOrder(stop_id, sizeP, stop_price, limitS, close_side)

           #if sizeP == sizeT and profit_price == priceT:
           if sizeP <= sizeT:
               t = 1
           else:
               #print('sizeP=',sizeP, ' sizeT=', sizeT, ' || priceT=', priceT, ' profit_price=', profit_price)
               fixTakeOrder(profit_id, sizeP, profit_price, close_side)
       else:
           q = 1

       # -> Позиция-то у нас точно ЕСТЬ!
       isPos = True

   elif pos != '' and posStarted == True and (stop_id == 0 or profit_id == 0):
       # Позиция уже обнаружена не первый раз, но почему-то нет стопов или профитов или и того и другого
       # Исправляем!
       next_step = 'WAITING_FOR_STOP_ORDER'

       # -> Позиция-то у нас точно ЕСТЬ!
       isPos = True

   elif pos == '' and posStarted == True:
       # Позиция закрыта - чистим за собой лишние ордера
       #print('Ух как интересно! Мы вот тут пробегаем пред закрытием???')
       dump(grey('=*=*=*=*=*=*=*=*=*='))
       posStarted = False
       inTrade = False
       next_step = 'KILLING_OPPOSIT_ORDER'

       # -> Позиции-то у нас точно НЕТ!
       isPos = False

   else:
       # Позиции просто еще НЕТ никакой!!!
       next_step = 'WAITING_FOR_NEW_POSITION'
       # -> Позиции-то у нас точно НЕТ!
       isPos = False

   # Формируем окончательный ответ
   result = {
       'isPos': isPos,
       'inTrade': inTrade,
       'posStarted': posStarted,
       'next_step': next_step,
       'posInfo': pos,
   }

   return result
#--- End of positionManager() ---#

#==========================================================
""" Убеждаемся в смерти СТОП-ЛОСС и ТЕЙК-ПРОФИТ ордеров """
#==========================================================
def killOppositeOrders():
   global next_step
   global stop_id
   global profit_id

   # разбираемся с ТЕЙК-ПРОФИТОМ
   #order = checkOrderById_WS(profit_id)
   order = checkOrderById_REST(profit_id, symbolC, taREST)
   if order != '':
       # тейк-профит еще есть
       t = 0
   else:
       # тейк-профит уже итак был снят или закрыт
       t = 1

   # разбираемся со СТОПОМ
   #order = checkOrderById_WS(stop_id)
   order = checkOrderById_REST(stop_id, symbolC, taREST)
   if order != '':
       # стоп-лосст еще есть
       s = 0
   else:
       # стоп-лосст уже итак был снят или закрыт
       s = 1

   if t == 1 and s == 0:
       # сделка закрыта по ТЕЙКУ
       killStopLoss_REST(stop_id, taREST)
       #dump(green('Сделка Закрыта по ТЕЙК-ПРОФИТ-ордеру! Поздравляю!'))
       dump(green('Сделка Закрыта!!!'))
       dump('СТОП еще не убран... ',green('Исправляем!!!'))

       if platform.system() == 'Darwin':
           os.system('afplay _sounds/3glasses.mp3')
       elif platform.system() == 'Windows':
           playsound.playsound('_sounds/3glasses.mp3', True)
       else:
           sound = 0

       s = 1

   elif t == 0 and s == 1:
       # сделка закрыта по СТОПУ
       killTakeProfit_REST(profit_id, taREST)
       #dump(green('Сделка Закрыта по СТОП-ордеру! Бывает...'))
       dump(green('Сделка Закрыта!!!'))
       dump('ПРОФИТ еще не убран... ',green('Исправляем!!!'))

       if platform.system() == 'Darwin':
           os.system('afplay _sounds/3glasses.mp3')
       elif platform.system() == 'Windows':
           playsound.playsound('_sounds/3glasses.mp3', True)
       else:
           sound = 0

       t = 1

   elif t == 1 and s == 1:
       # сделка закрыта по ВСТРЕЧНОМУ ОРДЕРУ - ВО ВСЯКОМ СЛУЧАЕ так при ЗАКРЫВАЮЩЕМ ЛИМИТНИКЕ на профите!
       killStopLoss_REST(stop_id, taREST)
       killTakeProfit_REST(profit_id, taREST)
       #dump(red(bold('Сделка Закрыта по ВСТРЕЧНОМУ ордеру!')))
       dump(red(bold('Сделка Закрыта!!!')))
       dump('ПРОФИТ и СТОП еще не убраны... ',green('Исправляем!!!'))

       if platform.system() == 'Darwin':
           os.system('afplay _sounds/3glasses.mp3')
       elif platform.system() == 'Windows':
           playsound.playsound('_sounds/3glasses.mp3', True)
       else:
           sound = 0

   else:
       # а вот тут как раз скорее похоже на выход по встречному при ОБЫЧНОМ ЛИМИТНИКЕ на профите
       killStopLoss_REST(stop_id, taREST)
       killTakeProfit_REST(profit_id, taREST)
       #dump(red(bold('Сделка Закрыта по ВСТРЕЧНОМУ ордеру!')))
       dump(red(bold('Сделка Закрыта!!!')))
       dump('ПРОФИТ и СТОП еще не убраны... ',green('Исправляем!!!'))

       if platform.system() == 'Darwin':
           os.system('afplay _sounds/3glasses.mp3')
       elif platform.system() == 'Windows':
           playsound.playsound('_sounds/3glasses.mp3', True)
       else:
           sound = 0

       t = 1
       s = 1

   if (t+s) == 2:
       if platform.system() == 'Darwin':
           os.system('afplay _sounds/3glasses.mp3')
       elif platform.system() == 'Windows':
           playsound.playsound('_sounds/3glasses.mp3', True)
       else:
           sound = 0

       writeWelcomeMessage()
       next_step = 'WAITING_FOR_NEW_POSITION'
   else:
       next_step = 'KILLING_OPPOSIT_ORDER'

#--- End of killOppositeOrders() ---#

#===========================================================
""" Выводим сообщение о готовности к новому циклу работы """
#===========================================================
def writeWelcomeMessage():
   global next_step
   global posStarted
   global inTrade
   global stop_id
   global profit_id
   global isTestMode

   otb.clear()
   ots.clear()
   co.clear()

   stop_id = 0
   profit_id = 0

   if isTestMode == 1:
       strMode = exchange.name + '-TEST'
   else:
       strMode = exchange.name + '-REAL'
   dump(grey('-----------------------------------------------------------------------------------------'))
   dump(' ',cyan(':'),green('ЖДЁМ'),'появления новой',yellow('ОТКРЫТОЙ ПОЗИЦИИ'),'по инструменту', bold(pink(symbolW)), 'на бирже', bold(red(strMode)),cyan(':'))
   dump(grey('-----------------------------------------------------------------------------------------'))

   inTrade = False
   posStarted = False
   next_step = 'WAITING_FOR_NEW_POSITION'

#--- End of writeWelcomeMessage() ---#

#==========================================================
""" Создаем СТОП и ПРОФИТ ордера и проверяем их наличие """
#==========================================================
def waitStopAndProfitOrders(pos):
   global next_step
   global stop
   global profit
   global delta
   global stop_id
   global profit_id
   global inTrade

   #pos = getPositionParameters_WS()
   if pos == '':
       pos = getPositionParameters_REST(symbolW, taREST)
       if pos == '':
           # если ОТКРЫТОЙ позиции вдруг уже нет (что странно!) - выходим
           return -1

   # если ОТКРЫТАЯ позиция все-таки есть - продолжаем
   sizeP = pos['pos_size']
   priceP = pos['pos_price']

   sideP = pos['pos_side']
   if sideP.upper() == 'BUY':
       # мы вошли в ЛОНГ - значит на закрытие оба ордера должны быть в ШОРТ!
       close_side = 'sell'
       priceS = priceP - stop
       limitS = priceS - delta
       priceT = priceP + profit
   else:
       # мы вошли в ШОРТ - значит на закрытие оба ордера должны быть в ЛОНГ!
       close_side = 'buy'
       priceS = priceP + stop
       limitS = priceS + delta
       priceT = priceP - profit

   # если позиция НЕ пустая - продолжаем!
   s = ordersCheck(stop_id)
   #s = True
   if str(stop_id) == '0' or s == False:
       # Если СТОП еще не создан - создаем
       r = makeStopOrder(sizeP, priceS, limitS, close_side)
       #if inTrade == True and r == True and s == False:
       if r == True and s == False:
           #dump('СТОП-ЛОСС   восстановлен!')
           if platform.system() == 'Darwin':
               os.system('afplay _sounds/purr.mp3')
           elif platform.system() == 'Windows':
               playsound.playsound('_sounds/purr.mp3', True)
           else:
               sound = 0

   else:
       # Если УЖЕ был создан - проверяем наличие
       #isStop = checkOrderById_WS(stop_id)
       isStop = checkOrderById_REST(stop_id, symbolC, taREST)
       if isStop != '':
           # если какой-то ордер нами был найден
           if isStop['order_type'].upper() == 'STOPLIMIT':
               order_price = isStop['order_price']
               order_amount = isStop['order_amount']
               if next_step == 'WAITING_FOR_STOP_ORDER':
                   dump('СТОП-ЛОСС   подтверждён!',red(order_type),'Ордер выставлен по цене',bold(yellow(str(order_price))), 'на', bold(red(str(order_amount))), 'контрактов')

                   if platform.system() == 'Darwin':
                       os.system('afplay _sounds/purr.mp3')
                   elif platform.system() == 'Windows':
                       playsound.playsound('_sounds/purr.mp3', True)
                   else:
                       sound = 0

                   #inTrade = True
               next_step = 'WAITING_FOR_PROFIT_ORDER'
               #time.sleep(1)
           else:
               dump(red('waitStopOrder:'), yellow('Что-то не так!'))
               makeStopOrder(sizeP, priceS, limitS, close_side)
       else:
           # видимо, еще не успели создать по причине тормозов на бирже
           stop_id = 0
           next_step = 'WAITING_FOR_STOP_ORDER'
           s = 1

   p = ordersCheck(profit_id)
   #p = True
   if str(profit_id) == '0' or p == False:
       # Если СТОП еще не создан - создаем
       r = makeProfitOrder(sizeP, priceT, close_side)
       #if inTrade == True and r == True and p == False:
       if r == True and p == False:
           #dump('ТЕЙК-ПРОФИТ восстановлен!')
           if platform.system() == 'Darwin':
               os.system('afplay _sounds/purr.mp3')
           elif platform.system() == 'Windows':
               playsound.playsound('_sounds/purr.mp3', True)
           else:
               sound = 0


   else:
       # Если УЖЕ был создан - проверяем наличие
       #isProfit = checkOrderById_WS(profit_id)
       isProfit = checkOrderById_REST(profit_id, symbolC, taREST)
       if isProfit != '':
           # если какой-то ордер нами был найден
           if isProfit['order_type'].upper() == 'LIMIT':
               order_price = isProfit['order_price']
               order_amount = isProfit['order_amount']
               #if next_step == 'WAITING_FOR_PROFIT_ORDER':
               dump('ТЕЙК-ПРОФИТ подтверждён!',green(order_type),'Ордер выставлен по цене',bold(yellow(str(order_price))), 'на', bold(green(str(order_amount))), 'контрактов')

               if platform.system() == 'Darwin':
                   os.system('afplay _sounds/purr.mp3')
               elif platform.system() == 'Windows':
                   playsound.playsound('_sounds/purr.mp3', True)
               else:
                   sound = 0

               inTrade = True
               next_step = 'WAITING_FOR_TRADE_ENDING'
               #time.sleep(1)

           else:
               dump(red('waitProfitOrder:'), yellow('Что-то не так!'))
               makeProfitOrder(sizeP, priceT, close_side)
       else:
           # видимо, еще не успели создать по причине тормозов на бирже
           next_step = 'WAITING_FOR_PROFIT_ORDER'
           s = 1

   #time.sleep(taREST)
#--- End of waitStopAndProfitOrders() ---#

#==========================================================
""" ЗАГЛУШКА: типа ожидаем окончания сделки             """
#==========================================================
def waitTradeEnd():
    return 1
#--- End of waitTradeEnd() ---#