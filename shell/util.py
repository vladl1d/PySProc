# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 19:22:37 2018

@author: V-Liderman
"""
import json
#import re
from datetime import datetime#, timedelta, timezone
from uuid import UUID
# C parser
from ciso8601 import parse_datetime

def get_typed_value(value, _type):
    '''Получение типизированного значения из строки'''
    if _type == int:
        return int(value)
    elif _type == float:
        return float(value)
    elif _type == bool:
        return value == True
    elif _type == UUID:
        return UUID(value)
    elif _type == datetime:
        if isinstance(value, str):
            #return quick_datetime_iso_parser(value)
            return parse_datetime(value)
        elif isinstance(value, bytes):
            #return quick_datetime_iso_parser(value.decode())
            return parse_datetime(value.decode())
        elif isinstance(value, datetime):
            return value
        elif isinstance(value, float):
            return datetime.fromtimestamp(value)
        elif isinstance(value, int):
            return datetime.fromordinal(value)
        else:
            raise TypeError('Неизвестный формат времени')
    else:
        return str(value)

class CustomEncoder(json.JSONEncoder):
    '''Helper Для сериализации составных типов'''
    def default(self, value):
        #обработка дополнительных типов
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, UUID):
            return str(value)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, value)
