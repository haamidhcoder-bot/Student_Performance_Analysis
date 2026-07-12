try:
    import random
    import mysql.connector as sql
    from person_names_720 import person_names

    # -------------------------
    # Database Configuration
    # -------------------------
    DB_CONFIG = {
        "host": "127.0.0.1",
        "user": "root",
        "password": "pass12345",
        }

    conn = sql.connect(**DB_CONFIG)
    cur = conn.cursor()

    import os

    schema_path = os.path.join(
        os.path.dirname(__file__),
        "school_database_schema_updated.sql"
    )

    with open(schema_path) as f:
        data = f.read()

    statements = [stmt.strip() for stmt in data.split(";") if stmt.strip()]
    for statement in statements:
        cur.execute(statement)

    cur.execute("use schooldb")
    # -------------------------
    # Teachers
    # -------------------------
    teachers = [
        ("teacher1", "pass123"),
        ("teacher2", "pass456"),
        ("teacher3", "pass789")
    ]

    cur.executemany(
        """
        INSERT INTO teachers(username,password)
        VALUES(%s,%s)
        """,
        teachers
    )

    # -------------------------
    # Exams
    # -------------------------
    exam_names = [
        "Unit Test 1",
        "Unit Test 2",
        "Quarterly Exam",
        "Half Yearly Exam",
        "Annual Exam"
    ]

    cur.executemany(
        """
        INSERT INTO exams(exam_name)
        VALUES(%s)
        """,
        [(exam,) for exam in exam_names]
    )

    conn.commit()

    # -------------------------
    # Get Exam IDs
    # -------------------------
    cur.execute("SELECT exam_id, exam_name FROM exams")

    exam_ids = {}

    for exam_id, exam_name in cur.fetchall():
        exam_ids[exam_name] = exam_id

    # -------------------------
    # Subjects
    # -------------------------
    subjects_1_10 = [
        "English",
        "Maths",
        "Science",
        "Social",
        "Tamil"
    ]

    subjects_11_12 = [
        "English",
        "Maths",
        "Physics",
        "Chemistry",
        "Computer"
    ]

    # -------------------------
    # Students
    # -------------------------

    sections = {
        "A":1,
        "B":2,
        "C":3
    }

    random.shuffle(person_names)

    name_index = 0

    for cls in range(1,13):

        subjects = subjects_1_10 if cls <= 10 else subjects_11_12

        for section in sections:

            for roll in range(1,21):

                roll_no = int(f"{cls}{sections[section]}{roll:02d}")

                student_name = person_names[name_index]
                name_index += 1

                cur.execute(
                    """
                    INSERT INTO students
                    (roll_no,student_name,class,section)
                    VALUES(%s,%s,%s,%s)
                    """,
                    (
                        roll_no,
                        student_name,
                        cls,
                        section
                    )
                )

                # -------------------------
                # Marks
                # -------------------------

                for exam in exam_names:

                    exam_id = exam_ids[exam]

                    for subject in subjects:
                        mark=random.randint(1,100)
                        cur.execute(
                            """
                            INSERT INTO marks
                            (roll_no,class,exam_id,subject,marks)
                            VALUES(%s,%s,%s,%s,%s)
                            """,
                            (
                                roll_no,
                                cls,
                                exam_id,
                                subject,
                                mark
                            )
                        )

    conn.commit()
    conn.close()

    print("Database populated successfully!")

except Exception as e:
    print(f"ERROR:{e}")

