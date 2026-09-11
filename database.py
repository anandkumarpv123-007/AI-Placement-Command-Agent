import sqlite3

DB_NAME = "placement.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        cgpa REAL NOT NULL,
        branch TEXT NOT NULL,
        graduation_year INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        min_cgpa REAL NOT NULL,
        required_skills TEXT NOT NULL,
        package_lpa REAL NOT NULL,
        location TEXT
    );

    CREATE TABLE IF NOT EXISTS student_skills (
        student_id INTEGER,
        skill TEXT,
        level TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id)
    );

    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        job_id INTEGER,
        status TEXT,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    );
    """)

    conn.commit()
    conn.close()


def get_student(student_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()
    conn.close()

    return dict(row) if row else None


def get_student_skills(student_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT skill, level FROM student_skills WHERE student_id = ?",
        (student_id,)
    ).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_jobs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM jobs").fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_application(student_id, job_id):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO applications (student_id, job_id, status)
        VALUES (?, ?, ?)
        """,
        (student_id, job_id, "Recommended")
    )

    conn.commit()
    conn.close()