#!/usr/bin/env python3
# --------------------#
# -*- coding: utf-8 -*-

import configparser
import codecs
import os

config_path = "_config.ini"
if not os.path.exists(config_path):
    # Если конфиг-файла нет - создаем пустой, надо будет его заполнить потом!
    createConfig(config_path)

config = configparser.ConfigParser()
config.read_file(codecs.open(config_path, "r", "utf-8" ))
#config.read(config_path)

# Читаем значения из конфигурационного файла.
symbolW  = config.get("Instrument", "symbolw")
symbolC  = config.get("Instrument", "symbolc")

TestMode = int(config.get("API", "testmode"))

profit   = float(config.get("RiskProfit", "profit"))
stop     = float(config.get("RiskProfit", "stop"))
delta    = float(config.get("RiskProfit", "delta"))
leverage = float(config.get("RiskProfit", "leverage"))
toWs     = float(config.get("TimeOuts", "toWS"))
toRest   = float(config.get("TimeOuts", "toREST"))

# А вот ЭТО лучше не трогать!!!
if TestMode == 1 or TestMode == "1":
    EndP = "https://testnet.bitmex.com/api/v1"  # используем TestNet через WebSocket API!!!
    EndpCCXT = "https://testnet.bitmex.com"  # используем TestNet через REST API и CCXT!!!
    api_key = config.get("API", "api_test_key")
    api_secret = config.get("API", "api_test_secret")
else:
    EndP = "https://www.bitmex.com/api/v1"  # используем Real через WebSocket API!!!
    EndpCCXT = "https://www.bitmex.com"  # используем Real через REST API и CCXT!!!
    api_key = config.get("API", "api_real_key")
    api_secret = config.get("API", "api_real_secret")
