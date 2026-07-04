
CREATE DATABASE IF NOT EXISTS schooldb;
USE schooldb;

CREATE TABLE IF NOT EXISTS teachers (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS students (
    roll_no INT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    class INT NOT NULL,
    section CHAR(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS marks (
    roll_no INT NOT NULL,
    exam_id INT NOT NULL,
    subject VARCHAR(50) NOT NULL,
    marks INT NOT NULL,

    PRIMARY KEY (roll_no, exam_id, subject),

    FOREIGN KEY (roll_no)
        REFERENCES students(roll_no)
        ON DELETE CASCADE,

    FOREIGN KEY (exam_id)
        REFERENCES exams(exam_id)
        ON DELETE CASCADE
);
