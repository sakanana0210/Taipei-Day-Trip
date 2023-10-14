from app import mysqlConfig,jwt
import json
from flask import *
import os
import time

dbconfig = mysqlConfig.dbconfig
conn_pool = mysqlConfig.conn_pool
verify_jwt = jwt.verify_jwt
upload_avatar_bp = Blueprint("upload_avatar", __name__)

def allowed_file(filename):
    allowed_extensions = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

@upload_avatar_bp.route("/upload", methods=["POST"])
def upload_avatar():
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
        if "file" not in request.files:
            raise Exception
        
        file = request.files["file"]
        if file.filename == "":
            raise Exception
        
        if file and allowed_file(file.filename):
            query = "SELECT avatar_url FROM member WHERE id = %s"
            cursor.execute(query, (user_id, ))
            result = cursor.fetchone()
            old_avatar_url = result[0]
            if old_avatar_url is not None and old_avatar_url != "":
                old_avatar_path = os.path.join(current_app.config["UPLOAD_FOLDER"], os.path.basename(old_avatar_url))
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            timestamp = int(time.time()) 
            base_filename, file_extension = os.path.splitext(file.filename)
            unique_filename = f"{base_filename}_{timestamp}{file_extension}"
            filename = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filename)
            avatar_url = f"/static/avatars/{unique_filename}"
            query = "UPDATE member SET avatar_url = %s WHERE id = %s"
            cursor.execute(query, (avatar_url, user_id))
            cnx.commit()
            new_data = {
                "ok": True 
            }
            json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
            response = Response(json_data, status=200, content_type="application/json; charset=utf-8")
            return response
        
        else:
            raise Exception

    except Exception as e:
        error_message = "上傳失敗"
        new_data = {"error": True, "message": error_message}
        json_data = json.dumps(new_data, ensure_ascii=False, sort_keys=False).encode("utf-8")
        response = Response(json_data, status=403, content_type="application/json; charset=utf-8")
        return response

    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
