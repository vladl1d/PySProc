# -*- coding: utf-8 -*-
"""
Конструкторы соединения для БД
@author: V-Liderman
"""
import threading
import time
from .types import t_dict

class Odbc:
    '''Простая работа с БД напрямую'''
    def __init__(self, dsn, module, debug=True):
        #строка соединения
        self._dsn = dsn
        #модуль для работы с БД
        import pyodbc
        self._module = module or pyodbc
        #эмуляция сессии
        self.session = self._module.connect(self._dsn)
        #отладка
        self.debug = debug
    def __del__(self):
        '''
        Стандартный деструктор
        '''
        if hasattr(self, 'session') and self.session:
            try:
                self.session.close()
            except:
                pass

class OdbcMT:
    '''Простая работа с БД напрямую с поддержкой многопоточности'''
    def __init__(self, dsn, module, debug=True):
        #строка соединения
        self._dsn = dsn
        #модуль для работы с БД
        import pyodbc
        self._module = module or pyodbc
        # кеш открытых соединений с БД
        self.connections = t_dict()
        #timeout ожидания запроса
        self.wait_timeout = 5
        #отладка
        self.debug = debug

    ############################## Работа с соедиенениями. Каждый data_id в своем соединении
    def new_db_job(self, job_id=None):
        '''Открывает соединение с БД для выполнения операций. Поддерживает мультипоточность'''
        if not job_id:
            job_id = len(self.connections.keys()) + 1
        thrd_id = threading.current_thread().ident
        job_id += '_' + str(thrd_id)
        conn = self.connections.get(job_id, None)
        i = 0
        while conn and i < self.wait_timeout/0.05:
            time.sleep(0.05)
            conn = self.connections.get(job_id, None)
        conn = self._module.connect(self._dsn)
#       conn.autocommit = True
        self.connections[job_id] = conn
        print('Новый запрос:', job_id)
        return job_id

    def execute(self, job_id, sql, params):
        '''выполнение запроса'''
        if not job_id or not self.connections.get(job_id, None):
            job_id = self.new_db_job()
        return self.connections[job_id](sql, params)

    def _finish_db_job(self, tran_func='commit', job_id=None):
        '''Закрывает операцию. Если не задан id операции закрывает все'''
        def _close_conn(conn, tran_func):
            try:
                getattr(conn, tran_func, lambda: True)()
                conn.close()
            except Exception as error:
                print('Не смогли закрыть: %s' % job_id, str(error))

        if job_id:
            thrd_id = threading.current_thread().ident
            job_id += '_' + str(thrd_id)
            if job_id in self.connections:
                _close_conn(self.connections[job_id], tran_func)
                self.connections.pop(job_id)
                print('Закрыли запрос:', job_id)
        else:
            for job_id in self.connections:
                _close_conn(self.connections[job_id], tran_func)

    def commit_db_job(self, job_id=None):
        '''Закрывает операцию с применением результата'''
        self._finish_db_job(tran_func='commit', job_id=job_id)
    def rollback_db_job(self, job_id=None):
        '''Закрывает операцию с отменой результата'''
        self._finish_db_job(tran_func='rollback', job_id=job_id)

    def __del__(self):
        '''
        Стандартный деструктор
        '''
        if hasattr(self, 'connections') and self.connections:
            try:
                self._finish_db_job()
            except:
                pass

class SqlAlchemy:
    '''Инициализация работы с БД через SQL Alchemy'''
    def __init__(self, dsn, module=None, debug=True):
        #строка соединения
        self._dsn = dsn
        #модуль для работы с БД
        from sqlalchemy import create_engine
        self._module = create_engine(dsn, echo=debug)
        from sqlalchemy.orm import sessionmaker
        #создаем сессию для выполнения
        self.session = sessionmaker(bind=self._module)()
        #отладка
        self.debug = debug
    def __del__(self):
        '''
        Стандартный деструктор
        '''
        if hasattr(self, '_module') and self._module:
            try:
                del self._module
            except:
                pass
