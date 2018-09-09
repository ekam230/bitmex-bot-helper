#!/usr/bin/env python3
#--------------------#
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
from global_variables import *
from dump_functions import *

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')


"""================================================================="""
""" Подключаем нужную нам биржу - тут БИТМЕКС - через CCXT          """
"""================================================================="""
# Подключаем мульти-криптовалютно-биржевую библиотеку CCXT
import ccxt
import settings as config


exchange = ccxt.bitmex({
        'apiKey': config.api_key,
        'secret': config.api_secret,
        #'enableRateLimit': False,  # эта опция обеспечивает соблюдение лимитов API на количество вызовов в определенное время
        #'enableRateLimit': True,  # эта опция обеспечивает соблюдение лимитов API на количество вызовов в определенное время
        'enableRateLimit': (config.toRest == 0) # пробуем на автомате отловить: если задан таймаут НОЛЬ - включаем опцию РейтЛимит, а если НЕ НОЛЬ - отключаем
})

#exchange.urls['api'] = exchange.urls['test'] #'https://testnet.bitmex.com/api/v1/'  # используем TestNet !!!
#exchange.urls['api'] = 'https://www.bitmex.com/api/v1/'  # используем REAL !!!
exchange.urls['api'] = config.EndpCCXT # используем "автопереключалку" между РЕАЛОМ или ТЕСТНЕТОМ в конфиге!!!

#print('RateLimit:', exchange.enableRateLimit)
#print('taREST: ', config.toRest)

"""================================================================="""
""" Закрываем ЛЮБУЮ ПОЗИЦИЮ просто по маркету                       """
"""================================================================="""
def closePositionByMarket_REST(symbol, timeout):
   # Нет конкретной команды на ЗАКРЫТИЕ позиции. Просто вызываем МАРКЕТ-ордер противоположного к позиции направления
   #pos = getPositionParameters_WS()
   pos = getPositionParameters_REST(symbol, timeout)
   if pos != '':
       # у нас есть-таки что закрывать
       if pos['order_side'].upper() == 'BUY':
           newMarketOrder_REST(symbol, pos['order_amount'], 'sell', timeout)
       else:
           newMarketOrder_REST(symbol, pos['order_amount'], 'buy', timeout)
   else:
       # закрывать-то и нечего!!!
       print('Ложный вызов! Нельзя закрыть позицию, если ее НЕТ!')
#--- End of closePositionByMarket_REST() ---#

"""================================================================="""
""" Создаем ЛЮБОЙ МАРКЕТ-ордер                                      """
"""================================================================="""
def newMarketOrder_REST(symbol, size, side, timeout):
  params = {}
  try:
      if side.upper() == 'BUY':
          result = exchange.createMarketBuyOrder (symbol, size, params)
      else:
          result = exchange.createMarketSellOrder (symbol, size, params)
      # вместо стандартной паузы из библиотеки CCXT
      time.sleep(timeout)
      return result['id']
  except ccxt.ExchangeError as e:
      print('----------')
      print('newMarketOrder_REST():',e)
      print('size:', size, ' || side: ', side)
      print('----------')

  #time.sleep(taREST) # делаем принудительно паузу (заданную в настройках), так как системная переменная EnableRateLimit у нас выключена!!!
  return 0
#--- End of newMarketOrder_REST() ---#

"""================================================================="""
""" Создаем ЛЮБОЙ СТОП-ордер, не обязательно для стоп-лосса         """
"""================================================================="""
def newStopOrder_REST(symbol, size, stop_price, limit_price, side, timeout):
    # чтобы избежать вот таких ошибок
    # bitmex {"error":{"message":"Invalid price tickSize","name":"HTTPError"}}
    # опять используем хитрость вида "умножить на 2, округлить до целого, разделить на 2"
    stop_price = round(2 * stop_price) / 2
    limit_price = round(2 * limit_price) / 2
    try:
        result = exchange.createOrder(symbol, 'StopLimit', side, size, limit_price, { 'stopPx': stop_price, 'price': limit_price, 'execInst': 'Close,LastPrice' }) # для БИТМЕКСА точно  работает!!!
        time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!
        return result['id']
    except ccxt.ExchangeError as e:
        print('----------')
        print('newStopOrder_REST():',e)
        print('size:', size, ' || stop:', stop_price, ' || limit:', limit_price, ' || side: ', side)
        print('----------')
    return 0
#--- End of newStopOrder() ---#

