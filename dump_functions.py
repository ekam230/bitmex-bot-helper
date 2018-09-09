#!/usr/bin/env python3
#--------------------#
# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import platform

# ================================================================== #
# Тут ниже еще несколько функций для красоты выводимой информации
# ================================================================== #

# Grey = '\033[90m'
# Red = '\033[91m'
# Green = '\033[92m'
# Yellow = '\033[93m'
# Blue = '\033[94m'
# Magenta = '\033[95m'
# Cyan = '\033[96m'
# White = '\033[97m'
# Black = '\033[90m'
# Default = '\033[99m'

#=================================================
def style(s, style):
    if platform.system() == 'Darwin':
        return style + s + '\033[0m'
    elif platform.system() == 'Windows':
        return s
    else:
        return s
#------
def grey(s):
    return style(s, '\033[90m')
def red(s):
    return style(s, '\033[91m')
def green(s):
    return style(s, '\033[92m')
def yellow(s):
    return style(s, '\033[93m')
def blue(s):
    return style(s, '\033[94m')
def pink(s):
    return style(s, '\033[95m')
def magenta(s):
    return style(s, '\033[95m') # same as pink
def cyan(s):
    return style(s, '\033[96m')
def white(s):
    return style(s, '\033[97m')
def default(s):
    return style(s, '\033[99m')

#------
def bold(s):
    return style(s, '\033[1m')
def underline(s):
    return style(s, '\033[4m')
#------
def dump(*args):
    print(' '.join([str(arg) for arg in args]))
#=================================================

#dump(cyan('color') + ' test'),
#os.system('afplay /System/Library/Sounds/Ping.aiff')
#os.system('afplay _sounds/glass.aiff')
#os.system('afplay _sounds/glass2.wav')
#os.system('afplay _sounds/3glasses.mp3')
