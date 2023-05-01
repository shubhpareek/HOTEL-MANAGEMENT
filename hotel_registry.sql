CREATE TABLE customer(
customer_ID SERIAL PRIMARY KEY,
TOTAL_PAYED INT NOT NULL  check(total_payed >= 0),
TOTAL_DUE     INT  NOT NULL,
NAME TEXT NOT NULL,
PHONE_NO TEXT NOT NULL,
AGE INT 
);

CREATE TABLE SERVICE(
SERVICE_ID  INT PRIMARY KEY ,
SERVICE_TYPE TEXT NOT NULL,
SERVICE_RATE INT NOT NULL 
);

CREATE TABLE ACCESSORY
(
ACCESSORY_ID  INT PRIMARY KEY, 
ACCESSORY_TYPE TEXT NOT NULL,
ACCESSOR_COST INT NOT NULL, 
QUANTITY_AVAILABLE INT NOT NULL
);

CREATE TABLE ROOM(
ROOM_NO int primary key,
ROOM_COST INT ,
ROOM_TYPE TEXT
);

CREATE TABLE PAYMENTS
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
);


CREATE TABLE SERVICE_TAKEN(
PAYMENT_ID SERIAL primary key,
service_id int ,
starttime timestamp,
endtime timestamp,
foreign key(service_id)
references service(service_id),
foreign key(payment_id)
references payments(payment_id)

);

create table rooms_booked (
PAYMENT_ID SERIAL primary key,
room_no int ,
room_indate timestamp not null,
room_outdate timestamp not null,
foreign key(payment_id)
references payments(payment_id),
FOREIGN KEY(ROOM_NO)
REFERENCES ROOM(ROOM_NO)
);

select room_no,t.day,t.day + interval '4 day' from
(SELECT * FROM   generate_series
(timestamp '2004-03-07', timestamp '2004-08-16', interval  '1 day') )AS t(day)
, room where room_no in (SELECT room_no from room where not exists ( select room_no from rooms_booked where (((room_indate between t.day and (t.day+  interval '4 day'))or(room_outdate between t.day and (t.day +  interval '4 day') )) and rooms_booked.room_no = room.room_no)));

insert into table rooms_booked values()

create type mytype as(ind timestamp,outd timestamp);


insert into payments (customer_id,amount,status,payment_type,room_no,DATE_OF_INITIATION,DATE_OF_completion) (select cust_id,room_cost,'PAID','BOOKING',room_no,now(),now() from room where not exists ( select room_no from rooms_booked where (((room_indate between in_date and out_date))or(room_outdate between in_date and out_date )) and rooms_booked.room_no = room.room_no and room.room_type = type) limit 1) returning payment_id into varu;



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
	from room where not exists ( select room_no from rooms_booked where (((room_indate between in_date and out_date))or(room_outdate between in_date and out_date )) and rooms_booked.room_no = room.room_no and room.room_type = type)AND ROOM_SIZE = SIZ)
	
then
	select room_cost ,room_no into cost,rno  from room where not exists ( select room_no from rooms_booked where (((room_indate between in_date and out_date))or(room_outdate between in_date and out_date )) and rooms_booked.room_no = room.room_no and room.room_type = type) AND ROOM_SIZE = SIZ limit 1 ;
	
	
	insert into payments (customer_id,amount,status,payment_type,room_no,DATE_OF_INITIATION,DATE_OF_completion) values(cust_id,cost,'PAID','BOOKING',rno,now(),now()) returning payment_id into varu;
	
	
	insert into rooms_booked values(varu,rno,in_date,out_date);
else 

 raise notice 'room on exact date was not availaible you can use closest function';
 

end if;

end;
$$;

PAYMENT_ID SERIALPRIMARY KEY,
customer_ID SERIAL ,
AMOUNT NUMERIC NOT NULL ,
STATUS TEXT NOT NULL,
PAYMENT_TYPE TEXT NOT NULL,
SERVICE_ID INT ,
ROOM_NO INT,
ACCESSORY_ID INT ,
DATE_OF_INITIATION timestamp,
DATE_OF_COMPLETION timestamp,




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


select distinct(room.room_type) 
from room,payments,rooms_booked 
where 
room.room_no=payments.room_no 
and payments.customer_id = 1 
and payments.payment_id= rooms_booked.payment_id  
and now() between room_indate and room_outdate 
and payment_type = 'BOOKING';


select accessory.accessory_type 
from accessory,payments 
where  payments.customer_id = 1 
and payments.accessory_id = accessory.accessory_id  
and payment_type = 'accessory' and status = 'due';


