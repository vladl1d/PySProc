#TODO: доработать поддержку extended props -> sqlacodegen
#sqlacodegen --noviews --outfile __init__.py mssql+pyodbc://v-liderman\sql2017/omnius?driver=ODBC+Driver+13+for+SQL+Server
#sqlautocode -o model.py -u mssql+pyodbc://v-liderman\sql2017/omnius?driver=ODBC+Driver+13+for+SQL+Server
python -m _generator.py