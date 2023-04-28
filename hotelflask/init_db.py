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
cur.execute("""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stat') THEN
	create type stat as enum ('paid', 'due','cancelled');        
    END IF;
END$$;
""")
cur.execute('drop trigger if exists loyalty on customer;')
cur.execute('drop function makeloyal cascade;')
cur.execute('drop trigger if exists logtableupd on service ')
# cur.execute('drop function insertlogtable cascade')
cur.execute('DROP TABLE IF EXISTS customer cascade;')
cur.execute('DROP TABLE IF EXISTS logtable cascade;')
cur.execute('DROP TABLE IF EXISTS service cascade;')
cur.execute('DROP TABLE IF EXISTS accessory cascade;')
cur.execute('DROP TABLE IF EXISTS room cascade;')
cur.execute('DROP TABLE IF EXISTS payments cascade;')
cur.execute('DROP TABLE IF EXISTS service_taken cascade ;')
cur.execute('DROP TABLE IF EXISTS rooms_booked cascade;')

cur.execute("""CREATE TABLE customer(
customer_ID SERIAL PRIMARY KEY,
TOTAL_PAYED INT NOT NULL  check(total_payed >= 0),
TOTAL_DUE     INT  NOT NULL,
loyalty int default 0,
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
ROOM_TYPE TEXT,'
ROOM_SIZE INT
);""")

cur.execute("""CREATE TABLE PAYMENTS
(
PAYMENT_ID SERIAL PRIMARY KEY ,
customer_ID SERIAL ,
AMOUNT NUMERIC NOT NULL ,
STATUS stat NOT NULL,
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
cur.execute("""create table logtable(
SERVICE_ID  INT PRIMARY KEY ,
SERVICE_TYPE TEXT NOT NULL,
SERVICE_RATE INT NOT NULL ,
time timestamp

);
create or replace function insertlogtable()
returns trigger 
language plpgsql
as $$
begin
	insert into logtable 
	values(new.service_id,new.service_type,new.service_rate,current_timestamp);
	return new;
end;
$$;

create trigger logtableupd
after delete
on service
for each row
execute procedure insertlogtable();
"""
)


cur.execute("""create or replace function makeloyal()
returns trigger
language plpgsql
as $$
begin
 if new.total_payed > 2000 
 then 
 
 update customer set loyalty = 2 
 where new.customer_id = customer.customer_id;
 
 return new;
 elsif new.total_payed > 1000
 then 
 
 update customer set loyalty = 1
 where new.customer_id = customer.customer_id;
 
 return new;
 else
  update customer set loyalty = 0
 where new.customer_id = customer.customer_id;

 return new; 
 end if;
end;
$$;
""")
cur.execute("""create trigger loyalty
after update or insert
on customer
for each row 
execute procedure makeloyal();
""")
cur.execute("""create or replace function updtotalpaid()
returns trigger
language plpgsql
as $$
begin
	if new.status = 'due'
	then
	 update customer set customer.total_due = customer.total_due + new.amount;
	elsif new.status = 'paid'
	then 
	 update customer set customer.total_paid = customer.total_paid + new.amount;
	elsif new.status = 'cancelled' and old.status = 'due'
	then
	 update customer set customer.total_due = customer.total_due - new.amount;
	elsif new.status = 'cancelled' and old.status = 'paid'
	then
	 update customer set customer.total_paid = customer.total_paid - new.amount;
	end if;
	return new;
	
end;
$$;
""")
cur.execute("""create trigger updtotalpayed
after insert on
payments
for each row
execute procedure updtotalpaid();
""")
conn.commit()

cur.close()
conn.close()