DROP DATABASE IF EXISTS schooldb;
CREATE DATABASE  schooldb;

USE schooldb;

-- ==========================================================
-- Teachers
-- ==========================================================

CREATE TABLE teachers (
    Gmail VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL
);

-- ==========================================================
-- Students
-- ==========================================================

CREATE TABLE students (
    roll_no INT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    class INT NOT NULL CHECK (class BETWEEN 1 AND 12),
    section CHAR(1) NOT NULL CHECK (section IN ('A','B','C'))
);

-- ==========================================================
-- Exams
-- ==========================================================

CREATE TABLE exams (
    exam_id INT AUTO_INCREMENT PRIMARY KEY,
    exam_name VARCHAR(50) NOT NULL UNIQUE
);

-- ==========================================================
-- Marks
-- ==========================================================

CREATE TABLE marks (
    roll_no INT NOT NULL,
    class INT NOT NULL,
    exam_id INT NOT NULL,
    subject VARCHAR(30) NOT NULL,
    marks INT DEFAULT 0,

    PRIMARY KEY (roll_no, exam_id, subject),

    FOREIGN KEY (roll_no)
        REFERENCES students(roll_no)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (exam_id)
        REFERENCES exams(exam_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CHECK (marks BETWEEN 0 AND 100 OR marks IS NULL)
);

-- ==========================================================
-- Useful Indexes
-- ==========================================================

CREATE INDEX idx_student_class
ON students(class, section);

CREATE INDEX idx_marks_subject
ON marks(subject);

CREATE INDEX idx_marks_exam
ON marks(exam_id);