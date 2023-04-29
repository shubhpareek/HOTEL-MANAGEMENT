from flask import Flask, render_template, request, url_for, redirect,session
from dotenv import load_dotenv
load_dotenv()
import os
import psycopg2

app = Flask(__name__)
app.secret_key = "shubh "
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='hotell',
                            user=os.getenv('DB_USERNAME'),
                            password=os.getenv('DB_PASSWORD'))
    return conn
def get_db_connection1(username,password):
    conn = psycopg2.connect(host='localhost',
                            database='hotell',
                            user=username,
                            password=password)
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    # cur.execute('SELECT * FROM books;')
    # books = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html')
# ...

@app.route('/receptionist/', methods=('GET', 'POST'))
def receptionist():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username']= username
        session['password']= password

        try:
            conn = get_db_connection1(username,password)
            # render_template('recepage.html');
            print("hellllo")
            return redirect(url_for('recepage'))
        except:
            return render_template('receptionist.html')

    return render_template('receptionist.html')

@app.route('/recepage/')
def recepage():
    # print("hello")

    return render_template('recepage.html')

@app.route('/roombook/',methods=('GET', 'POST'))
def roombook():

    if request.method == 'POST':
        customer_id= request.form['customer_id']
        indate = request.form['indate']
        outdate = request.form['outdate']
        size = request.form['size']
        typpe = request.form['type']
        indate = indate.replace('T',' ')
        outdate  = outdate.replace('T',' ')
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("CALL book_room(%s,%s,%s,%s,%s)",[customer_id,indate,outdate,typpe,size])
            print(cur.statusmessage)
            msg = conn.notices[-1]
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('message.html',message=msg)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    return render_template('roombook.html')
@app.route('/createcustomer/',methods=('GET','POST'))
def createcustomer():
    
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        age = request.form['age']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute('insert into customer(name,phone_no,age,lastexit) values(%s,%s,%s,current_timestamp)',[name,phone,age])
            # msg = conn.notices[-1]
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('message.html',message='created customer')
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    return render_template('createcustomer.html')
@app.route('/closest/',methods=('GET','POST'))
def closest():
    if request.method == 'POST':
        indate = request.form['indate']
        outdate = request.form['outdate']
        size = request.form['size']
        typpe = request.form['type']
        indate = indate.replace('T',' ')
        outdate  = outdate.replace('T',' ')
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("select closest(%s,%s,%s,%s)",[indate,outdate,typpe,size])
            vv = cur.fetchall()
            # print(vv)
            # for x in vv:
            #     print(x)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('closest.html',books=vv)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    else:
        return render_template('closest1.html')
@app.route('/lookup/',methods=['GET','POST'])
def lookup():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        when = request.form['when']
        quantity = request.form['quantity']
        type = request.form['type']
        when = when.replace('T',' ')
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("select lookupacc(%s,%s,%s,%s)",[customer_id,type,quantity,when])
            vv = cur.fetchall()
            # print(vv)
            # for x in vv:
            #     print(x)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('message.html',message=vv)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    else:
        return render_template('lookup.html')
@app.route('/forservice/',methods=('GET', 'POST'))
def forservice():
    if request.method == 'POST':
        customer_id= request.form['customer_id']
        indate = request.form['indate']
        outdate = request.form['outdate']
        typpe = request.form['type']
        indate = indate.replace('T',' ')
        outdate  = outdate.replace('T',' ')
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("CALL forservice(%s,%s,%s,%s)",[customer_id,indate,outdate,typpe])
            print(cur.statusmessage)
            msg = conn.notices[-1]
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('message.html',message=msg)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    return render_template('forservice.html')
@app.route('/finalbill/',methods = ['GET','POST'])
def finalbill():
    if request.method == 'POST':
        customer_id= request.form['customer_id']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("""
            select payments.payment_type,amount,status,DATE_OF_INITIATION from payments,customer
            where payments.customer_id = %s and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;
            """,[customer_id])
            vv = cur.fetchall()
            cur.execute("""select sum(amount) from payments,customer
            where payments.customer_id = %s and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;""",[customer_id])
            total = cur.fetchall();
            print(vv)
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('finalbill.html',books=vv,customer_id=customer_id,total=total[0][0])
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    return render_template('finalbill1.html')
@app.route('/customerinformation/',methods = ['GET','POST'])
def customerinformation():
    if request.method == 'POST':
        customer_id= request.form['customer_id']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("""
            select * from customer where name like %s
            """,['%'+customer_id+'%'])
            vv = cur.fetchall()
            print(vv)
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('customerinformation.html',books=vv)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    return render_template('customerinformation1.html')
@app.route('/manager/', methods=('GET', 'POST'))
def manager():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username1']= username
        session['password1']= password

        try:
            conn = get_db_connection1(username,password)
            # render_template('recepage.html');
            print("hellllo")
            return redirect(url_for('manpage'))
        except:
            return render_template('manager.html')

    return render_template('manager.html')
@app.route('/manpage/')
def manpage():
    # print("hello")

    return render_template('manpage.html')
@app.route('/addaccessory/',methods = ['GET','POST'])
def addaccessory():
    if request.method == 'POST':
        accessory_id = request.form['accessory_id']
        quantity = request.form['quantity']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username1'],session['password1'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("update accessory set quantity = %s where accessory_id = %s",[quantity,accessory_id])
            vv = cur.statusmessage
            # print(vv)
            # for x in vv:
            #     print(x)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('message2.html',message=vv)
        except Exception as e:
            print(e)
            return redirect(url_for('manager'))
    else:
        return render_template('addaccessory.html')
    
@app.route('/payment/<customer_id>',methods=('GET','POST'))
def payment(customer_id):
    if request.method == 'POST':
        try:
            conn = get_db_connection1(session['username'],session['password'])
            cur = conn.cursor()
            cur.execute("call finalpayment(%s)",customer_id)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('payment.html',message="payment done")
        except Exception as e:  
            print(e)
            return redirect(url_for('receptionist'))
    else:
        return render_template('payment.html',message="payment failed")