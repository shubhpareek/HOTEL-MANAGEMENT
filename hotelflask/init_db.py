import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, AsIs
conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user='newuser',
        password='password')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute("""DROP DATABASE IF EXISTS hotell;""")
cur.close()
conn.close()

conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user='newuser',
        password='password')
cur = conn.cursor()
cur.execute('drop role if exists receptionist;')
cur.execute('drop role if exists manager;')
for i in range(1,7):
    cur.execute('drop role if exists %s;',[AsIs('worker'+str(i))])
conn.commit()
cur.close()
conn.close()

conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user='newuser',
        password='password')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute('create database hotell;')
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
TOTAL_DUE INT  default 0 check(total_due >= 0) NOT NULL,
loyalty int default 0 check(loyalty >= 0 and loyalty <= 2),
NAME TEXT NOT NULL,
PHONE_NO TEXT NOT NULL,
AGE INT check(age > 0),
lastexit timestamp check(lastexit <= NOW()) 
);

create table message(
	time timestamp check(time <= NOW()),
	source text,
	msg text
)
""")

cur.execute("""CREATE TABLE SERVICE(
SERVICE_ID  INT PRIMARY KEY ,
SERVICE_TYPE TEXT NOT NULL,
SERVICE_RATE INT NOT NULL check(service_rate > 0) 
);""")

cur.execute("""CREATE TABLE ACCESSORY
(
ACCESSORY_ID  INT PRIMARY KEY, 
ACCESSORY_TYPE TEXT NOT NULL,
ACCESSOR_COST INT NOT NULL check(ACCESSOR_COST > 0), 
QUANTITY_AVAILABLE INT NOT NULL check(QUANTITY_AVAILABLE >= 0)
);""")

cur.execute("""
create type rtype as enum ('premium','basic','ac','non-ac');
CREATE TABLE ROOM(
ROOM_NO int primary key,
ROOM_COST INT check(room_cost > 0),
ROOM_TYPE text,
ROOM_SIZE INT check(room_size > 0)
);""")

cur.execute("""CREATE TABLE PAYMENTS
(
PAYMENT_ID SERIAL PRIMARY KEY ,
customer_ID INT ,
AMOUNT NUMERIC NOT NULL,
STATUS text NOT NULL,
PAYMENT_TYPE TEXT NOT NULL,
SERVICE_ID INT,
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
);
ALTER TABLE payments ADD CONSTRAINT pay_check
CHECK (amount >=0 AND 
date_of_initiation <= date_of_completion AND
date_of_initiation <= NOW());
""")


cur.execute("""CREATE TABLE SERVICE_TAKEN(
PAYMENT_ID SERIAL primary key,
service_id int ,
starttime timestamp,
endtime timestamp,
foreign key(service_id)
references service(service_id),
foreign key(payment_id)
references payments(payment_id)
);
ALTER TABLE service_taken ADD CONSTRAINT ser_tak_check
CHECK(starttime >= NOW() AND endtime >= starttime);
""")

cur.execute("""CREATE table rooms_booked (
PAYMENT_ID SERIAL primary key,
room_no int ,
room_indate timestamp not null,
room_outdate timestamp not null,
foreign key(payment_id)
references payments(payment_id),
FOREIGN KEY(ROOM_NO)
REFERENCES ROOM(ROOM_NO)
);
ALTER TABLE rooms_booked ADD CONSTRAINT room_b_check
CHECK(room_indate >= NOW() AND room_outdate >= room_indate)
""")

cur.execute("""create table logtable(
SERVICE_ID  INT PRIMARY KEY ,
SERVICE_TYPE TEXT NOT NULL,
SERVICE_RATE INT NOT NULL ,
time timestamp
);
create table waiting(
	waiting_id serial primary key,
	customer_id int ,
	accessory_id int,
	quantity int,
	beffore timestamp
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
lock payments in access exclusive mode;
lock rooms_booked in access exclusive mode;
if exists
(SELECT room_no 
	from room where room_type = type and  ROOM_SIZE = SIZ and not exists ( select room_no from rooms_booked where (((room_indate between in_date and out_date))or(room_outdate between in_date and out_date )) and rooms_booked.room_no = room.room_no and room.room_type = type) )
	
then
	select room_cost ,room_no into cost,rno  from room where room_type = type and ROOM_SIZE = SIZ and not exists ( select room_no from rooms_booked where (((room_indate between in_date and out_date))or(room_outdate between in_date and out_date )) and rooms_booked.room_no = room.room_no and room.room_type = type) limit 1 ;
	
	
	insert into payments (customer_id,amount,status,payment_type,room_no,DATE_OF_INITIATION,DATE_OF_completion) values(cust_id,ceil(cost*(extract (epoch from out_date - in_date))/3600),'PAID','BOOKING',rno,now(),now()) returning payment_id into varu;
	
	
	insert into rooms_booked values(varu,rno,in_date,out_date);
	insert into message values(current_timestamp,'system','room was booked');
	raise notice ' room was booked successfull';
else 

insert into message values(current_timestamp,'system','room could not be booked');
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
 insert into message values(current_timestamp,'system','a customer became loyal of second level') ;
 return new;
 elsif new.total_payed > 1000
 then 
 
 update customer set loyalty = 1
 where new.customer_id = customer.customer_id;
 insert into message values(current_timestamp,'system','a customer became loyal of first level') ;
 
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
	return query (select t.day,t.day +   (out_date - in_date ) from
(SELECT * FROM   generate_series

(in_date, in_date + interval '30 day', interval  '1 day') )AS t(day)

, room where room_type = type and room_size = SIZ and room_no in (SELECT room_no from room where not exists ( select room_no from rooms_booked where (((room_indate between t.day and (t.day+

 (out_date - in_date ) ))or(room_outdate between t.day and (t.day +  (out_date - in_date ) )) and rooms_booked.room_no = room.room_no )))));
 
end;
$$;

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
		insert into message values(current_timestamp,'system','an accessory was not found ,it will be availaible when manager updates');
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
		insert into message values(current_timestamp,'system','an accessory was found that was in waiting list');
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
	
	
	insert into payments (customer_id,amount,status,payment_type,service_id,DATE_OF_INITIATION,DATE_OF_completion) values(cust_id,cast(ceil(rno*(extract (epoch from out_date - in_date))/3600) as numeric),'PAID','SERVICE',varu,now(),now()) returning payment_id into pid;
	
	
	insert into service_taken values(pid,varu,in_date,out_date);
		insert into message values(current_timestamp,'system','an service was allotted');

	raise notice 'service was availaible';
else 

		insert into message values(current_timestamp,'system','an service was not availaible');
 raise notice 'not availaible';
 

end if;

end;
$$;

""")
vals = [[1,20,'premium',4],[2,10,'basic',3],[3,5,'ac',5],[4,5,'non-ac',2]]
for val in vals:
    cur.execute('insert into room values(%s,%s,%s,%s)',val)

vals = [[1,'bed',5,4],[2,'brush',5,3],[3,'soap',5,5],[4,'pillow',5,2],[5,'freshair',5,5]]
for val in vals:
    cur.execute('insert into accessory values(%s,%s,%s,%s)',val)
vals = [[1,'massage',5],[2,'roomclean',5],[3,'laundry',5],[4,'satishservice',5],[5,'massage',5],[6,'satishservice',5]]
for val in vals:
    cur.execute('insert into service values(%s,%s,%s)',val)
    cur.execute('create view %s as (select * from service_taken where service_id = %s and endtime >= current_timestamp);',[AsIs('for'+str(val[0])+'viewer'),str(val[0])])
    cur.execute('create role %s login password %s;',[AsIs('worker'+str(val[0])),'password'])
    cur.execute('grant select on %s to %s;',[AsIs('for'+str(val[0])+'viewer'),AsIs('worker'+str(val[0]))])
cur.execute("insert into customer values(1,0,0,0,'shubh','123',12,current_timestamp)")
cur.execute("insert into customer values(2,0,0,0,'pratham','123',12,current_timestamp)")
cur.execute("delete from customer ")
cur.execute("insert into customer(name,phone_no,age,lastexit) values('shubh','34','20',current_timestamp)")

cur.execute("""
CREATE OR REPLACE procedure finalpayment(cust_id int)
language plpgsql
as $$
begin
update payments set status='paid' where customer_ID=cust_id;
update customer set lastexit=current_timestamp; 
end;
$$;""")
            
cur.execute("""
create index roomsearchhelper on rooms_booked using btree(room_indate,room_outdate) INCLUDE(room_no);
""")
cur.execute("""
insert into message values(current_timestamp,'owner','hello , this is the first messge');
""")
cur.execute("""
create role receptionist login password 'password';
grant select on room,service,accessory to receptionist;
grant select,insert,delete,update on service_taken,customer,message,payments,rooms_booked to receptionist;
grant usage, select on all sequences in schema public to receptionist;	

create role manager login password 'password';
grant select,insert,delete,update on accessory,message to manager;
create view not_available_accessory as (select * from accessory where quantity_available = 0);
grant select on not_available_accessory to manager;
""")

conn.commit()

cur.close()
conn.close()