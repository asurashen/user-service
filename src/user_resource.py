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
    def _modify_sql(sql):
        logging.info(sql)
        connection = UserResource._get_connection()
        cur = connection.cursor()
        cur.execute(sql)
        connection.commit()
        result = cur.rowcount
        return result


    @staticmethod
    def get_all_users():
        sql = "SELECT id FROM user_schema.user_info"
        return UserResource._run_sql(sql)

    @staticmethod
    def get_user_by_id(id):
        sql = "SELECT id, name FROM user_schema.user_info WHERE id = {}".format(id)
        return UserResource._run_sql(sql)

    @staticmethod
    def validate_email(email):
        sql = "SELECT id FROM user_schema.user_info WHERE email = '{}'".format(email)
        return UserResource._run_sql(sql)

    @staticmethod
    def get_user_by_login(username, password):
        sql = "SELECT id, name FROM user_schema.user_info WHERE name='{}' AND password='{}'".format(username, password)
        return UserResource._run_sql(sql)

    @staticmethod
    def get_teachers_courses_byuser(id):
        teachers_sql = "SELECT Distinct teacher FROM user_schema.user_{}".format(id)
        teachers = UserResource._run_sql(teachers_sql)
        courses_sql = "SELECT Distinct course FROM user_schema.user_{}".format(id)
        courses = UserResource._run_sql(courses_sql)
        return teachers, courses

    @staticmethod
    def post_user_register(username, password, email, address):
        sql = "SELECT * FROM user_schema.user_info WHERE name = '{}'".format(username)
        if UserResource._run_sql(sql):
            return False, -2
        if UserResource.validate_email(email):
            return False, -3
        sql = "INSERT INTO user_schema.user_info(name,password,email,address) VALUES ('{}', '{}', '{}','()')".format(username, password, email, address)
        result = UserResource._modify_sql(sql)
        print(username,password,email)
        print(result)
        if result==1:
            print('here')
            userID = UserResource._run_sql("SELECT id from user_schema.user_info where name='{}' AND password='{}' AND email='{}'".format(username, password, email))
            print(userID)
            sql2 = "CREATE TABLE user_schema.user_{} (teacher varchar(255),course varchar(255))".format(int(userID[0][0]))
            result2 = UserResource._modify_sql(sql2)
            return True, userID
        return False, -1
    
    @staticmethod
    def post_teacher_course(user, teacher, course):
        sql = "INSERT INTO user_schema.user_{}(teacher,course) VALUES ('{}', '{}')".format(user, teacher, course)
        if UserResource._modify_sql(sql)==1:
            return True
        return False
    #post teachers and courses

# main function is only for testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    res = UserResource.post_user_register("asura", "030508", "asurashen8@gmail.com")
    print(res)

                                                                  
        
    
