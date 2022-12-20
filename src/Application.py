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

@app.route("/user", methods=["GET"])
def get_all_users():
    db_result = UserResource.get_all_users()
    print(db_result)
    if db_result:
        result = {'userIDs': [x[0] for x in db_result]}
        print(result)
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NO USER EXIST", status=404, content_type="text/plain")

    return rsp

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

@app.route("/user/validate", methods=["GET"])
def validate_email():
    email = ''
    if not request.args:
        logging.info('username and password are empty')
    else:
        args = dict(request.args)
        email = args['email']
    db_result = UserResource.validate_email(email)
    if db_result:
        db_result = db_result[0]
        result = {'id': db_result[0]}
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("Email NOT FOUND", status=404, content_type="text/plain")

    return rsp

@app.route("/user/login", methods=["GET"])
def get_user_by_login():
    if not request.args:
        logging.info('username and password are empty')
    else:
        args = dict(request.args)
        username, password = args['username'],args['password']
        db_result = UserResource.get_user_by_login(username, password)
    if db_result:
        db_result = db_result[0]
        result = {'id': db_result[0]}
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp
@app.route("/user/register", methods=["POST"])
def post_user_register():
    #client = Client(AUTH_ID, AUTH_TOKEN)
    if not request.args:
        logging.info('user register info is empty')
    else:
        args = dict(request.args)
        username, password, email, address = args['username'], args['password'], args['email'], args['address']
        db_result = UserResource.post_user_register(username, password, email,address)
        #if username is exit:
        #rsp = Response("BAD USERNAME", status=401, content_type="text/plain")

    if db_result[0]:
        result = {'success': db_result[0], 'userID': db_result[1]}
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        if db_result[1]==-2:
            rsp = Response("Duplicate Username, Please Try Again", status=401, content_type="text/plain")
        elif db_result[1]==-3:
            rsp = Response("Email already registered, Please Try Again", status=401, content_type="text/plain")
        else:
            rsp = Response("NOT FOUND", status=404, content_type="text/plain")
    return rsp
@app.route("/user/<id>", methods=["POST"])
def post_teacher_course(id):
    if not request.args:
        logging.info('course info is empty')
    else:
        args = dict(request.args)
        teacher, course = args['teacher'], args['course']
        db_result = UserResource.post_teacher_course(id, teacher, course)
        if db_result:
            result = {'success': db_result}
            rsp = Response(json.dumps(result), status=200, content_type="application.json")
        else:
            rsp = Response("NOT FOUND", status=404, content_type="text/plain")
        return rsp



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011)
