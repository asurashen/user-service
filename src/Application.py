import json
import logging
from collections import defaultdict
from datetime import datetime
from flask import Flask, Response, request


from user_resource import UserResource

logging.basicConfig(level=logging.INFO)

# Create the Flask application object.
app = Flask(__name__)


@app.route('/', methods=["GET"])
def index():
    return 'You have reached the index page!'

@app.route("/health", methods=["GET"])
def get_health():
    msg = {
        "name": "User Service",
        "health": "Good",
        "at time": str(datetime.now())
    }
    result = Response(json.dumps(msg), status=200, content_type="application/json")

    return result

@app.route("/user/<id>", methods=["GET"])
def get_user_by_id(id):
    db_result = UserResource.get_user_by_id(id)
    if db_result:
        db_result = db_result[0]
        teachers, courses= UserResource.get_teachers_courses_byuser(id)
        result = {'id': db_result[0], 'username': db_result[1], 'teachers': teachers , 'courses': courses}
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

@app.route("/user/login", methods=["GET"])
def get_user_by_login(username, password):
    db_result = UserResource.get_user_by_login(username, password)
    if db_result:
        db_result = db_result[0]
        result = {'id': db_result[0]}
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")
        
    return rsp

@app.route("/user/register", methods=["POST"])
def post_user_register(username, password, email):
    db_result = UserResource.post_user_register(username, password, email)
    result = {'success': db_result}
    rsp = Response(json.dumps(result), status=200, content_type="application.json")
    return rsp
    
@app.route("/user/<id>", methods=["POST"])
def post_teacher_course(id, teacher, course):
    db_result = UserResource.post_teacher_course(id, teacher, course)
    result = {'success': db_result}
    rsp = Response(json.dumps(result), status=200, content_type="application.json")
    return rsp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
