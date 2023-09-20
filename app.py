from flask import *
import mysql.connector
import mysql.connector.pooling
import jwt
from datetime import datetime, timedelta
import re
import json

secret_key = "Ca6478B46s551BE1DD067Dds8CB4D71CD9CCBE2E4571047DCE18669B19a257c3C"

def create_jwt(user_id, user_name, user_email):
	payload = {"id": user_id,
		"name": user_name,
		"email": user_email,
		"exp": datetime.utcnow() + timedelta(days=7)
		}
	token = jwt.encode(payload, secret_key, algorithm = "HS256")
	return token

def verify_jwt(token):
	try:
		payload = jwt.decode(token, secret_key, algorithms=["HS256"])
		new_data = {
		"data": {
			"id": payload["id"],
			"name": payload["name"],
			"email": payload["email"]
		}
		}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		return json_data
	except jwt.ExpiredSignatureError:
		new_data = {
		"data": None
		}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		return json_data
	except jwt.InvalidTokenError:
		new_data = {
		"data": None
		}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		return json_data

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
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

# Api
@app.route("/api/attractions", methods=["GET"])
def attractions():
	try:
		message = "查詢錯誤，請重新查詢"
		page = int(request.args.get("page", 0))
		keyword = request.args.get("keyword", "")
		nextpage = page + 1
		start_index = 0
		start_index += page * 12
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		data = []
		if keyword:
			query = "SELECT * FROM attractions WHERE mrt = %s OR name LIKE %s LIMIT %s, 12;"
			cursor.execute(query,(keyword, "%" + keyword + "%", start_index))
			results = cursor.fetchall()
			query_next = "SELECT id FROM attractions WHERE mrt = %s OR name LIKE %s LIMIT %s, 1;"
			cursor.execute(query_next,(keyword, "%" + keyword + "%", start_index + 12))
			ifNext = cursor.fetchall()
			if not results:
				message = "超出查詢範圍，請重新查詢"
				raise Exception
			elif not ifNext:
				nextpage = None
		else:
			query = "SELECT * from attractions LIMIT %s, 12;"
			cursor.execute(query, (start_index,))
			results = cursor.fetchall()
			query_next = "SELECT id FROM attractions LIMIT  %s, 1;"
			cursor.execute(query_next, (start_index + 12,))
			ifNext = cursor.fetchall()
			if not results:
				message = "超出查詢範圍，請重新查詢"
				raise Exception
			elif not ifNext:
				nextpage = None

		for result in results:
			entry = {
				"id": result[0],
				"name": result[1],
				"category": result[2],
				"description": result[3],
				"address": result[4],
				"transport": result[5],
				"mrt": result[6],
				"lat": result[7],
				"lng": result[8],
				"images": json.loads(result[9])
			}
			data.append(entry)
		
		new_data = {"nextPage" : nextpage, "data" : data}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response
	except Exception:
		new_data = {"error": True, "message": message}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
		return response
	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()

@app.route("/api/attraction/<int:attractionId>", methods=["GET"])
def attractions_id(attractionId):
	try:
		message = "查詢錯誤，請重新查詢"
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		query = "SELECT * from attractions WHERE id = %s;"
		cursor.execute(query, (attractionId,))
		result = cursor.fetchone()
		if not result:
			message = "景點編號不正確，請重新查詢"
			raise Exception
		data = {
			"id": result[0],
			"name": result[1],
			"category": result[2],
			"description": result[3],
			"address": result[4],
			"transport": result[5],
			"mrt": result[6],
			"lat": result[7],
			"lng": result[8],
			"images": json.loads(result[9])
		}
		new_data = { "data" : data}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response
	except Exception:
		if(message == "景點編號不正確，請重新查詢"):
			new_data = {"error": True, "message": message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
			return response
		else:
			new_data = {"error": True, "message": message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
			return response
	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()

@app.route("/api/mrts", methods=["GET"])
def mrts():
	try:
		message = "查詢錯誤，請重新查詢"
		cnx = conn_pool.get_connection()
		cursor = cnx.cursor()
		query = "SELECT mrt, COUNT(*) as count FROM attractions GROUP BY mrt ORDER BY count DESC LIMIT 40"
		cursor.execute(query)
		results = cursor.fetchall()
		data = []
		if not results:
			raise Exception
		for result in results:
			data.append(result[0])
		new_data = {"data" : data}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
		return response
	except Exception:
		new_data = {"error": True, "message": message}
		json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
		response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
		return response
	finally:
		if cursor:
			cursor.close()
		if cnx:
			cnx.close()

def check_password(password):
	pattern = r"^(?=.*[A-Za-z])(?=.*\d).{8,20}$"
	return re.match(pattern, password)

def check_email(email):
	pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
	return re.match(pattern, email)

@app.route("/api/user", methods=["POST"])
def user():
	cnx = conn_pool.get_connection()
	cursor = cnx.cursor()
	try:
		data = request.get_json()
		name = data["name"]
		email = data["email"]
		password = data["password"]
		cursor.execute("SELECT email FROM member WHERE BINARY email = %s", (email,))
		useremail = cursor.fetchone()
		if not check_email(email):
			error_message = "email格式錯誤"
			new_data = {"error": True, "message": error_message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
			return response
		elif useremail:
			error_message = "email已經被註冊"
			new_data = {"error": True, "message": error_message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
			return response
		elif not check_password(password):
			error_message = "密碼格式錯誤 (需包含字母與數字，且長度在8到20之間)"
			new_data = {"error": True, "message": error_message}
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
			return response
		else:
			cursor.execute("INSERT INTO member (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
			cnx.commit()
			return jsonify({"ok": True}), 200
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

@app.route("/api/user/auth", methods=["GET", "PUT"])
def user_auth():
	try:
		if request.method == "PUT":
			cnx = conn_pool.get_connection()
			cursor = cnx.cursor()
			data = request.get_json()
			email = data["email"]
			password = data["password"]
			cursor.execute("SELECT id, name, email FROM member WHERE BINARY email = %s and password = %s ", (email,password))
			user_matched = cursor.fetchone()
			if (user_matched):
				token = create_jwt(user_matched[0],user_matched[1],user_matched[2])
				new_data = {"token": token}
				json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
				response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
				return response
			else:
				cursor.execute("SELECT name FROM member WHERE BINARY email = %s", (email,))
				user_unmatched = cursor.fetchone()
				if(not user_unmatched):
					error_message = "登入失敗，此email尚未註冊"
				else: 
					error_message = "登入失敗，密碼錯誤"
				new_data = {"error": True, "message": error_message}
				json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
				response = Response(json_data, status=400, content_type="application/json; charset=utf-8")
				return response
		elif request.method == "GET":
			token = request.headers.get("Authorization")
			new_data = verify_jwt(token.split(" ")[1])
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
			return response
		
	except Exception as e:
		if request.method == "PUT":
			error_message = "伺服器內部錯誤: {}".format(str(e))
			new_data = {"error": True, "message": error_message}
			print(new_data)
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
			return response
		elif request.method == "GET":
			new_data = { "data": None }
			json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
			response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
			return response
	finally:
		if request.method == "PUT":
			if cursor:
				cursor.close()
			if cnx:
				cnx.close()

app.run(host="0.0.0.0", port=3000)