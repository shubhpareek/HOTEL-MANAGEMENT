from flask import Flask, render_template, request, url_for, redirect,session
import psycopg2
from psycopg2.extensions import AsIs
from dotenv import load_dotenv
load_dotenv()
import os

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
    return render_template('index.html')

# receptionist starts 
@app.route('/receptionist-login/', methods=('GET', 'POST'))
def receptionist_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['rusername']= username
        session['rpassword']= password
        try:
            conn = get_db_connection1(username,password)
            conn.close()
            return redirect(url_for('receptionist_home'))
        except Exception as e:
            print(e)
            error = 'Incorrect username or password'
            return render_template('login.html',role='Receptionist',error=error)
    return render_template('login.html',role='Receptionist')

@app.route('/receptionist-home/')
def receptionist_home():
    try:
        conn = get_db_connection1(session['rusername'],session['rpassword'])
        cur = conn.cursor()
        try:
            cur.execute("select * from message order by time desc;")
            msg = cur.fetchall() 
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
        return render_template('receptionist/home.html',message=msg)
    except Exception as e:
        print(e)
        return redirect(url_for('receptionist_login'))   

@app.route('/book-room/',methods=('GET', 'POST'))
def book_room():
    if request.method == 'POST':
        customer_id= request.form['customer_id']
        indate = request.form['indate']
        outdate = request.form['outdate']
        size = request.form['size']
        typpe = request.form['type']
        indate = indate.replace('T',' ')
        outdate  = outdate.replace('T',' ')
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("CALL book_room(%s,%s,%s,%s,%s)",[customer_id,indate,outdate,typpe,size])
                msg = conn.notices[-1]
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',message=msg)
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                error = "check whether the in date-time is not in the past and in date-time is not after out date-time"
                return render_template('receptionist/book_room.html',error=error)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('receptionist/book_room.html')

@app.route('/create-customer/',methods=('GET','POST'))
def create_customer():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        age = request.form['age'] 
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute('insert into customer(name,phone_no,age,lastexit) values(%s,%s,%s,current_timestamp)',[name,phone,age])
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',message='Created customer')
            except Exception as e:
                print(e)
                error = "check whether the age is greater than zero"
                cur.close()
                conn.close()
                return render_template('receptionist/create_customer.html',error=error)   
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('receptionist/create_customer.html')

@app.route('/find-closest-available-room/',methods=('GET','POST'))
def closest():
    if request.method == 'POST':
        indate = request.form['indate']
        outdate = request.form['outdate']
        size = request.form['size']
        typpe = request.form['type']
        indate = indate.replace('T',' ')
        outdate  = outdate.replace('T',' ')
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("select closest(%s,%s,%s,%s)",[indate,outdate,typpe,size])
                vv = cur.fetchall()
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/closest.html',books=vv)
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                error = "check whether the in date-time is not in the past and in date-time is not after out date-time"
                return render_template('receptionist/closest.html',error=error)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('receptionist/closest1.html')

@app.route('/give-accessory/',methods=['GET','POST'])
def give_accessory():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        when = request.form['when']
        quantity = request.form['quantity']
        type = request.form['type']
        when = when.replace('T',' ')
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("select lookupacc(%s,%s,%s,%s)",[customer_id,type,quantity,when])
                vv = cur.fetchall()
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',message=vv)
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',error=e)
        except Exception as e:
            print(e)
            return render_template('receptionist/give_accessory.html')
    else:
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            cur.execute("select * from accessory")
            accessories = cur.fetchall()
            cur.close()
            conn.close()
        except:
            return redirect(url_for('receptionist_login'))
        return render_template('receptionist/give_accessory.html',accessories=accessories)

@app.route('/give-service/',methods=('GET', 'POST'))
def give_service():
    if request.method == 'POST':
        customer_id= request.form['customer_id']
        indate = request.form['indate']
        outdate = request.form['outdate']
        typpe = request.form['type']
        indate = indate.replace('T',' ')
        outdate  = outdate.replace('T',' ')
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("CALL forservice(%s,%s,%s,%s)",[customer_id,indate,outdate,typpe])
                msg = conn.notices[-1]
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',message=msg)
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                error = "check whether start date-time is not in the past and start date-time is not after end date-time"
                return render_template("receptionist/give_service.html",error=error)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    else:
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            cur.execute("select * from service")
            services = cur.fetchall()
            cur.close()
            conn.close()
        except:
            return redirect(url_for('receptionist_login'))
        return render_template('receptionist/give_service.html',services=services)

