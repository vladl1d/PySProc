# -*- coding: utf-8 -*-
"""
Объявление приложения Celery
@author: V-Liderman
"""
from celery import Celery

app = Celery('pyproc',
             broker='pyamqp://',
             backend='rpc://',
             include=['mqadapter.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()

