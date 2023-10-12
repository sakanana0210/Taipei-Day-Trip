from flask import *
from app import mysqlConfig,jwt
import re

dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
create_jwt = jwt.create_jwt
verify_jwt = jwt.verify_jwt
user_change_bp = Blueprint("chanuser_change", __name__)

def check_password(password):
	pattern = r"^(?=.*[A-Za-z])(?=.*\d).{8,20}$"
	return re.match(pattern, password)

def check_phone(phone):
	pattern = r"^0\d{9}$"
	return re.match(pattern, phone)

@user_change_bp.route("/user_change", methods=["POST"])
def user_change():
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
            
        data = request.get_json()
        name = data["name"]
        email = data["email"]
        new_password = data["new_password"]
        phone = data["phone"]
        old_password = data["old_password"]
        cursor.execute("SELECT id FROM member WHERE BINARY id = %s and password = %s", (user_id, old_password))
        password_correct = cursor.fetchone()
        if not password_correct:
            error_message = "原密碼錯誤，請重新嘗試"
            new_data = {"error": True, "message": error_message}
            json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
            response = Response(json_data, status=403, content_type="application/json; charset=utf-8")
            return response
        if new_password is not None and new_password != "" and not check_password(new_password):
            error_message = "新密碼格式錯誤 (需包含字母與數字，且長度在8到20之間)"
            new_data = {"error": True, "message": error_message}
            json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
            response = Response(json_data, status=403, content_type="application/json; charset=utf-8")
            return response
        elif new_password is not None and new_password != "" and check_password(new_password):
            query = "UPDATE member SET password = %s WHERE id = %s"
            cursor.execute(query, (new_password, user_id))
            cnx.commit()

        if name is not None and name != "":
            query = "UPDATE member SET name = %s WHERE id = %s"
            cursor.execute(query, (name, user_id))
            cnx.commit()

        if phone is not None and phone != "" and not check_phone(phone):
            error_message = "電話號碼格式錯誤(09開頭，共10碼)"
            new_data = {"error": True, "message": error_message}
            json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
            response = Response(json_data, status=403, content_type="application/json; charset=utf-8")
            return response
        elif phone is not None and phone != "" and check_phone(phone):
            query = "UPDATE member SET phone = %s WHERE id = %s"
            cursor.execute(query, (phone, user_id))
            cnx.commit()

        if email is not None and email != "":
            query = "UPDATE member SET email = %s WHERE id = %s"
            cursor.execute(query, (email, user_id))
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