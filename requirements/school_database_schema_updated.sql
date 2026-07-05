CREATE DATABASE IF NOT EXISTS schooldb;
USE schooldb;

CREATE TABLE IF NOT EXISTS teachers (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    roll_no INT,
    student_name VARCHAR(100) NOT NULL,
    class INT NOT NULL,
    section CHAR(1) NOT NULL,
    subject VARCHAR(10),
    marks INT,
    PRIMARY KEY (roll_no)
);
