import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user='newuser',
        password='password')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute("DROP DATABASE IF EXISTS hotell;")
cur.execute('CREATE DATABASE hotell;')
cur.close()
conn.close()
conn = psycopg2.connect(
        host="localhost",
        database="hotell",
        user='newuser',
        password='password')
cur = conn.cursor()
cur.execute("""
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stat') THEN
	create type stat as enum ('paid', 'due','cancelled');        
    END IF;
END$$;
""")
# cur.execute('drop trigger if exists loyalty on customer;')
# cur.execute('drop function makeloyal cascade;')
# cur.execute('drop trigger if exists logtableupd on service ')
# # cur.execute('drop function insertlogtable cascade')
# cur.execute('DROP TABLE IF EXISTS customer cascade;')
# cur.execute('DROP TABLE IF EXISTS logtable cascade;')
# cur.execute('DROP TABLE IF EXISTS service cascade;')
# cur.execute('DROP TABLE IF EXISTS accessory cascade;')
# cur.execute('DROP TABLE IF EXISTS room cascade;')
# cur.execute('DROP TABLE IF EXISTS payments cascade;')
# cur.execute('DROP TABLE IF EXISTS service_taken cascade ;')
# cur.execute('DROP TABLE IF EXISTS rooms_booked cascade;')

