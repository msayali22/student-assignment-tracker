create database login_details;
use login_details;
create table user(userid varchar(100) not null,
					name varchar(100),
					email varchar(100),
					password varchar(100),
					user_type varchar(100),
					primary key(userid)
				 );

create table assignment(assignmentid varchar(100) not null,
					title varchar(100),
					description varchar(1000),
					submission_due_date varchar(100),
					primary key(assignmentid)
				 );
					
create table submission(submissionid varchar(100),
					assignmentid varchar(100),
					userid varchar(100), 
					submission_date varchar(100),
					solution varchar(1000),
					status varchar(100),
					foreign key(assignmentid) references assignment(assignmentid),
					foreign key(userid) references user(userid)
					
				 );
				