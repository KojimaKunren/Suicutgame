import pymysql.cursors


def connect():
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="suicutgame",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


def find_all():
    result = None
    with connect() as con:
        with con.cursor() as cursor:
            sql = "SELECT * FROM userdata"
            cursor.execute(sql)
            result = cursor.fetchall()
    return result


def find_one(user):
    result = None
    resultOne = []
    with connect() as con:
        with con.cursor() as cursor:
            sql = "SELECT * FROM userdata"
            cursor.execute(sql)
            result = cursor.fetchall()
            for n in result:
                if n["username"] == user.username and n["password"] == user.password:
                    id = int(n.get("id"))
                    username = n.get("username")
                    password = n.get("password")
                    topscore = int(n.get("topscore"))
                    secondscore = int(n.get("secondscore"))
                    thirdscore = int(n.get("thirdscore"))
                    resultOne.append(id)
                    resultOne.append(username)
                    resultOne.append(password)
                    resultOne.append(topscore)
                    resultOne.append(secondscore)
                    resultOne.append(thirdscore)
                    break
    return resultOne


def insert_one(user):
    with connect() as con:
        with con.cursor() as cursor:
            sql = "INSERT userdata(username,password,topscore,secondscore,thirdscore) VALUES(%s,%s,%s,%s,%s)"
            cursor.execute(sql, (user.username, user.password, 0, 0, 0))
        con.commit()


def update_one(user):
    with connect() as con:
        with con.cursor() as cursor:
            sql = "UPDATE userdata SET topscore=%d,secondscore=%d,thirdscore=%d"
            cursor.execute(
                sql, (user["topscore"], user["secondscore"], user["thirdscore"])
            )
        con.commit()
