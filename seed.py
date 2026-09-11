from database import get_connection, init_db


def seed_data():
    init_db()

    conn = get_connection()
    cur = conn.cursor()

    # Clear existing demo data
    cur.execute("DELETE FROM student_skills")
    cur.execute("DELETE FROM applications")
    cur.execute("DELETE FROM students")
    cur.execute("DELETE FROM jobs")

    students = [
        (1042, "Anand Kumar", 8.7, "CSE", 2029),
        (1043, "Rahul Sharma", 8.2, "CSE", 2029),
        (1044, "Priya Reddy", 9.1, "CSE", 2029),
        (1045, "Vikram Singh", 7.8, "ECE", 2029),
        (1046, "Sneha Rao", 8.9, "CSE", 2029),
    ]

    jobs = [
        (1, "TCS", "Software Engineer", 7.5,
         "Python,SQL,DSA,Git", 7.5, "Hyderabad"),

        (2, "Infosys", "Python Developer", 7.0,
         "Python,SQL,Git", 6.5, "Bangalore"),

        (3, "Microsoft", "Software Engineer Intern", 8.5,
         "Python,DSA,Git,Cloud", 20.0, "Bangalore"),

        (4, "Deloitte", "Technology Analyst", 7.5,
         "Python,SQL,Communication", 9.0, "Hyderabad"),

        (5, "Amazon", "SDE Intern", 8.0,
         "Python,DSA,Cloud,Git", 18.0, "Bangalore"),
    ]

    skills = [
        (1042, "Python", "Advanced"),
        (1042, "SQL", "Intermediate"),
        (1042, "DSA", "Intermediate"),
        (1042, "Git", "Intermediate"),

        (1043, "Python", "Intermediate"),
        (1043, "SQL", "Advanced"),
        (1043, "DSA", "Beginner"),

        (1044, "Python", "Advanced"),
        (1044, "SQL", "Advanced"),
        (1044, "DSA", "Advanced"),
        (1044, "Git", "Advanced"),
        (1044, "Cloud", "Intermediate"),

        (1045, "Python", "Intermediate"),
        (1045, "SQL", "Intermediate"),

        (1046, "Python", "Advanced"),
        (1046, "DSA", "Advanced"),
        (1046, "Git", "Advanced"),
        (1046, "Cloud", "Intermediate"),
    ]

    cur.executemany(
        "INSERT INTO students VALUES (?, ?, ?, ?, ?)",
        students
    )

    cur.executemany(
        "INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, ?)",
        jobs
    )

    cur.executemany(
        "INSERT INTO student_skills VALUES (?, ?, ?)",
        skills
    )

    conn.commit()
    conn.close()

    print("Database seeded successfully!")


if __name__ == "__main__":
    seed_data()