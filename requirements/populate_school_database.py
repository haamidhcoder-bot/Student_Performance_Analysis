try:
    import random
    import mysql.connector as sql

    # Update these if needed
    DB_CONFIG = {
        "host": "127.0.0.1",
        "user": "root",
        "password": "pass12345",#put ur database password
    }

    conn = sql.connect(**DB_CONFIG)
    cur = conn.cursor()

    with open(r"C:\Users\dell\Desktop\Student_Performance_Analysis\requirements\school_database_schema.sql") as f:
        queries=f.read()

    # Split statements using ';'
    for statement in queries.split(';'):
        statement = statement.strip()

        if statement:
            try:
                cur.execute(statement)
                conn.commit()
            except Exception as e:
                print(f"Error:{e}")

    # Teachers
    teachers = [
        ("teacher1", "pass123"),
        ("teacher2", "pass456"),
        ("teacher3", "pass789")
    ]
    cur.executemany(
        "INSERT INTO teachers VALUES(%s,%s)",
        teachers
    )

    # Exams
    exam_names = [
        "Unit Test 1",
        "Quarterly Exam",
        "Half Yearly Exam",
        "Unit Test 2",
        "Annual Exam"
    ]
    cur.executemany(
        "INSERT INTO exams(exam_name) VALUES(%s)",
        [(e,) for e in exam_names]
    )

    subjects_1_10 = ["English", "Maths", "Social", "Science", "Tamil"]
    subjects_11_12 = ["English", "Maths", "Physics", "Chemistry", "Computer"]

    # Students and marks
    for cls in range(1, 13):
        for i in range(1, 21):
            roll_no = cls * 100 + i
            name = f"Student_{cls}_{i}"

            cur.execute(
                "INSERT INTO students(roll_no, student_name, class, section) VALUES(%s,%s,%s,%s)",
                (roll_no, name, cls, "A")
            )

            subjects = subjects_1_10 if cls <= 10 else subjects_11_12

            for exam_id in range(1, 6):
                for subject in subjects:
                    mark = random.randint(35, 100)
                    cur.execute(
                        "INSERT INTO marks(roll_no, exam_id, subject, marks) VALUES(%s,%s,%s,%s)",
                        (roll_no, exam_id, subject, mark)
                    )

    conn.commit()
    conn.close()

    print("Database populated successfully!")

except Exception as e:
    print(f"ERROR:{e}")