select service.service_type 
from service,payments 
where payments.customer_id = 1 
and payment_type = 'service' 
and status = 'due' 
and service.service_id = payments.service_id;

select distinct(customer.name,customer.customer_id) 
from customer,payments,rooms_booked 
where customer.customer_id = payments.customer_id
and payments.payment_id = rooms_booked.payment_id 
and cast ('2023-03-06'as timestamp) 
between rooms_booked.room_indate and room_outdate;

select count(*) 
from room 
join rooms_booked 
on room.room_no=rooms_booked.room_no  
where room.room_type = 'small';

create role receptionist;

grant select on room,service,accessory,payments to receptionist;

grant select on rooms_booked to receptionist;

grant select,insert,delete,update on customer to receptionist;
grant insert,delete,update on payments to receptionist;
grant insert,delete,update on rooms_booked to receptionist;

create role manager ;

grant select,insert,delete,update on accessory to manager;


create role cleaner;

create view cleaner_appointments as (select * from service_taken where service_id = 1);

grant select on cleaner_appointments to cleaner;

create role hotel_owner superuser login password '1234' ;

create view not_available_accessory as (select accessory_type from accessory where quantity = 0);



ALTER TABLE PAYMENTS ADD CONSTRAINT MyUniqueConstraint AUTO_INCREMENT(payment_id);

create table message(
	time timestamp,
	source text,
	msg text
)










create or replace function makeloyal()
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
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'stat') THEN
	create type stat as enum ('paid', 'due','cancelled');        
    END IF;
END$$;

create type stat as enum ('paid', 'due','cancelled');

create or replace function updtotalpaid()
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



create trigger loyalty
after update or insert
on customer
for each row 
execute procedure makeloyal();


create trigger updtotalpayed
after insert on
payments
for each row
execute procedure updtotalpaid();





create table logtable(
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
		if exists (select accesor_cost*quantity into cus from accessory where accessory_id = id and quantity <= QUANTITY_AVAILABLE)
		then
		insert into payments(customer_id,amount,status,payment_type,accessory_id,DATE_OF_INITIATION) values(customerid,cus,'accessory',id,current_timestamp);
		return 'accessory availaible inserted into payments'
		else
		insert into waiting(
	customer_id ,
	accessory_id ,
	quantity ,
	beffore) values(customerid,id,quantity,whenn);
		return 'accessory not availaible currently so inserted in waiting'
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
execute procedure ;





CREATE OR REPLACE procedure forservice(cust_id int , in_date timestamp, out_date timestamp, whservice text )
language plpgsql
as $$
declare
	varu int;
	rno int;
	pid int;
begin

if exists
(SELECT service_id 
	from service where not exists ( select service_id from service_taken where (((startime between in_date and out_date))or(endtime between in_date and out_date )) and service.service_id= service_taken.service_id )AND service_type = whservice)
	
then
	SELECT service_id,service_rate into varu, rno 
	from service where not exists ( select service_id from service_taken where (((startime between in_date and out_date))or(endtime between in_date and out_date )) and service.service_id= service_taken.service_id )AND service_type = whservice limit 1;
	
	
	insert into payments (customer_id,amount,status,payment_type,service_id,DATE_OF_INITIATION,DATE_OF_completion) values(cust_id,cast(rno as numeric),'PAID','SERVICE',varu,now(),now()) returning payment_id into pid;
	
	
	insert into service_taken values(pid,varu,in_date,out_date);
	raise notice 'service was availaible';
else 

 raise notice 'not availaible';
 

end if;

end;
$$;
status message 


query for finall bill 

select payments.payment_type,amount,status,DATE_OF_INITIATION from payments,customer
where payments.customer_id = %s% and DATE_OF_INITIATION > lastexit and customer.customer_id = payments.customer_id;


CREATE OR REPLACE procedure finalpayment(cust_id int)
language plpgsql
as $$
begin
update payments set status='paid' where customer_ID=cust_id;
update customer set lastexit=current_timestamp; 
end;
$$;

-- amount , type , size , status , room_no , date of initiation
select p.amount,r.type,r.size,p.status,r.room_no,p.DATE_OF_INITIATION,p.payment_id from payments as p,rooms_booked as rb,room as r where payments.customer_id = %s and payments.payment_id =
rooms_booked.payment_id and room_indate >= current_timestamp and r.room_no = rb.room_no and payments.payment_type = 'BOOKING' ;