"""================================================================="""
""" Создаем ТЕЙК-ПРОФИТ-ордер                                       """
"""================================================================="""
def newProfitOrder_REST(symbol, size, limit_price, side, timeout):
   # чтобы избежать вот таких ошибок
   # bitmex {"error":{"message":"Invalid price tickSize","name":"HTTPError"}}
   # опять используем хитрость вида "умножить на 2, округлить до целого, разделить на 2"
   limit_price = round(2 * limit_price) / 2
   try:
       result = exchange.createOrder(symbol, 'Limit', side, size, limit_price, { 'price': limit_price, 'execInst': 'Close' }) # для БИТМЕКСА точно  работает!!!
       time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!
       return result['id']
   except ccxt.ExchangeError as e:
       print('----------')
       print('newProfitOrder_REST():',e)
       print('size:', size, ' || limit:', limit_price, ' || side: ', side)
       print('----------')
   return 0
#--- End of newLimitOrder() ---#

"""================================================================="""
""" Создаем ЛЮБОЙ ЛИМИТНЫЙ ордер                                    """
"""================================================================="""
def newLimitOrder_REST(symbol, size, limit_price, side, timeout):
  # чтобы избежать вот таких ошибок
  # bitmex {"error":{"message":"Invalid price tickSize","name":"HTTPError"}}
  # опять используем хитрость вида "умножить на 2, округлить до целого, разделить на 2"
  limit_price = round(2 * limit_price) / 2
  try:
      result = exchange.createOrder(symbol, 'Limit', side, size, limit_price, { 'price': limit_price }) # для БИТМЕКСА точно  работает!!!
      time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!
      return result['id']
  except ccxt.ExchangeError as e:
      print('----------')
      print('newLimitOrder_REST():',e)
      print('size:', size, ' || limit:', limit_price, ' || side: ', side)
      print('----------')
  return 0
#--- End of newLimitOrder() ---#

"""================================================================="""
""" Убиваем СТОП-ЛОСС ордер                                         """
"""================================================================="""
def killStopLoss_REST(stop_id, timeout):
 try:
     exchange.cancel_order(stop_id)
     time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!
 except ccxt.ExchangeError as e:
     #print(e)
     s=1

#--- End of killStopLoss() ---#

"""================================================================="""
""" Убиваем ТЕЙК-ПРОФИТ ордер                                       """
"""================================================================="""
def killTakeProfit_REST(profit_id, timeout):
 try:
     exchange.cancel_order(profit_id)
     time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!
 except ccxt.ExchangeError as e:
     #print(e)
     s=1

#--- End of killTakeProfit_REST() ---#

"""================================================================="""
""" Изменяем ЛЮБОЙ ордер                                            """
"""================================================================="""
def editOrder_REST(id, symbol, type, side, newprice, newlimitprice, newsize, timeout):
 params = {}
 # чтобы избежать вот таких ошибок
 # bitmex {"error":{"message":"Invalid price tickSize","name":"HTTPError"}}
 # опять используем хитрость вида "умножить на 2, округлить до целого, разделить на 2"
 newprice = round(2 * newprice) / 2
 newlimitprice = round(2 * newlimitprice) / 2
 try:
     if type == 'StopLimit':
         params = { 'stopPx': newprice, 'price': newlimitprice, 'execInst': 'Close,LastPrice' }
         #exchange.edit_order(id, symbol, type, side, amount=newsize, price=newlimitprice, params)
         exchange.edit_order(id, symbol, type, side, newsize, newlimitprice, params)
     else:
         exchange.edit_order(id, symbol, type, side, newsize, newprice, params)
     time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!
 except ccxt.ExchangeError as e:
     #print(e)
     s=1

#--- End of editOrder_REST() ---#

"""================================================================="""
""" Получаем ВСЕ доступные ордера                                   """
"""================================================================="""
def getAllOrders_REST(symbol, timeout):

    if (exchange.has['fetchOrders']):
        orders = exchange.fetchOrders(symbol, params={})
        time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!

    num = len(orders)
    if num > 0:
        return orders
    else:
        return ''
#--- End of getOrders_REST() ---#

"""================================================================="""
""" Получаем все доступные ОТКРЫТЫЕ ордера                          """
"""================================================================="""
def getOpenOrders_REST(symbol, timeout):

    if (exchange.has['fetchOpenOrders']):
        orders = exchange.fetchOpenOrders(symbol, params={})
        time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!

    num = len(orders)
    if num > 0:
        return orders
    else:
        return ''
