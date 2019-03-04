# -*- coding: utf-8 -*-
"""
Created on Sun Feb 17 17:04:53 2019

@author: V-Liderman
"""

from sqlalchemy.engine import create_engine
from sqlalchemy.schema import MetaData

from shell.codegen import CodeGenerator
from collections import defaultdict
#import pickle
#import os

schema = None
tables=list()
#ignore views
noviews = True
#ignore indexes
noindexes = True
noconstraints = False
#don't try to convert tables names to singular form
noinflect = True
#don't generate classes, only tables
noclasses = False
#don't autodetect joined table inheritance
nojoined = False

url = r'mssql+pyodbc://v-liderman\sql2017/omnius?driver=ODBC+Driver+13+for+SQL+Server'

engine = create_engine(url)

ep_sql = '''
SELECT o.type, S.name as [schema], O.name AS [object], c.name [column], 
    convert(varchar(255),ep.name) name, convert(varchar(1024),ep.value) value
FROM sys.extended_properties EP
INNER JOIN sys.all_objects O ON ep.major_id = O.object_id 
INNER JOIN sys.schemas S on O.schema_id = S.schema_id
LEFT JOIN sys.columns AS c ON ep.major_id = c.object_id AND ep.minor_id = c.column_id
where o.type in ('U', 'V')
order by 1,2,3,4,5
'''
ep_cache = defaultdict(dict)
for prop in engine.execute(ep_sql):
    ep_cache[prop.schema][(prop.object, prop.column, prop.name)] = prop.value


ep_tables = {sch:{obj[0] for obj in ep_cache[sch].keys() if obj[2].lower()=='xmeta.user.module'} \
             for sch in ep_cache.keys() }

metadata = MetaData(engine)
tables = tables or None

#file_name = os.path.join(os.path.dirname(__file__), 'metadata.pickle')
#try:
#    with open(file_name, 'rb') as file:
#        metadata = pickle.load(file)
#except:
for schema in ep_tables.keys():
    tables = list(ep_tables[schema])
    if not tables: continue
    metadata.reflect(engine, schema, not noviews, tables)

generator = CodeGenerator(metadata, noindexes, noconstraints, nojoined, noinflect, noclasses)

with open(r'__init__.py', 'w', encoding='utf-8') as fout:
    # Write the generated model code to the specified file or standard output
    generator.render(fout)
    


