import json
import logging
from collections import defaultdict
from datetime import datetime
from flask import Flask, Response, request

from user_resource import UserResource
# Python standard libraries
import json
import os
import sqlite3

# Third party libraries
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from user import User
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, generate_csrf

# Configuration
GOOGLE_CLIENT_ID = "260669321555-0gh3da24debt1goor8ku6if4s9a5p8nd.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# Flask app setup
logging.basicConfig(level=logging.INFO)

# Create the Flask application object.
app = Flask(__name__)
app.config.update(
    DEBUG=True,
    SECRET_KEY="secret_sauce",
    SESSION_COOKIE_HTTPONLY=True,
    REMEMBER_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"

csrf = CSRFProtect(app)
cors = CORS(
    app,
    resources={r"*": {"origins": "http://localhost:4200,https://d1dp9xzujhowgt.cloudfront.net/"}},
    expose_headers=["Content-Type", "X-CSRFToken"],
    supports_credentials=True,
)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    print("hello???")
    return User.get(user_id)

whitelist = ["googleLogin",
             "checkIsAuthenticated",
             "callback",
             "post_user_register",
             "get_all_users",
             "get_health",
             "validate_email",
             "get_user_by_login"]
@app.before_request
def before_request():
    print(request.endpoint)
    print(request.endpoint not in whitelist )
    if request.endpoint not in whitelist and not current_user.is_authenticated:
        return redirect("https://d1dp9xzujhowgt.cloudfront.net/login")

@app.route('/auth',methods = ['GET'])
def checkIsAuthenticated():
    print(current_user)
    if current_user.is_authenticated:
       data = current_user.id
    else:
       data = -1
    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200, https://d1dp9xzujhowgt.cloudfront.net/")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@app.route("/googleLogin")
def googleLogin():
    site = request.args.get('site')
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    print("authorization_endpoint", authorization_endpoint)

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
        state=site
    )
    print("request_uri", request_uri)
    return redirect(request_uri)


@app.route("/googleLogin/callback")
def callback():
    print(request)
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    site = request.args.get('state')


    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    db_result = UserResource.validate_email(users_email)
    # Doesn't exist? Add to database
    if not db_result:
        return redirect(f"https://d1dp9xzujhowgt.cloudfront.net/register?email={users_email}&name={users_name}")
    else:
        print(db_result)
        user = User(
            id_=db_result[0][0], name="", email=users_email, profile_pic=picture
        )

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    if site is None:
        return redirect("https://d1dp9xzujhowgt.cloudfront.net/home")
    else:
        return redirect("https://d1dp9xzujhowgt.cloudfront.net"+site)


@app.route("/logout")
@login_required
def logout():
    print("logging out")
    logout_user()
    response = app.response_class(
        response=json.dumps("success"),
        status=200,
        mimetype='application/json'
    )
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200, https://d1dp9xzujhowgt.cloudfront.net/")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


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
        print(db_result)
        user = User(db_result[0][0], db_result[0][1])
        login_user(user)
        response = app.response_class(
            response=json.dumps({'id': db_result[0][0]}),
            status=200,
            mimetype='application/json'
        )
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200, https://d1dp9xzujhowgt.cloudfront.net/")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
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
    app.run(host="0.0.0.0", port=5000)
