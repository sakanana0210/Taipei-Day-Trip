import mysql.connector
import mysql.connector.pooling
import os
from dotenv import load_dotenv
load_dotenv()

dbconfig = {
    "user": os.getenv("DB_USER"), 
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"), 
    "database": os.getenv("DB_DATABASE"),
    "charset": "utf8"
}

conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "mypool",
                            pool_size = 5,
                            **dbconfig)

