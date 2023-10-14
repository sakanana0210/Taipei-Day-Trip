from flask import *
from app import mysqlConfig,jwt
import mysql
import mysql.connector
dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
verify_jwt = jwt.verify_jwt
user_orders_bp = Blueprint("user_orders", __name__)

@user_orders_bp.route("/user_orders", methods=["GET"])
def user_orders():
    try:
        cnx = conn_pool.get_connection()
        cursor = cnx.cursor()
        token = request.headers.get("Authorization")
        user_info = verify_jwt(token.split(" ")[1])
        user_info_dict = json.loads(user_info.decode("utf-8"))
        if user_info_dict["data"] is None:
            error_message = "未登入系統，拒絕存取"
            new_data = {"error": True, "message": error_message}
            json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
            response = Response(json_data, status=403, content_type="application/json; charset=utf-8")
            return response
        user_id = user_info_dict["data"]["id"]
        query = """SELECT orders.order_number, DATE_FORMAT(orders.created_at, "%Y-%m-%d") as order_time, 
        attractions.name AS attraction_name,orders.date AS date, orders.time AS time, orders.price, 
        orders.pay_status AS status FROM attractions JOIN orders ON attractions.id = orders.attraction_id 
        WHERE orders.user_id = %s ORDER BY order_time DESC;"""
        cursor.execute(query,(user_id, ))
        results = cursor.fetchall()
        if not results:
            raise mysql.connector.Error
        data = []
        for result in results:
            order_number = result[0]
            order_day_time = result[1]
            attraction_name = result[2]
            schedule_date = result[3]
            formatted_schedule_date = schedule_date.strftime("%Y-%m-%d")
            schedule_time = result[4]
            order_price = result[5]
            order_status = result[6]
            entry = {
				"number": order_number,
				"order_time": order_day_time,
				"attraction_name": attraction_name,
				"schedule_date": formatted_schedule_date,
				"schedule_time": schedule_time,
				"price": order_price,
				"status": order_status
			}
            data.append(entry)
        new_data = {"data" : data}

        json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
        response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
        return response
    
    except mysql.connector.Error as err:
        new_data = {"data" : None}
        json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
        response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
        return response

    except Exception as e:
        error_message = "伺服器內部錯誤: {}".format(str(e))
        new_data = {"error": True, "message": error_message}
        json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
        response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
        return response
    
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()