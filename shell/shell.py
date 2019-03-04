# -*- coding: utf-8 -*-
"""
Абстрактное ядро воркера.
@author: V-Liderman
"""
import os
import logging
import importlib

from configparser import ConfigParser

__RUN_DIR__ = os.path.dirname(__file__)

class ProcShell:
    '''Абстрактное ядро воркера'''
    def __init__(self, db_driver, ini_file='config.ini', base_dir=None, debug=False):
        #конфигурация
        self._config = None
        # рабочая директория
        self.base_dir = base_dir if base_dir else __RUN_DIR__
        #логгер
        self.log = None
#        self._log_queue = queue.Queue()
        self._log_handler = None
        #адаптер к данным
        self.data_adapter = None
        #отладка
        self.debug = debug

        assert ini_file, 'Название конфигурационного файла должно быть задано'
        #чтение ini-файла
        self._read_ini_file(ini_file)
        # запуск системы логирования
        self._init_log_system()
        # соединение с БД
        self._init_db_adapter(db_driver)


############### Ini-file #######################
    def cfg_get(self, section, key, default=None, init=None, assert_key=False):
        '''получение настройки из файла'''
        assert self._config, 'Не инициированы настройки'
        assert section and key, 'Неверные параметры'
        #assert cfg_section, 'Конфигурационный файл не содержит секции' + section
        value = self._config.get(section, key, fallback=default)
        assert not assert_key or value is not None, 'В ini-файле в секции %s на найден ключ %s' % \
                                            (section, key)
        if init:
            if init == bool:
                init = (lambda x: int(x) != 0 if x.isnumeric() else bool(x))
            value = init(value)
        return value

    def _read_ini_file(self, ini_file):
        ''' Инициализация среды исполнения программы'''
        config = ConfigParser()
        path = os.path.join(self.base_dir, ini_file)
        try:
            config.read(path)
        except:
            print('Ошибка чтения ini-файла')
            return
        else:
            self._config = config

        if 'GLOBALS' in config.sections():
            for key in config['GLOBALS']:
                globals()[key] = config['GLOBALS'][key]
                setattr(self, key, config['GLOBALS'][key])

############### Logger #######################
    def _init_log_system(self):
        '''Инициализация среды исполнения'''
        log_name = self.cfg_get('Logging', 'LogName', assert_key=True)
        log_path = self.cfg_get('Logging', 'LogPath', default='./__Log__', assert_key=False)
        log_level = self.cfg_get('Logging', 'LogLevel', default=0, assert_key=False)
        log_path = os.path.join(self.base_dir, log_path, log_name+'.log')
#        rec_log = self.log.getChild('data')
        #настройка системы логирования
        _format = '%(asctime)s;%(levelname)s;%(message)s;%(filename)s;%(funcName)s'
#        file_handler = logging.handlers.TimedRotatingFileHandler('OmniX_CR', when='midnight', \
#                                                                 backupCount=365, encoding='utf-8')
        logging.root.handlers.clear()
        logging.basicConfig(filename=log_path, datefmt='%Y.%m.%d %H:%M:%S', style='%', \
                            format=_format, level=log_level)

        self.log = logging.getLogger(log_name)
        #настройка системы ассинхронного логирования на сервер
#        self.log_data_id = self.cfg_get('Logging', 'LogDataID', assert_key=False)
#        if self.log_data_id:
#            queue_handler = logging.handlers.QueueHandler(self._log_queue)
#            self.log.addHandler(queue_handler)
#            log_handler = ShellLogHandler(self._data_adapter.push_record, \
#                                          data_id=self.log_data_id, \
#                                          param_values=self.context_param_values)
#            self._log_handler = logging.handlers.QueueListener(self._log_queue, log_handler)

        self.log.info('===========================================================')
        self.log.info('Старт системы логирования. Уровень логирования: %s', log_level)

############### Data Adapter #######################
    def _init_db_adapter(self, db_driver):
        '''Инициализация адаптера к БД и потокового чтения json-файлов'''

        #драйвер
        driver = self.cfg_get('DataAdapter', 'Driver', default='pyodbc', assert_key=False)
        module = importlib.import_module(driver)
        # источник данных
        dsn = self.cfg_get('DataAdapter', 'DSN', assert_key=True)
        # Диалект SQL
#        sql_lang = self.cfg_get('DataAdapter', 'Dialect', assert_key=False)
        #инициализация адаптера
        self.data_adapter = db_driver(dsn, module, debug=self.debug)
        #кодировка
        self.encoding = self.cfg_get('DataAdapter', 'Encoding', default='utf-8', assert_key=True)
        self.log.info('Адаптер успешно проиницализирован')

    def stop(self):
        '''Остановка оболочки'''
        if hasattr(self, 'log') and hasattr(self.log, 'info'):
            self.log.info('Остановка ноды')

        if hasattr(self, '_log_handler') and  hasattr(self._log_handler, 'stop'):
            self._log_handler.stop()

    def __del__(self):
        self.stop()
