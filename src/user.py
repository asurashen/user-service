from flask_login import UserMixin
from user_resource import UserResource
class User(UserMixin):
    def __init__(self, id_, name, email="", profile_pic=""):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        print(user_id)
        user = UserResource.get_user_by_id(user_id)
        print(user)
        if user:
            return User(id_=user[0][0], name=user[0][1])
        else:
            return None
