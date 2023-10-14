from app import mysqlConfig,jwt
import json
from flask import *

dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
create_jwt = jwt.create_jwt
verify_jwt = jwt.verify_jwt
get_avatar_phone_bp = Blueprint("get_avatar", __name__)

@get_avatar_phone_bp.route("/get_avatar", methods=["GET"])
def get_avatar():
    try:
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
        cnx = conn_pool.get_connection()
        cursor = cnx.cursor()
        query = "SELECT avatar_url, phone FROM member WHERE id = %s"
        cursor.execute(query, (user_id, ))
        result = cursor.fetchone()
        avatar_url = result[0]
        user_phone = result[1]
        new_data = {
            "data": {
                "avatar_url": avatar_url,
                "phone": user_phone
            }
        }
        json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
        response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
        return response

    except Exception as e:
        error_message = "伺服器內部錯誤"
        new_data = {"error": True, "message": error_message}
        json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
        response = Response(json_data, status=500, content_type="application/json; charset=utf-8")
        return response

    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