#--- End of getOrders_REST() ---#

"""================================================================="""
""" Получаем все доступные ЗАКРЫТЫЕ ордера                          """
"""================================================================="""
def getClosedOrders_REST(symbol, timeout):

    if (exchange.has['fetchClosedOrders']):
        orders = exchange.fetchClosedOrders(symbol, params={})
        time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!

    num = len(orders)
    if num > 0:
        return orders
    else:
        return ''
#--- End of getOrders_REST() ---#

"""============================================================================"""
""" Проверяем само СУЩЕСТВОВАНИЕ ордера с заданными параметрами среди ОТКРЫТЫХ """
"""============================================================================"""
def isOrderByParams_REST(symbol, type, side, size, price, timeout):

    orders = getOpenOrders_REST(symbol, timeout)
    num = len(orders)
    for i in range(0, num):
        #print(str(order))
        order_id = orders[i]['id']
        order_status = orders[i]['status']
        order_price = orders[i]['price']
        order_amount = orders[i]['amount']
        order_type = orders[i]['type']
        order_side = orders[i]['side'].upper()

        if order_type == type and order_side == side.upper() and order_amount == size and order_price == price and orders[i]['ordStatus'].upper() == 'NEW':
            return order_id # то есть НАШЛИ подходящий ордер с нужными параметрами и при этом еще НЕ закрытый!!! - Возвращаем его АЙДИ

    # Очевидно, не нашли нужного нам ордера...
    return 0
#--- End of isOrderById_WS() ---#


"""====================================================================="""
""" Получаем все данные об ОРДЕРЕ с заданным ID (если он есть, конечно) """
"""====================================================================="""
def checkOrderById_REST(id, symbol, timeout):

    orders = getOpenOrders_REST(symbol, timeout)
    num = len(orders)
    for i in range(0, num):
        if orders[i]['id'] == id: #and orders[i]['ordStatus'].upper() == 'NEW':
            order = orders[i]
            result = {
                'order_id': order['id'],
                'order_status': order['status'],
                'order_price': order['price'],
                'order_amount': order['amount'],
                'order_type': order['type'],
                'order_side': order['side'].upper(),
                'order_filled': order['filled'],
                'order_remaining': order['remaining']
            }
            # Вроде бы нашли нужный нам ордер...
            return result

    # Очевидно, что не нашли нужного нам ордера...
    return ''
#--- End of checkOrderById_REST() ---#

"""================================================================="""
""" Получаем НУЖНЫЕ НАМ параметры по текущей позиции                """
"""================================================================="""
def getPositionParameters_REST(symbol, timeout):
    positions = exchange.private_get_position({
        'filter': json.dumps({
            "isOpen": True,
            "symbol": symbol
        }),
        'columns': 'symbol,isOpen,execBuyQty,execSellQty,currentQty,realisedPnl,unrealisedPnl,lastPrice,avgEntryPrice,marginCallPrice,liquidationPrice,markPrice'
    })
    time.sleep(timeout) # делаем принудительно паузу (заданную в настройках), если системная переменная EnableRateLimit у нас выключена!!!
    # dump(grey('=*=*=*=*=*=*=*=*=*='))
    # print(symbol)
    # print(positions)
    # dump(grey('=*=*=*=*=*=*=*=*=*='))
    # return ''
    #
    num = len(positions)
    if num > 0:
        pos = positions[0]
        #inst = ws.get_instrument()

        if pos['currentQty'] > 0:
            pos_size  = pos['currentQty']
            pos_side = 'BUY'
        else:
            pos_size  = 0 - pos['currentQty']
            pos_side = 'SELL'

        result = {
            'pos_status':   'FILLED',
            'pos_price':    pos['avgEntryPrice'],
            'pos_size':     pos_size,
            'pos_side':     pos_side,
            'pos_Upnl':     pos['unrealisedPnl'],
            'pos_Rpnl':     pos['realisedPnl'],
            'pos_idxPrice':   pos['lastPrice'],
            'pos_Mprice':   pos['markPrice'],
            # 'bidPrice':     inst['bidPrice'],
            # 'midPrice':     inst['midPrice'],
            # 'askPrice':     inst['askPrice'],
            'bidPrice':     'NA',
            'midPrice':     'NA',
            'askPrice':     'NA',
        }

        return result

    else:
        m=1
        return ''
#--- End of getPositionParameters_REST() ---#