@app.route('/final-bill/',methods = ['GET','POST'])
def final_bill():
    if request.method == 'POST':
        customer_id= request.form['customer_id']
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("""
                select payments.payment_type,amount,status,DATE_OF_INITIATION from payments,customer
                where payments.customer_id = %s and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;
                """,[customer_id])
                vv = cur.fetchall()
                cur.execute("""select sum(amount) from payments,customer
                where payments.customer_id = %s and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;""",[customer_id])
                total = cur.fetchall()
                cur.execute("""select sum(amount) from payments,customer
                where payments.customer_id = %s and status = 'due' and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;""",[customer_id])
                due = cur.fetchall()

                cur.execute("""select loyalty from payments,customer
                where payments.customer_id = %s and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;""",[customer_id])
                loyalty=cur.fetchall()
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/final_bill.html',due=due[0][0],books=vv,customer_id=customer_id,total=total[0][0],discount=str(loyalty[0][0]*5)+'%',discounted=float(total[0][0])*(float(loyalty[0][0]*0.05)))
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('receptionist/final_bill1.html')

@app.route('/search-customer-by-id',methods=('GET','POST'))
def search_customer_by_id():
    heading = "Search Customer By ID"
    label = 'customer_id'
    label_heading = 'Customer ID'
    type = 'number'
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("""select customer_id,name,phone_no,
                loyalty,age,total_payed,total_due,lastexit 
                from customer where customer_id=%s""",[customer_id])
                info = cur.fetchall()
                return render_template('receptionist/single_search.html',heading=heading,label=label,
                                label_heading=label_heading,type=type,info=info)
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('receptionist/single_search.html',heading=heading,label=label,
                           label_heading=label_heading,type=type)

@app.route('/search-customer-by-name',methods=('GET','POST'))
def search_customer_by_name():
    heading = "Search Customer By Name"
    label = 'name'
    label_heading = 'Name'
    type = 'text'
    error = None
    if request.method == 'POST':
        name = request.form['name']
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("""select customer_id,name,phone_no,
                loyalty,age,total_payed,total_due,lastexit 
                from customer where name ilike %s """,["%"+name+"%"])
                info = cur.fetchall()
                if len(info) == 0:
                    error = "No customer found"
                return render_template('receptionist/single_search.html',heading=heading,label=label,
                                label_heading=label_heading,type=type,info=info,error=error)
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('receptionist/single_search.html',heading=heading,label=label,
                           label_heading=label_heading,type=type)

@app.route('/delete-customer/<customer_id>')
def delete_customer(customer_id):
    try:
        conn = get_db_connection1(session['rusername'],session['rpassword'])
        cur = conn.cursor()
        try:
            cur.execute("delete from customer where customer_id=%s",[customer_id])
            conn.commit()
            cur.close()
            conn.close()
            return render_template('receptionist/message.html',message="Deleted Customer Successfully")
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return render_template('receptionist/message.html',error=e)
    except Exception as e:  
        print(e)
        return redirect(url_for('receptionist_login'))

@app.route('/update-customer/<customer_id>',methods=('GET','POST'))
def update_customer(customer_id):
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        name = request.form['name']
        phone_no = request.form['phone_no']
        age = request.form['age']
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("update customer set name=%s,phone_no=%s,age=%s where customer_id=%s",
                            [name,phone_no,age,customer_id])
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('update_customer',customer_id=customer_id))
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return redirect(url_for('update_customer'),customer_id=customer_id)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    try:
        conn = get_db_connection1(session['rusername'],session['rpassword'])
        cur = conn.cursor()
        try:
            cur.execute("select customer_id,name,phone_no,age from customer where customer_id=%s",[customer_id])
            info = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()
            return render_template('receptionist/update_customer.html',info=info)
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return render_template('receptionist/message.html',error=e)
    except Exception as e:
        print(e)
        return redirect(url_for('receptionist_login'))

@app.route('/payment/<customer_id>',methods=('GET','POST'))
def payment(customer_id):
    if request.method == 'POST':
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            cur.execute("call finalpayment(%s)",customer_id)
            try:
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',message="payment done")
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',error=e)
        except Exception as e:  
            print(e)
            return redirect(url_for('receptionist_login'))
    else:
        return render_template('receptionist/message.html',message="payment failed")
    
