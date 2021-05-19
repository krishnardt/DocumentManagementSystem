import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT # <-- ADD THIS LINE

# con = psycopg2.connect(dbname='postgres',
#       user=self.user_name, host='',
#       password=self.password)



con = psycopg2.connect(
   database="postgres", user='root', password='root', host='127.0.0.1', port= '5432'
)
con.autocommit = True
print('Database connected.')


cur = con.cursor()

cur.execute("SELECT datname FROM pg_database;")

list_database = cur.fetchall()

database_name = "doc_service2"

if (database_name,) in list_database:
    print("'{}' Database already exist".format(database_name))
else:
    print("'{}' Database not exist.".format(database_name))
    sql = '''CREATE database mydb''';
    cur.execute(sql)
    print("Database created successfully........")
con.close()
print('Done')

