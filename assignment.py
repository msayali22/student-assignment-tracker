from flask import Flask,send_from_directory,render_template,redirect,url_for,request,session,send_file
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
import mysql.connector
import MySQLdb.cursors
import re
import os
import random
from datetime import datetime


app=Flask(__name__)
Uploder="C:\\Users\\sss\\Documents\\student-assignment-tracker\\static_pages"

app.secret_key="defaultkey"
app.config['UPLOAD_FOLDER']=Uploder
app.config['MAX_CONTENT_PATH']='5,00,000'

mysql = MySQL(app)
  
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Sroot@1234'
app.config['MYSQL_DB'] = 'login_details'
  
@app.route("/basic")
def show_homepage():
    page=render_template("basic.html")
    return page


@app.route("/")
def home_page():
    return redirect(url_for('show_homepage'))
    

@app.route('/userlogin',methods=["GET","POST"])
def userlogin():
    if request.method == "GET":
        page=render_template("userlogin.html")
        return page
    elif request.method == "POST":
        msg="Invalid Login"
        name = request.form['username']
        password = request.form['password']
        USERS = get_USER(name)
        User_type=get_user_type(name)
        if len(USERS)==0:
            return render_template("userlogin.html")
        if len(USERS)>1:
            raise Exception (f"Multiple USERS with same name present")
        USER = USERS[0]
        User_type=User_type[0]
        
        if USER[3]==password and User_type[0]=="Student":
            session['username']=request.form['username']
            return redirect(url_for("studentprofile"))
        elif USER[3]==password and User_type[0]=="Faculty":
            return redirect(url_for("facultyprofile"))
        else:
            return render_template('userlogin.html',msg=msg)
    
        
def get_USER(name):
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select * from USER where name = '{name}';""")
    result=cursor.fetchall()
    return result
    
def get_user_type(name):
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select user_type from USER where name = '{name}';""")
    result=cursor.fetchall()
    return result
    
    
@app.route("/userregister",methods=["GET","POST"])
def userregister():
    userid=str(random.randint(0,10000))
    msg=" "
    if request.method=="GET":
        return render_template("userregister.html")
    elif request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        user_type=request.form['user_type']
        USERS = get_USER(name)
        if len(USERS)>0:
            return render_template("userregister.html",already_exists=True)
        elif len(USERS)==0:
            cursor=mysql.connection.cursor()
            cursor.execute(f"""insert into user(userid,name,email,password,user_type)
                       values('{userid}','{name}','{email}','{password}','{user_type}');
                       """)
            mysql.connection.commit()
            cursor.close()
            session['name']=request.form['name']
            session['email']=request.form['email']
            session['password']=request.form['password']
            session['user_type']=request.form['user_type']
            msg="You Have Successfully Registered!!!"
            return redirect(url_for('userlogin'))
            
@app.route("/studentprofile",methods=["GET","POST"])
def studentprofile():
    username=None
    if 'username' in session:
        username=session['username']
    page=render_template("studentprofile.html",username=username)
    return page
    
@app.route("/userdashboard")
def userdashboard():
	if 'username' in session:
		name=session['username']
		cursor=mysql.connection.cursor()
		cursor.execute(f"""select * from user where name='{name}';""")
		result=cursor.fetchall()
		return render_template("userdashboard.html",records=result)
    
@app.route("/deleteprofile",methods=["GET","POST"])
def deleteprofile():
    if 'username' in session:
        name=session['username']
        cursor=mysql.connection.cursor()
        cursor.execute(f"""delete from user where name='{session['username']}';""")
        result=mysql.connection.commit()
        page=render_template("basic.html",records=result)
        return page
  
        
@app.route("/editprofile",methods=["GET","POST"])
def editprofile():
    if request.method=="GET":
        return render_template("editprofile.html")
    elif request.method=="POST":
        if 'username' in session:
            name=session['username']
            email=request.form['email']
            password=request.form['password']
            user_type=request.form['user_type']
            USERS = get_USER(name)
            if len(USERS)>0:
                msg="You Have Successfully Updated!!!"
                cursor=mysql.connection.cursor()
                cursor.execute(f"""Update user
                                SET name='{name}',
                                    email='{email}',
                                    password='{password}',
                                    user_type='{user_type}'
                                    where name='{name}';
                                """)
                result=mysql.connection.commit()
                session['name']=request.form['name']
                session['email']=request.form['email']
                session['password']=request.form['password']
                session['user_type']=request.form['user_type']
                return render_template("userlogin.html",msg=msg,records=result)

