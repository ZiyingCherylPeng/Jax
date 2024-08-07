

import urllib.parse
import os

os.environ['DBHOST'] = 'ex1-pg-vectordb.postgres.database.azure.com'
os.environ['DBNAME'] = 'postgres'
os.environ['DBUSER'] = 'ex1pgadmin'
os.environ['SSLMODE'] = 'require'
os.environ['DBPASSWORD'] = '523799pzy.SFU'
def get_connection_uri():

    # Read URI parameters from the environment
    dbhost = os.environ['DBHOST']
    dbname = os.environ['DBNAME']
    dbuser = urllib.parse.quote(os.environ['DBUSER'])
    password = os.environ['DBPASSWORD']
    sslmode = os.environ['SSLMODE']

    # Construct connection URI
    db_uri = f"postgresql://{dbuser}:{password}@{dbhost}/{dbname}?sslmode={sslmode}"
    return db_uri

# print("the url:", get_connection_uri())