@app.route('/cancel-booking/',methods = ['GET','POST'])
def cancel_booking():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("""
                select p.amount,r.room_type,r.room_size,p.status,r.room_no,p.DATE_OF_INITIATION,p.payment_id from payments as p,rooms_booked as rb,room as r where p.customer_id = %s and p.payment_id =
                rb.payment_id and room_indate >= current_timestamp and r.room_no = rb.room_no and p.payment_type = 'BOOKING' ;
                """,[customer_id])
                vv = cur.fetchall()
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/cancel_booking.html',books=vv)
            except Exception as e:
               print(e) 
               cur.close()
               conn.close()
               return render_template('receptionist/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('receptionist/cancel_booking1.html')

@app.route('/cancel/<payment_id>',methods = ['GET','POST'])
def cancel(payment_id):
    try:
        conn = get_db_connection1(session['rusername'],session['rpassword'])
        cur = conn.cursor()
        try:
            cur.execute("""
            delete from rooms_booked where payment_id = %s ;""",payment_id)
            cur.execute("""
            delete from payments where payment_id = %s ;""",payment_id)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(e,'yoyo')
            cur.close()
            conn.close()
            return render_template('receptionist/message.html',error=e)
    except Exception as e:
        print(e,'oyo')
        return redirect('receptionist_login')
    return render_template('receptionist/message.html',message ='Booking of payment id '+str(payment_id)+'was deleted' )

@app.route('/receptionist-message/',methods=['GET','POST'])
def receptionist_message():
    if request.method == 'POST':
        customer_id= request.form['message']
        try:
            conn = get_db_connection1(session['rusername'],session['rpassword'])
            cur = conn.cursor()
            try:
                cur.execute("""
                insert into message values(current_timestamp,'receptionist',%s);
                """,[customer_id])
                conn.commit()
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',message='message sent successfully')
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('receptionist/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('receptionist_login'))
    return render_template('take_message.html')

# manager starts 
@app.route('/manager-login/', methods=('GET', 'POST'))
def manager_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['musername']= username
        session['mpassword']= password
        try:
            conn = get_db_connection1(username,password)
            conn.close()
            return redirect(url_for('manager_home'))
        except:
            return render_template('login.html',role='Manager')
    return render_template('login.html',role='Manager')

@app.route('/manager-home/')
def manager_home():
    try:
        conn = get_db_connection1(session['musername'],session['mpassword'])
        cur = conn.cursor()
        try:
            cur.execute("select * from message order by time desc;")
            print(cur.statusmessage)
            msg = cur.fetchall() 
            print("hellllo")
            conn.commit()
            cur.close()
            conn.close()
            return render_template('manager/home.html',message=msg)
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return render_template('manager/message.html',error=e)
    except Exception as e:
        print(e)
        return redirect(url_for('manager_login'))

@app.route('/add-new-accessory/',methods = ['GET','POST'])
def add_accessory():
    if request.method == 'POST':
        name = request.form['name']
        cost = request.form['cost']
        quantity = request.form['quantity'] 
        try:
            conn = get_db_connection1(session['musername'],session['mpassword'])
            cur = conn.cursor()
            try:
                cur.execute("insert into accessory(accessory_type,accessor_cost,quantity_available) values(%s,%s,%s)",[name,cost,quantity])
                vv = cur.statusmessage
                conn.commit()
                cur.close()
                conn.close()
                return render_template('manager/add_accessory.html',message="Accessory added successfully")
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('manager/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('manager_login'))
    return render_template('manager/add_accessory.html')

@app.route('/delete-accessories/',methods = ['GET','POST'])
def delete_accessories():    
    if request.method == 'POST':
        id = request.form['id']
        try:
            conn = get_db_connection1(session['musername'],session['mpassword'])
            cur = conn.cursor()
            try:
                cur.execute("delete from accessory where accessory_id = %s",[id])
                conn.commit()
                cur.close()
                conn.close()
                return redirect(url_for('delete_accessories'))
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('manager/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('manager_login'))
    try:
        conn = get_db_connection1(session['musername'],session['mpassword'])
        try:
            cur = conn.cursor()
            cur.execute("select * from accessory order by accessory_id;")
            accessories = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()
            return render_template('manager/delete_accessories.html',accessories=accessories)
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return render_template('manager/message.html',error=e)
    except Exception as e:
        print(e)
        return redirect(url_for('manager_login'))

@app.route('/update-accessories/',methods = ['GET','POST'])
def update_accessories():    
    if request.method == 'POST':
        name = request.form['name']
        cost = request.form['cost']
        quantity = request.form['quantity']
        id = request.form['id']
        try:
            conn = get_db_connection1(session['musername'],session['mpassword'])
            cur = conn.cursor()
            try:
                cur.execute("update accessory set accessory_type=%s,accessor_cost=%s,quantity_available = %s where accessory_id = %s",[name,cost,quantity,id])
                vv = cur.statusmessage
                conn.commit()
                cur.close()
                conn.close()
                print("not here")
                return redirect(url_for('update_accessories'))
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('manager/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('manager_login'))
    try:
        conn = get_db_connection1(session['musername'],session['mpassword'])
        cur = conn.cursor()
        try:
            cur.execute("select * from accessory order by accessory_id;")
            accessories = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()
            return render_template('manager/update_accessories.html',accessories=accessories)
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return render_template('manager/message.html',error=e)
    except Exception as e:
        print(e)
        return redirect(url_for('manager_login'))


@app.route('/finished-accessories/')
def finished_accessories():
    try:
        conn = get_db_connection1(session['musername'],session['mpassword'])
        cur = conn.cursor()
        try:
            cur.execute("""
            select * from not_available_accessory;
            """)
            vv = cur.fetchall()
            print(vv)
            conn.commit()
            cur.close()
            conn.close()
            return render_template('manager/finished_accessories.html',books=vv)
        except Exception as e:
            print(e)
            cur.close()
            conn.close()
            return render_template('manager/message.html',error=e)
    except Exception as e:
        print(e)
    return redirect(url_for('manager_login'))

@app.route('/manager-message/',methods=['GET','POST'])
def manager_message():
    if request.method == 'POST':
        message = request.form['message']
        try:
            conn = get_db_connection1(session['musername'],session['mpassword'])
            cur = conn.cursor()
            try:
                cur.execute("""
                insert into message values(current_timestamp,'manager',%s);
                """,[message])
                conn.commit()
                cur.close()
                conn.close()
                return render_template('manager/message.html',message='Message sent successfully')
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('manager/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('manager_login'))
    return render_template('take_message.html')
# manager ends

# worker starts        
@app.route('/worker-login/', methods=('GET', 'POST'))
def worker_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['wusername']= username
        session['wpassword']= password
        try:
            conn = get_db_connection1(username,password)
            conn.close()
            return redirect(url_for('worker_home'))
        except:
            return render_template('login.html',role='Worker')
    return render_template('login.html',role='Worker')

@app.route('/worker-home/')
def worker_home():
    num = session['wusername'].replace('worker','')
    try:
        conn = get_db_connection1(session['wusername'],session['wpassword'])
        try:
            cur = conn.cursor()
            cur.execute("""select * from %s;""",[AsIs('for'+num+'viewer')])
            vv = cur.fetchall()
            conn.commit()
            cur.close()
            conn.close()
            return render_template('worker/home.html',books=vv)
        except Exception as e:
            print(e)
            cur.close()
            conn.commit()
            return render_template('worker/message.html',error=e)
    except Exception as e:
        print(e)       
        return redirect(url_for('worker_login'))
# worker ends

# admin starts
@app.route('/admin-login/', methods=('GET', 'POST'))
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['ausername']= username
        session['apassword']= password
        try:
            conn = get_db_connection1(username,password)
            conn.close()
            return redirect(url_for('admin_home'))
        except:
            return render_template('login.html',role='Admin')
    return render_template('login.html',role='Admin')

@app.route('/admin-home/')
def admin_home():
    return render_template('admin/home.html')

@app.route('/query-tool/',methods = ['GET','POST'])
def query_tool():
    if request.method == 'POST':
        query= request.form['query']
        try:
            conn = get_db_connection1(session['ausername'],session['apassword'])
            cur = conn.cursor()
            try:
                cur.execute("%s",[AsIs(query)])
                desc = cur.description
                vv = cur.fetchall()
                desc = [x[0] for x in desc]
                conn.commit()
                cur.close()
                conn.close()
                return render_template('admin/query_tool.html',books=vv,desc=desc)
            except Exception as e:
                print(e)
                cur.close()
                conn.close()
                return render_template('admin/message.html',error=e)
        except Exception as e:
            print(e)
            return redirect(url_for('admin_login'))
    return render_template('admin/query_tool1.html')
      