@app.route("/viewfile")
def viewfile():
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select * from assignment;""")
    result=cursor.fetchall()
    print(result)
    page=render_template("viewfile.html",records=result)
    return page
    
@app.route('/uploadfile',methods=["GET"])
def uploadfile():
    username=session['username']
    return render_template('uploadfile.html',username=username)
 
 
@app.route("/uploader",methods=["GET","POST"])
def upload_file():
    if 'username' in session:
        username=session['username']
    if request.method == 'POST':
        cursor=mysql.connection.cursor()
        submissionid=str(random.randint(0,1000000))
        submission_date=datetime.now()
        f = request.files['file']
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],f.filename))
        
        u1 = f"""select userid from user where name='{session['username']}' ;"""
        cursor.execute(u1)
        userid_record=cursor.fetchall()
        userid=userid_record[0]
                    
        title=request.form['title']
        
        a1 = f"""select assignmentid from assignment where title='{title}';"""
        cursor.execute(a1)
        assignmentid_rec=cursor.fetchone()
        print(userid_record)
        print(assignmentid_rec)
        
        query=f"""insert into submission(submissionid,assignmentid,userid,submission_date,solution)
            values('{submissionid}','{assignmentid_rec[0]}','{userid[0]}','{submission_date}','{f.filename}');"""
        print(query)
        cursor.execute(query)
        mysql.connection.commit()
        
        return render_template("studentprofile.html",username=username) 

def get_userid(name):
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select userid from USER where name = '{name}';""")
    userid_rec=cursor.fetchone()
    return userid_rec
    
def get_assignmentid(title):
    if 'title' in session:
        title=session['title']
        cursor=mysql.connection.cursor()
        cursor.execute(f"""select assignmentid from assignment where title = '{title}';""")
        assignmentid_rec=cursor.fetchone()
        return assignmentid_rec
        

@app.route("/viewremark",methods=["GET"])
def viewremark():
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select u.email,s.submissionid,s.submission_date,s.status
                       from user u inner join submission s
                       on u.userid=s.userid
                       where name='{session['username']}';""")
    result=cursor.fetchall()
    print(result)
    cursor.close()
    return render_template("viewremark.html",records=result)


@app.route("/facultyprofile",methods=["GET","POST"])
def facultyprofile():
	username=None
	if 'username' in session:
		username=session['username']
	page=render_template("facultyprofile.html",username=username)
	return page
   
   
@app.route("/fuserdashboard",methods=["GET"])
def fuserdashboard():
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select * from user where user_type='Faculty';""")
    result=cursor.fetchall()
    cursor.close()
    return render_template("fuserdashboard.html",records=result)
    

@app.route("/newassignment",methods=["GET","POST"])
def newassignment():
    assignmentid=str(random.randint(0,100000))
    msg='New Assignment Is Uploaded Successfully'
    cursor=mysql.connection.cursor()
    if request.method=='GET':
        return render_template("newassignment.html",msg=msg)
    elif request.method == 'POST':
        title=request.form['title']
        description=request.form['description']
        submission_due_date=request.form['submission_due_date']
        cursor.execute(f"""insert into assignment(assignmentid,title,description,submission_due_date)
                        values('{assignmentid}','{title}','{description}','{submission_due_date}');
                        """)
        result=mysql.connection.commit()
        print(result)
        return redirect(url_for("facultyprofile"))
        
@app.route("/studentassignment",methods=["GET","POST"])
def studentassignment():
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select * from submission;""")
    result=cursor.fetchall()
    cursor.close()
    return render_template("studentassignment.html",records=result)


@app.route('/download/<string:filename>', methods=['GET'])
def download(filename):
   print(filename)
   uploads=Uploder
   return send_file(uploads+'/'+filename, as_attachment=True)
 
 
@app.route('/status',methods=['POST'])
def status():
    cursor=mysql.connection.cursor()
    if request.method == 'POST':
        status = request.form['status']
        submissionid = request.form['submissionid']
        cursor.execute(f"""update submission 
                        SET status = '{status}' 
                        WHERE submissionid ='{submissionid}';""")
        mysql.connection.commit()   
        return render_template("studentassignment.html")

 
@app.route('/status_assignment')
def status_assignment():   
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select * from submission;""")
    result = cursor.fetchall()
    page = render_template("status_assignment.html", records=result)
    return page


@app.route("/approved_assignment")
def approved_assignment():
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select name,email from user where userid in (select userid from submission where status="approved") ;""")
    result=cursor.fetchall()
    page=render_template("approved_assignment.html",records=result)
    return page
 

@app.route("/rejected_assignment")
def rejected_assignment():
    cursor=mysql.connection.cursor()
    cursor.execute(f"""select name,email from user where userid in (select userid from submission where status="rejected") ;""")
    result=cursor.fetchall()
    page=render_template("rejected_assignment.html",records=result)
    return page

    
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('show_homepage'))
   
    
if __name__=="__main__":
    app.run(host="0.0.0.0",port=50000)
    
            
