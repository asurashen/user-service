import logging
import os
import pymysql

class UserResource:
    def __int__(self):
        pass

    @staticmethod
    def _get_connection():
        connection = pymysql.connect(
            user='admin',
            password='Bluesun777!',
            host='user-db.csxsjvnu1wkk.us-east-1.rds.amazonaws.com', #modify
            port=3306,
        )
        return connection

    @staticmethod
    def _run_sql(sql):
        logging.info(sql)
        connection = UserResource._get_connection()
        cur = connection.cursor()
        cur.execute(sql)
        result = cur.fetchall()
        return result

    @staticmethod
    def get_user_by_id(id):
        sql = "SELECT id, name FROM user_schema.user_info WHERE id = {}".format(id)
        return UserResource._run_sql(sql)

    @staticmethod
    def get_user_by_login(username, password):
        sql = "SELECT id, name FROM user_schema.user_info WHERE name = {} and password = {}".format(username, password)
        return UserResource._run_sql(sql)
        
    @staticmethod
    def get_teachers_courses_byuser(id):
        teachers_sql = "SELECT Distinct teachers FROM user_schema.user_{}".format(id)
        teachers = UserResource._run_sql(teachers_sql)
        courses_sql = "SELECT Distinct courses FROM user_schema.user_{}".format(id)
        courses = UserResource._run_sql(courses_sql)
        return teachers, courses
    
    @staticmethod
    def post_user_register(username, password, email):
        sql = "INSERT INTO user_schema.user_info(name,password,email) VALUES ({}, {}, {})".format(username, password, email)
        if UserResource._run_sql(sql)==1:
            userID = UserResource._run_sql("SELECT id from user_schema.user_info where name={} and password={} and email={}".format(username, password, email))
            sql2 = "CREATE TABLE user_{} (teacher varchar(255),course varchar(255));".format(userID)
            return True
        return False
        
    
    @staticmethod
    def post_teacher_course(user, teacher, course):
        sql = "INSERT INTO user_schema.user_{}(teacher,course) VALUES ({}, {})".format(user, teacher, course)
        if UserResource._run_sql(sql)==1:
            return True
        return False
    #post teachers and courses

# main function is only for testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    res = UserResource.post_user_register("asura", "030508", "asurashen8@gmail.com")
    print(res)
