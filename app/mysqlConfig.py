import mysql.connector
import mysql.connector.pooling

dbconfig = {
    "user": "root", 
    "password": "ji3cl31;4", 
    "host": "127.0.0.1", 
    "database": "taipei_day_trip",
    "charset": "utf8"
}

conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name = "mypool",
                            pool_size = 5,
                            **dbconfig)

