from flask import * 
import mysql.connector

con = mysql.connector.connect(
    user = "root",
    # password = os.getenv("mysql_pass"),
    password = "test",
    host = "127.0.0.1",
    database = "website",
)
# print("資料庫連線成功")
cursor = con.cursor()

app = Flask(__name__)
app.secret_key = "secret"

# 首頁
@app.route("/") 
def home(): 
    if session.get("username"):
        return redirect("/member")
    else:
        return render_template("home.html")

# 註冊
@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name")
    username = request.form.get("username")
    password = request.form.get("password")
    # print("名字" + name)
    # print("帳號在這裡" + username)
    # print("密碼在這裡" + password)
    check = "SELECT username FROM member WHERE username = %s"
    user = (username,) # Tuple，只有一個變數逗號還是要留著
    cursor.execute(check, user)
    check_username = cursor.fetchone()
    if check_username != None : 
        return redirect("/error?message=帳號已經被註冊")
    else:
        insert = "INSERT INTO member (name, username, password) VALUES (%s, %s, %s)"
        insert_value = (name, username, password)
        cursor.execute(insert, insert_value)
        con.commit()
        select = "SELECT username FROM member WHERE username = %s"
        select_value = (username,)
        cursor.execute(select, select_value)
        for i in cursor:
            session["username"] = i[0]
        return redirect("/member")

# 登入
@app.route("/signin", methods=["POST"]) 
def signin():
    username = request.form.get("username")
    password = request.form.get("password")
    check = "SELECT password FROM member WHERE username = %s"
    check_value = (username,)
    cursor.execute(check, check_value)
    for member in cursor: 
        # print("for 回圈裡的", member)
        if member[0] == password:
            session["username"] = username
            return redirect("/member")
    return redirect("/error?message=帳號或密碼輸入錯誤")

# 登出
@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

# 會員頁
@app.route("/member")
def member():
    # print("哈囉")
    if session.get("username"): 
        check_name = "SELECT name FROM member WHERE username =%s"
        check_value = (session["username"],)
        cursor.execute(check_name, check_value)
        for name in cursor:
            name = name[0]
        # 留言
        content = "SELECT name, content FROM member INNER JOIN message ON member.id=message.member_id ORDER BY message.time DESC"
        cursor.execute(content)
        row = []
        for i in cursor:
            row.append([i[0],i[1]])
        # print("row 在這裡",row)
        return render_template("member.html", name = name, row = row) # 前面的 row 對 html，後面的 row 是 list
    else:
        return redirect("/")

# 留言系統
@app.route("/createMessage", methods=["POST"])
def createMessage():
    message = request.form.get("message")
    select = "SELECT id FROM member WHERE username = %s"
    select_id = (session["username"],)
    cursor.execute(select, select_id)
    for id in cursor:
        id = id[0]
    insert = "INSERT INTO message (member_id, content) VALUES (%s, %s) "
    insert_value = (id, message)
    cursor.execute(insert, insert_value)
    con.commit()
    return redirect("/member")

# 失敗頁
@app.route("/error")
def error():
    message = request.args.get("message")
    return render_template("error.html", message = message)

if __name__ == "__main__":
    app.run(port=3000, debug = True)
    app.secret_key = "secret"
