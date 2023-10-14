from flask import *
from app import mysqlConfig,jwt
import re
dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
create_jwt = jwt.create_jwt
verify_jwt = jwt.verify_jwt
booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/booking", methods=["GET", "POST", "DELETE"])
def api_booking():
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
		if request.method == "POST":
			booking_data = request.get_json()
			date_string = booking_data["date"]
			booknig_date = date_string.replace("-", "")
			booknig_attraction_id = booking_data["attractionId"]
			booknig_time = booking_data["time"]
			booking_price = str(booking_data["price"])
			date_pattern = re.compile(r"^\d{8}$")
			for key, value in booking_data.items():
				if value == "" or value is None:
					error_message = "建立失敗，輸入不正確或其他原因"
					new_data = {"error": True, "message": error_message}
					json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
					response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
					return response
			if not (date_pattern.match(booknig_date) and (booknig_time == "morning" or booknig_time == "afternoon") and (booking_price == "2500" or booking_price == "2000")):
				error_message = "建立失敗，輸入不正確或其他原因"
				new_data = {"error": True, "message": error_message}
				json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
				response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
				return response
			query = "INSERT INTO booking (user_id, attraction_id, date, time, price) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE user_id = VALUES(user_id),  attraction_id = VALUES(attraction_id), date = VALUES(date), time = VALUES(time), price = VALUES(price)"
			cursor.execute(query,(user_id, booknig_attraction_id, booknig_date, booknig_time, booking_price ))
			cnx.commit()
			new_data = {"ok": True}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
			return response
		
		elif request.method == "GET":
			query_1 = "SELECT id FROM booking WHERE user_id = %s;"
			cursor.execute(query_1,(user_id, ))
			booking_id_tuple = cursor.fetchone()
			booking_id = booking_id_tuple[0]
			query_2 = "SELECT attractions.id AS attraction_id, attractions.name AS attraction_name, attractions.address AS attraction_address, JSON_UNQUOTE(JSON_EXTRACT(attractions.images, '$[0]')) AS attraction_image, booking.date AS booking_date, booking.time AS booking_time, booking.price AS booking_price FROM attractions JOIN booking ON attractions.id = booking.attraction_id WHERE booking.id = %s;"
			cursor.execute(query_2,(booking_id, ))
			result = cursor.fetchone()
			formated_date = result[4].strftime("%Y-%m-%d")
			if (result is None):
				new_data = {"data": None}
				json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
				response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
				return response
			new_data = {
				"data": {
					"attraction": {
						"id": result[0],
						"name": result[1],
						"address": result[2],
						"image": result[3]
					},
					"date":formated_date,
					"time": result[5],
					"price": result[6]
				}
			}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
			return response
		
		elif request.method == "DELETE":
			query = "DELETE FROM booking WHERE user_id = %s;"
			cursor.execute(query, (user_id, ))
			cnx.commit()
			new_data = {"ok": True}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
			return response

	except Exception as e:
		if request.method == "POST":
			error_message = "伺服器內部錯誤: {}".format(str(e))
			new_data = {"error": True, "message": error_message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
			return response
		elif request.method == "GET":
			new_data = {"data": None}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
			return response

	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()