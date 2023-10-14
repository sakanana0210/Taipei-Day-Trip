from flask import *
from app.attractions_bp import attractions_bp
from app.user_bp import user_bp
from app.booking_bp import booking_bp
from app.orders_bp import orders_bp
from app.upload_avatar_bp import upload_avatar_bp
from app.get_avatar_phone_bp import get_avatar_phone_bp
from app.user_change_bp import user_change_bp
from app.user_orders_bp import user_orders_bp

app=Flask(__name__)
app.register_blueprint(attractions_bp, url_prefix="/api")
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(booking_bp, url_prefix="/api")
app.register_blueprint(orders_bp, url_prefix="/api")
app.register_blueprint(upload_avatar_bp, url_prefix="/api")
app.register_blueprint(get_avatar_phone_bp, url_prefix="/api")
app.register_blueprint(user_change_bp, url_prefix="/api")
app.register_blueprint(user_orders_bp, url_prefix="/api")

app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config["UPLOAD_FOLDER"] = "static/avatars"
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

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
@app.route("/user")
def user():
	return render_template("member_center.html")

app.run(host="0.0.0.0", port=3000)