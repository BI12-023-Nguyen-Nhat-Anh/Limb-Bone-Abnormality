drop database if exists Account;
create database Account;
use Account; 
drop table if exists User;
drop table if exists File;
create table User(
	id int(10) auto_increment primary key,
    email text,
    username text,
    password text
);
create table File(
	id int(10) auto_increment primary key,
    data BLOB,
    date datetime,
    user_id int(10),
    foreign key(user_id) references User(id)
)auto_increment = 1;