cur.execute("""CREATE TABLE customer(
customer_ID SERIAL PRIMARY KEY,
TOTAL_PAYED INT NOT NULL  default 0 check(total_payed >= 0),
TOTAL_DUE      INT  default 0 NOT NULL,
loyalty int default 0,
NAME TEXT NOT NULL,
PHONE_NO TEXT NOT NULL,
AGE INT,
lastexit timestamp 
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

cur.execute("""
create type rtype as enum ('premium','basic','ac','non-ac');
CREATE TABLE ROOM(
ROOM_NO int primary key,
ROOM_COST INT ,
ROOM_TYPE text,
ROOM_SIZE INT
);""")

cur.execute("""CREATE TABLE PAYMENTS
(
PAYMENT_ID SERIAL PRIMARY KEY ,
customer_ID SERIAL ,
AMOUNT NUMERIC NOT NULL ,
STATUS text NOT NULL,
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
cur.execute("""

CREATE OR REPLACE procedure book_room(cust_id int , in_date timestamp, out_date timestamp, type text, SIZ INT)
language plpgsql
as $$
declare
	varu int;
	cost numeric;
	rno int;
begin

if exists
(SELECT room_no 
	from room where room_type = type and  ROOM_SIZE = SIZ and not exists ( select room_no from rooms_booked where (((room_indate between in_date and out_date))or(room_outdate between in_date and out_date )) and rooms_booked.room_no = room.room_no and room.room_type = type) )
	
then
	select room_cost ,room_no into cost,rno  from room where room_type = type and ROOM_SIZE = SIZ and not exists ( select room_no from rooms_booked where (((room_indate between in_date and out_date))or(room_outdate between in_date and out_date )) and rooms_booked.room_no = room.room_no and room.room_type = type) limit 1 ;
	
	
	insert into payments (customer_id,amount,status,payment_type,room_no,DATE_OF_INITIATION,DATE_OF_completion) values(cust_id,cost,'PAID','BOOKING',rno,now(),now()) returning payment_id into varu;
	
	
	insert into rooms_booked values(varu,rno,in_date,out_date);
	raise notice ' room was booked successfull';
else 

 raise notice 'room on exact date was not availaible you can use closest function';
 

end if;

end;
$$;
""")

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
after update of total_payed or insert
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
	 update customer set total_due = total_due + new.amount;
	elsif new.status = 'paid'
	then 
	 update customer set total_payed = total_payed + new.amount;
	elsif new.status = 'cancelled' and old.status = 'due'
	then
	 update customer set total_due = total_due - new.amount;
	elsif new.status = 'cancelled' and old.status = 'paid'
	then
	 update customer set total_payed = total_payed - new.amount;
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

create or replace function closest(in_date timestamp, out_date timestamp, type text,SIZ int)
returns table (inn_date timestamp,outt_date timestamp)
language plpgsql
as $$
begin
	return query (select t.day,t.day + interval '4 day' from
(SELECT * FROM   generate_series

(in_date, in_date + interval '30 day', interval  '1 day') )AS t(day)

, room where room_type = type and room_size = SIZ and room_no in (SELECT room_no from room where not exists ( select room_no from rooms_booked where (((room_indate between t.day and (t.day+

 (out_date - in_date ) ))or(room_outdate between t.day and (t.day +  (out_date - in_date ) )) and rooms_booked.room_no = room.room_no )))));
 
end;
$$;
create table waiting(
	waiting_id serial primary key,
	customer_id int ,
	accessory_id int,
	quantity int,
	beffore timestamp
);
create or replace function lookupacc(customerid int,id int,quantity int,whenn timestamp)
returns text
language plpgsql
as $$
declare
	cus int;

begin
		if exists (select accessory.accessor_cost from accessory where accessory_id = id and quantity <= QUANTITY_AVAILABLE)
		then
		select accessory.accessor_cost into cus from accessory where accessory_id = id and quantity <= QUANTITY_AVAILABLE;
		cus = cus*quantity;
		insert into payments(customer_id,amount,status,payment_type,accessory_id,DATE_OF_INITIATION) values(customerid,cus,'paid','accessory',id,current_timestamp);
		return 'accessory availaible inserted into payments';
		else
		insert into waiting(
	customer_id ,
	accessory_id ,
	quantity ,
	beffore) values(customerid,id,quantity,whenn);
		return 'accessory not availaible currently so inserted in waiting';
		end if;
end;
$$;

create or replace function funfindwho()
returns trigger
language plpgsql
as $$
declare 
	wt int;
	cus int;
	wq int;
	iid int;

begin
		if exists (select * from waiting 
		where timestamp > current_timestamp and new.accessory_id = waiting.accessory_id and new.quantity > waiting.quantity
		 order by waiting_id limit 1)
		 then
		 	select waiting_id into wt from waiting 
		where timestamp > current_timestamp and new.accessory_id = waiting.accessory_id and new.quantity > waiting.quantity
		 order by waiting_id limit 1;
		 	select customer_id into cus from waiting 
		where timestamp > current_timestamp and new.accessory_id = waiting.accessory_id and new.quantity > waiting.quantity
		 order by waiting_id limit 1;
		 	select waiting.quantity into wq from waiting 
		where timestamp > current_timestamp and new.accessory_id = waiting.accessory_id and new.quantity > waiting.quantity
		 order by waiting_id limit 1;
		 	select waiting.accessory_id into iid from waiting 
		where timestamp > current_timestamp and new.accessory_id = waiting.accessory_id and new.quantity > waiting.quantity
		 order by waiting_id limit 1;
		 	
			insert into payments(customer_id,amount,status,payment_type,accessory_id,DATE_OF_INITIATION) values(cus,new.ACCESSOR_COST*wq,'due','accessory',iid,current_timestamp); 
			update accessory set QUANTITY_AVAILABLE = QUANTITY_AVAILABLE - wq where accessory_id = iid;
		return new;
		end if;
		return new;
end;
$$;


create trigger findwho
after update 
on accessory
for each row
execute procedure funfindwho();


CREATE OR REPLACE procedure forservice(cust_id int , in_date timestamp, out_date timestamp, whservice text )
language plpgsql
as $$
declare
	varu int;
	rno int;
	pid int;
begin

if exists
(SELECT service_id from service where
 service_type = whservice and 
	not exists ( select service_id from service_taken where (((starttime between in_date and out_date))or(endtime between in_date and out_date )) and service.service_id= service_taken.service_id ))
	
then
	SELECT service_id,service_rate into varu, rno 
    from service where 
    service_type = whservice and 
	not exists ( select service_id from service_taken where (((starttime between in_date and out_date))or(endtime between in_date and out_date )) and service.service_id= service_taken.service_id ) limit 1;
	
	
	insert into payments (customer_id,amount,status,payment_type,service_id,DATE_OF_INITIATION,DATE_OF_completion) values(cust_id,cast(rno as numeric),'PAID','SERVICE',varu,now(),now()) returning payment_id into pid;
	
	
	insert into service_taken values(pid,varu,in_date,out_date);
	raise notice 'service was availaible';
else 

 raise notice 'not availaible';
 

end if;

end;
$$;

""")
vals = [[1,20,'premium',4],[2,10,'basic',3],[3,5,'ac',5],[4,5,'non-ac',2]]
for val in vals:
    cur.execute('insert into room values(%s,%s,%s,%s)',val)

vals = [[1,'bed',5,4],[2,'brush',5,3],[3,'soap',5,5],[4,'pillow',5,2]]
for val in vals:
    cur.execute('insert into accessory values(%s,%s,%s,%s)',val)
vals = [[1,'massage',5],[2,'roomclean',5],[3,'laundry',5],[4,'satishservice',5]]
for val in vals:
    cur.execute('insert into service values(%s,%s,%s)',val)
cur.execute("insert into customer values(1,0,0,0,'shubh','123',12,current_timestamp)")
cur.execute("insert into customer values(2,0,0,0,'pratham','123',12,current_timestamp)")
cur.execute("delete from customer ")
cur.execute("insert into customer values(1,0,0,0,'shubh','123',12,current_timestamp)")
conn.commit()

cur.close()
conn.close()