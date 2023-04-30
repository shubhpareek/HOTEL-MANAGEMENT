from flask import Flask, render_template, request, url_for, redirect,session

from psycopg2.extensions import AsIs
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
    conn = get_db_connection1(session['username'],session['password'])
    # render_template('recepage.html');

    cur = conn.cursor()
    cur.execute("select * from message order by time desc;")
    print(cur.statusmessage)
    msg = cur.fetchall() 
    print("hellllo")
    conn.commit()
    cur.close()
    conn.close()

    return render_template('recepage.html',message=msg)

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
            print(total)
            cur.execute("""select loyalty from payments,customer
            where payments.customer_id = %s and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;""",[customer_id])
            loyalty=cur.fetchall();
            print(loyalty)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('finalbill.html',books=vv,customer_id=customer_id,total=total[0][0],discount=str(loyalty[0][0]*5)+'%',discounted=float(total[0][0])*(float(loyalty[0][0]*0.05)))
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
    conn = get_db_connection1(session['username'],session['password'])
    # render_template('recepage.html');

    cur = conn.cursor()
    cur.execute("select * from message order by time desc;")
    print(cur.statusmessage)
    msg = cur.fetchall() 
    print("hellllo")
    conn.commit()
    cur.close()
    conn.close()

    return render_template('manpage.html',message=msg)
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
            return render_template('message.html',message="payment done")
        except Exception as e:  
            print(e)
            return redirect(url_for('receptionist'))
    else:
        return render_template('message.html',message="payment failed")


@app.route('/cancelbooking/',methods = ['GET','POST'])
def cancelbooking():
    if request.method == 'POST':
        customer_id= request.form['customer_id']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            cur = conn.cursor()
            cur.execute("""
            select p.amount,r.room_type,r.room_size,p.status,r.room_no,p.DATE_OF_INITIATION,p.payment_id from payments as p,rooms_booked as rb,room as r where p.customer_id = %s and p.payment_id =
            rb.payment_id and room_indate >= current_timestamp and r.room_no = rb.room_no and p.payment_type = 'BOOKING' ;
            """,[customer_id])
            vv = cur.fetchall()
            print(vv)
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('cancelbooking.html',books=vv)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    return render_template('cancelbooking1.html')
@app.route('/cancel/<payment_id>',methods = ['GET','POST'])
def cancel(payment_id):

    conn = get_db_connection1(session['username'],session['password'])
    cur = conn.cursor()
    cur.execute("""
    delete from rooms_booked where payment_id = %s ;""",payment_id)
    cur.execute("""
    delete from payments where payment_id = %s ;""",payment_id)
    conn.commit()
    cur.close()
    conn.close()
    return render_template('message.html',message ='booking of payment id '+str(payment_id)+'was deleted' )
@app.route('/worker/', methods=('GET', 'POST'))
def worker():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username2']= username
        session['password2']= password

        try:
            conn = get_db_connection1(username,password)
            # render_template('recepage.html');
            print("hellllo")
            return redirect(url_for('workpage'))
        except:
            return render_template('worker.html')

    return render_template('worker.html')
@app.route('/workpage/')
def workpage():
    # print("hello")

    return render_template('workpage.html')
@app.route('/seeservice/',methods = ['GET','POST'])
def seeservice():
    if request.method == 'POST':
        service_id= request.form['service_id']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            cur = conn.cursor()
            cur.execute("""
            select * from %s;
            """,[AsIs('for'+str(service_id)+'viewer')])
            vv = cur.fetchall()
            print(vv)
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('seeservice1.html',books=vv)
        except Exception as e:
            print(e)
            return redirect(url_for('worker'))
    return render_template('seeservice.html')
@app.route('/ADMIN/', methods=('GET', 'POST'))
def ADMIN():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username2']= username
        session['password2']= password

        try:
            conn = get_db_connection1(username,password)
            # render_template('recepage.html');
            print("hellllo")
            return redirect(url_for('ADMINPAGE'))
        except:
            return render_template('ADMIN.html')

    return render_template('ADMIN.html')
@app.route('/ADMINPAGE/')
def ADMINPAGE():
    # print("hello")

    return render_template('ADMINPAGE.html')
@app.route('/seequery/',methods = ['GET','POST'])
def seequery():
    if request.method == 'POST':
        query= request.form['query']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            cur = conn.cursor()
            cur.execute("""
            %s
            """,[AsIs(query)])
            xx= cur.description
            print(xx)

            vv = cur.fetchall()
            print(vv)
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('seequery.html',books=vv,desc=xx)
        except Exception as e:
            print(e)
            return redirect(url_for('ADMIN'))
    return render_template('seequery1.html')
@app.route('/finzeroac/')
def finzeroac():
    try:
        conn = get_db_connection1(session['username1'],session['password1'])
        cur = conn.cursor()
        cur.execute("""
        select * from not_available_accessory;
        """)

        vv = cur.fetchall()
        print(vv)
        conn.commit()
        cur.close()
        conn.close()
        return render_template('finzeroac.html',books=vv)
    except Exception as e:
        print(e)
        return redirect(url_for('manager'))
    return render_template('seequery1.html')
@app.route('/messageforman/',methods=['GET','POST'])
def messageforman():
    if request.method == 'POST':
        customer_id= request.form['message']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("""
            insert into message values(current_timestamp,'manager',%s);
            """,[customer_id])
            # vv = cur.fetchall()
            # print(vv)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('message2.html',message='message sent successfully')
        except Exception as e:
            print(e)
            return redirect(url_for('manager'))
    return render_template('takemessage.html')
        
@app.route('/messageforrecep/',methods=['GET','POST'])
def messageforrecep():
    if request.method == 'POST':
        customer_id= request.form['message']
        # print(indate,outdate) 
        try:
            conn = get_db_connection1(session['username'],session['password'])
            # render_template('recepage.html');

            cur = conn.cursor()
            cur.execute("""
            insert into message values(current_timestamp,'receptionist',%s);
            """,[customer_id])
            # vv = cur.fetchall()
            # print(vv)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('message.html',message='message sent successfully')
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist'))
    return render_template('takemessage.html')
        