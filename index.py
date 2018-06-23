from flask import Flask,render_template,request,make_response,redirect,session
import pymysql
import json
import re #匹配正则
from datetime import timedelta #设置session的储存时间
#app.config['SECRET_KEY']=os.urandom(abc)

import common.password as m #引入加密函数
app=Flask(__name__)
app.secret_key='abc'
db=pymysql.connect('localhost','root','root','u1801',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
@app.route("/",methods=["GET"])
def a():
    # if(not session.get('user')):
    #     return redirect('/#/login')
    # else:
    #     return make_response(render_template('index.html'))
    return make_response(render_template('index.html'))
# 注册验证
@app.route("/ajax/check",methods=["GET"])
def check():
    names = request.args.get('uname')
    pass1 = request.args.get('pass1')
    pass2 = request.args.get('pass2')
    if not re.match('^[a-zA-Z]\w{2,21}$',names):
        return redirect('/reg')
    if not re.match('^.{8,32}$',pass1):
        return redirect('/reg')
    if (names == '' or pass1 == '' or pass1 != pass2):
        return redirect('/reg')
    else:
        cursor=db.cursor()
        sql="insert into user (username,password) values(%s,%s)"
        cursor.execute(sql,[names,m.md5(pass1)])
        db.commit()
        return 'ok'
@app.route('/ajax/checks',methods=['GET'])
def checks():
    names=request.args.get('uname')
    cursor=db.cursor()
    sql="select * from user where username='%s'"%(names)
    result=cursor.execute(sql)
    if (result):
        return "ok"
    else:
        return "yes"
@app.route("/ajax/match",methods=["GET"])
def match():
    username = request.args.get('uname')
    password = request.args.get('pass')
    # check= request.args.get('week')
    # if(check):
    #     app.config['PERMANENT_SESSION_LIFETIME']=timedelta(days=7)
    #     session.permanent=True
    cursor = db.cursor()
    sql = "select * from user where username=%s and password=%s"
    cursor.execute(sql, [username, m.md5(password)])
    result = cursor.fetchall()
    if (len(result) > 0):
        str = {"uname": username,"uid":result[0]["id"], "message": "ok"}
        return json.dumps(str)
    else:
        return json.dumps({"message": "yes"})
@app.route('/ajax/select',methods=["GET"])
def select():
    cursor=db.cursor()
    uid=request.args.get('uid')
    did = request.args.get('did')
    sql="select * from todolist1 where uid="+uid+" and did="+did
    cursor.execute(sql)
    data=cursor.fetchall()
    return json.dumps(data)
@app.route('/ajax/add',methods=["GET"])
def add():
    cursor=db.cursor()
    val=request.args.get('val')
    uid = request.args.get('uid')
    did = request.args.get('did')
    sql="insert into todolist1(val,state,edit,uid,did) values('%s',0,1,'%s','%s')"%(val,uid,did)
    cursor.execute(sql)
    db.commit()
    return "ok"
@app.route('/ajax/del',methods=["GET"])
def dels():
    cursor=db.cursor()
    id=request.args.get('id')
    sql="delete from todolist1 where id="+id
    cursor.execute(sql)
    db.commit()
    return "ok"
@app.route('/ajax/changeState',methods=["GET"])
def changeState():
    cursor=db.cursor()
    attr = request.args.get('attr')
    id=request.args.get('id')
    values = request.args.get('values')
    sql="update todolist1 set %s='%s'where id=%s"%(attr,values,id)
    cursor.execute(sql)
    db.commit()
    return "ok"
@app.route('/ajax/addDir',methods=["GET"])
def addDir():
    cursor=db.cursor()
    label=request.args.get('label')
    uid = request.args.get('uid')
    pid = request.args.get('pid')
    edit = request.args.get('edit')
    type = request.args.get('type')
    sql="insert into dir (label,uid,pid,edit,type) values(%s,%s,%s,%s,%s)"
    cursor.execute(sql,[label,uid,pid,edit,type])
    result=db.insert_id()
    db.commit()
    return json.dumps(result)
@app.route('/ajax/editDir',methods=["GET"])
def editDir():
    cursor=db.cursor()
    label=request.args.get('label')
    id = request.args.get('id')
    sql="update dir set label=%s where id=%s"
    cursor.execute(sql,[label,id])
    db.commit()
    return "ok"
@app.route('/ajax/selectDir',methods=["GET"])
def selectDir():
    cursor = db.cursor()
    uid = request.args.get('uid')
    sql = "select * from dir where uid=%s"
    cursor.execute(sql ,[uid])
    result = cursor.fetchall()
    return json.dumps(result)
@app.route('/ajax/delDir',methods=['GET'])
def delDir():
    cursor=db.cursor()
    ids=request.args.get('ids')
    obj=json.loads(ids)  #转化为数组
    str1="("
    str2="("
    flag=True
    for item in obj:
        str1+=str(item["id"])+","
        if(item["type"]=="0"):
            flag=False
            str2 += str(item["id"]) + ","
    str1 = str1[:-1]
    str2 = str2[:-1]
    str1+=")"
    str2+=")"
    if flag:
        str2="(0)"
    sql1 = "delete from dir where id in" + str1
    sql2 = "delete from todolist1 where did in" + str2
    try:
        cursor.execute(sql1)
        cursor.execute(sql2)
    except:
        db.rollback()
    else:
        db.commit()
    return "ok"
if(__name__=="__main__"):
    app.run(host='0.0.0.0')