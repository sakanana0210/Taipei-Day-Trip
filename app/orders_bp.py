from flask import *
from app import mysqlConfig,jwt
import mysql
from datetime import datetime
import requests

dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
create_jwt = jwt.create_jwt
verify_jwt = jwt.verify_jwt
orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/orders", methods=["POST"])
def orders():
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
		order_number = datetime.now().strftime("%Y%m%d%H%M%S")
		request_data = request.get_json()
		prime = request_data["prime"]
		attraction_id = request_data["order"]["trip"]["attraction"]["id"]
		booking_date = request_data["order"]["trip"]["date"]
		booknig_date_formateed = booking_date.replace("-", "")
		booking_time = request_data["order"]["trip"]["time"]
		price = request_data["order"]["price"]
		phone = request_data["order"]["contact"]["phone"]
		name = request_data["order"]["contact"]["name"]
		email = request_data["order"]["contact"]["email"]
		query = "INSERT INTO orders (order_number, user_id, attraction_id, date, time, price, pay_status, contact_email, contact_name, contact_phone) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor.execute(query,(order_number, user_id, attraction_id, booknig_date_formateed, booking_time, price, -1, email, name, phone))
		cnx.commit()
		partner_key = "partner_cSANX2R4GHeUnR1rmaHC7rawYrUWlT3tAbGN5Rlw4ZNld7FisDZGthgQ"
		merchant_id = "sakanana0210_ESUN"
		url = f"https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime?partner_key={partner_key}&merchant_id={merchant_id}"
		payload = {
			"prime": prime,
			"partner_key": partner_key,
			"merchant_id": merchant_id,
			"details":"TapPay Test",
			"amount": price,
			"currency": "TWD",
			"cardholder": {
				"phone_number": phone,
				"name": name,
				"email": email
			},
			"remember": True
		}
		headers = {
			"Content-Type": "application/json",
			"x-api-key": partner_key
		}
		timeout = 30
		response = requests.post(url, json=payload, headers=headers, timeout=timeout)
		if response.status_code == 200:
			response_content = response.json()
			status = response_content.get("status")

		if status == 0:
			message = "付款成功"
			query = "UPDATE orders SET pay_status = %s WHERE order_number = %s LIMIT 1;"
			cursor.execute(query,(1, order_number))
			cnx.commit()
		else:
			message = "付款失敗"

		new_data = {
			"data": {
				"number": order_number,
				"payment": {
				"status": status,
				"message": message
				}
			}
		}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response

	except mysql.connector.Error as err:
		error_message = "訂單建立失敗，輸入不正確或其他原因"
		new_data = {"error": True, "message": error_message}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
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

@orders_bp.route("/order/<order_number>", methods=["GET"])
def get_order(order_number):
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

		query = """SELECT orders.user_id, orders.order_number, orders.price AS price, 
		attractions.id AS attraction_id, attractions.name AS attraction_name, 
		attractions.address AS attraction_address, JSON_UNQUOTE(JSON_EXTRACT(attractions.images, '$[0]')) AS attraction_image, 
		orders.date AS date, orders.time AS time, orders.contact_email AS email, orders.contact_name AS name,
		orders.contact_phone AS phone, orders.pay_status
		FROM attractions JOIN orders ON attractions.id = orders.attraction_id WHERE orders.order_number = %s;"""
		cursor.execute(query,(order_number, ))
		result = cursor.fetchone()

		order_user_id = result[0]
		if user_id is not order_user_id:
			error_message = "登入id與訂購id不匹配，拒絕存取"
			new_data = {"error": True, "message": error_message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=403, content_type="application/json; charset=utf-8")
			return response

		number = result[1]
		price = result[2]
		attraction_id = result[3]
		attraction_name = result[4]
		attraction_address = result[5]
		attractions_image = result[6]
		date = result[7]
		time = result[8]
		email = result[9]
		name = result[10]
		phone = result[11]
		status = result[12]
		formated_date = date.strftime("%Y-%m-%d")
		new_data ={
				"data": {
					"number": number,
					"price": price,
					"trip": {
					"attraction": {
						"id": attraction_id,
						"name": attraction_name,
						"address": attraction_address,
						"image": attractions_image
					},
					"date": formated_date,
					"time": time
					},
					"contact": {
					"name": name,
					"email": email,
					"phone": "0" + phone
					},
					"status": status
				}
			}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response

	except Exception as e:
		error_message = "無此訂單匹配資訊"
		new_data = {"error": True, "message": error_message}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=403, content_type="application/json; charset=utf-8")
		return response

	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()