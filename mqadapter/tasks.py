# -*- coding: utf-8 -*-
"""
Объявления задач celery
@author: V-Liderman
"""
import os
from .celery import app
__BASE_DIR = os.path.join(os.path.dirname(__file__), '..')

@app.task
def test():
    '''Загрушка'''
    return False
