from flask import *
from app import mysqlConfig,jwt
import re

dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
create_jwt = jwt.create_jwt
verify_jwt = jwt.verify_jwt
user_bp = Blueprint("user", __name__)


def check_password(password):
	pattern = r"^(?=.*[A-Za-z])(?=.*\d).{8,20}$"
	return re.match(pattern, password)

def check_email(email):
	pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
	return re.match(pattern, email)


@user_bp.route("/user", methods=["POST"])
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


@user_bp.route("/user/auth", methods=["GET", "PUT"])
def user_auth():
	try:
		if request.method == "PUT":
			cnx = conn_pool.get_connection()
			cursor = cnx.cursor()
			data = request.get_json()
			email = data["email"]
			password = data["password"]
			if not check_email(email):
				error_message = "email格式錯誤"
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
			response = Response(new_data, status=200, content_type="application/json; charset=utf-8")
			return response
		
	except Exception as e:
		if request.method == "PUT":
			error_message = "伺服器內部錯誤: {}".format(str(e))
			new_data = {"error": True, "message": error_message}
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