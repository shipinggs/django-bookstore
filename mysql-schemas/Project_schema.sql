CREATE DATABASE django_db;
USE django_db;

CREATE TABLE books (
	ISBN13 CHAR(14) NOT NULL UNIQUE PRIMARY KEY,
    ISBN10 CHAR(10) NOT NULL UNIQUE,
    title VARCHAR(256) NOT NULL,
    author VARCHAR(256),
    publisher VARCHAR(256),
    year INT,
    num_copies INT CHECK(num_copies>=0),
    price REAL CHECK(price>=0),
    book_format CHAR(9) CHECK(format = 'paperback' OR format='hardcover'),
    keyword VARCHAR(256),
    book_subject VARCHAR(256));
    
CREATE TABLE customers (
	login_name VARCHAR(256) PRIMARY KEY,
    fullname VARCHAR(256),
    login_password VARCHAR(256) NOT NULL,
    credit_card VARCHAR(16) CHECK( LEN(credit_card)=16),
    address VARCHAR(256),
    phone_num INT );
    
CREATE TABLE orders (
	login_name VARCHAR(256),
    ISBN13 CHAR(14),
    num_order INT CHECK(num_order>0),
    order_date DATE,
    order_status VARCHAR(256),
    PRIMARY KEY (login_name,ISBN13),
    FOREIGN KEY (login_name) REFERENCES customers(login_name),
    FOREIGN KEY (ISBN13) REFERENCES books(ISBN13));
    
CREATE TABLE feedbacks(
	login_name VARCHAR(256),
    ISBN13 CHAR(14),
    feedback_score INT CHECK (feedback_score>=0 AND feedback_score<=10),
    feedback_text VARCHAR(256),
    feedback_date DATE,
    PRIMARY KEY( login_name, ISBN13),
    FOREIGN KEY (login_name) REFERENCES customers(login_name),
    FOREIGN KEY (ISBN13) REFERENCES books(ISBN13));
      
CREATE TABLE rates(
	rater VARCHAR(256)  NOT NULL,
    rated VARCHAR(256)  NOT NULL,
    rating INT  NOT NULL CHECK (rating <=10 AND rating >=1),
    ISBN13 CHAR(14) NOT NULL,
    PRIMARY KEY ( rater, rated, ISBN13),
    FOREIGN KEY (rater) REFERENCES customers(login_name),
    FOREIGN KEY (rated) REFERENCES customers(login_name),
    FOREIGN KEY (ISBN13) REFERENCES books(ISBN13));    
