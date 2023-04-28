import os
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="hotell",
        user='newuser',
        password='password')

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute('DROP TABLE IF EXISTS customer;')
cur.execute('DROP TABLE IF EXISTS service;')
cur.execute('DROP TABLE IF EXISTS accessory;')
cur.execute('DROP TABLE IF EXISTS room;')
cur.execute('DROP TABLE IF EXISTS payments;')
cur.execute('DROP TABLE IF EXISTS service_taken')
cur.execute('DROP TABLE IF EXISTS rooms_booked;')

cur.execute("""CREATE TABLE customer(
customer_ID SERIAL PRIMARY KEY,
TOTAL_PAYED INT NOT NULL  check(total_payed >= 0),
TOTAL_DUE     INT  NOT NULL,
NAME TEXT NOT NULL,
PHONE_NO TEXT NOT NULL,
AGE INT 
);""")

cur.execute("""CREATE TABLE SERVICE(
SERVICE_ID  INT PRIMARY KEY ,
SERVICE_TYPE TEXT NOT NULL,
SERVICE_RATE INT NOT NULL 
);""")

cur.execute("""CREATE TABLE ACCESSORY
(
ACCESSORY_ID  INT PRIMARY KEY, 
ACCESSORY_TYPE TEXT NOT NULL,
ACCESSOR_COST INT NOT NULL, 
QUANTITY_AVAILABLE INT NOT NULL
);""")

cur.execute("""CREATE TABLE ROOM(
ROOM_NO int primary key,
ROOM_COST INT ,
ROOM_TYPE TEXT
);""")

cur.execute("""CREATE TABLE PAYMENTS
(
PAYMENT_ID SERIAL PRIMARY KEY ,
customer_ID SERIAL ,
AMOUNT NUMERIC NOT NULL ,
STATUS TEXT NOT NULL,
PAYMENT_TYPE TEXT NOT NULL,
SERVICE_ID INT ,
ROOM_NO INT,
ACCESSORY_ID INT ,
DATE_OF_INITIATION timestamp,
DATE_OF_COMPLETION timestamp,
FOREIGN KEY(customer_ID)
REFERENCES customer(customer_ID),
FOREIGN KEY(ROOM_NO)
REFERENCES ROOM(ROOM_NO),
FOREIGN KEY(SERVICE_ID)
REFERENCES SERVICE(SERVICE_ID),
FOREIGN KEY(ACCESSORY_ID)
REFERENCES ACCESSORY(ACCESSORY_ID)
);""")


cur.execute("""CREATE TABLE SERVICE_TAKEN(
PAYMENT_ID SERIAL primary key,
service_id int ,
starttime timestamp,
endtime timestamp,
foreign key(service_id)
references service(service_id),
foreign key(payment_id)
references payments(payment_id)

);""")

cur.execute("""CREATE table rooms_booked (
PAYMENT_ID SERIAL primary key,
room_no int ,
room_indate timestamp not null,
room_outdate timestamp not null,
foreign key(payment_id)
references payments(payment_id),
FOREIGN KEY(ROOM_NO)
REFERENCES ROOM(ROOM_NO)
);""")

conn.commit()

cur.close()
conn.close()