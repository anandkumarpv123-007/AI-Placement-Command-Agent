from database import (
    get_student,
    get_student_skills,
    get_jobs,
    create_application
)


def get_student_profile(student_id):
    """Retrieve complete student profile."""
    student = get_student(student_id)

    if not student:
        return {
            "success": False,
            "message": f"Student {student_id} not found."
        }

    skills = get_student_skills(student_id)

    return {
        "success": True,
        "student": student,
        "skills": skills
    }


def find_matching_jobs(student_id):
    """Find and rank suitable placement opportunities."""

    student = get_student(student_id)

    if not student:
        return {
            "success": False,
            "message": "Student not found."
        }

    skills_data = get_student_skills(student_id)
    student_skills = {
        s["skill"].lower() for s in skills_data
    }

    jobs = get_jobs()
    results = []

    for job in jobs:

        if student["cgpa"] < job["min_cgpa"]:
            continue

        required = [
            skill.strip().lower()
            for skill in job["required_skills"].split(",")
        ]

        matched = [
            skill for skill in required
            if skill in student_skills
        ]

        missing = [
            skill for skill in required
            if skill not in student_skills
        ]

        skill_score = (
            len(matched) / len(required) * 100
            if required else 0
        )

        # CGPA contributes 30%, skills contribute 70%
        cgpa_score = min(
            student["cgpa"] / 10 * 100,
            100
        )

        match_score = round(
            skill_score * 0.7 + cgpa_score * 0.3,
            1
        )

        results.append({
            "job_id": job["id"],
            "company": job["company"],
            "role": job["role"],
            "package_lpa": job["package_lpa"],
            "location": job["location"],
            "match_score": match_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "eligible": True
        })

    results.sort(
        key=lambda x: x["match_score"],
        reverse=True
    )

    return {
        "success": True,
        "student": student,
        "matches": results
    }


def check_eligibility(student_id, job_id):
    """Check whether a student satisfies a job's eligibility."""

    student = get_student(student_id)
    jobs = get_jobs()

    job = next(
        (j for j in jobs if j["id"] == job_id),
        None
    )

    if not student or not job:
        return {
            "eligible": False,
            "reason": "Student or job not found."
        }

    if student["cgpa"] < job["min_cgpa"]:
        return {
            "eligible": False,
            "reason": (
                f"CGPA {student['cgpa']} is below "
                f"required {job['min_cgpa']}"
            )
        }

    return {
        "eligible": True,
        "reason": "Academic eligibility satisfied."
    }


def generate_skill_gap(student_id, job_id):
    """Identify skills the student should improve."""

    student_skills = {
        s["skill"].lower()
        for s in get_student_skills(student_id)
    }

    jobs = get_jobs()

    job = next(
        (j for j in jobs if j["id"] == job_id),
        None
    )

    if not job:
        return {"success": False}

    required = [
        skill.strip()
        for skill in job["required_skills"].split(",")
    ]

    missing = [
        skill for skill in required
        if skill.lower() not in student_skills
    ]

    return {
        "success": True,
        "company": job["company"],
        "role": job["role"],
        "skill_gaps": missing
    }


def apply_to_job(student_id, job_id):
    """Create a placement application."""

    eligibility = check_eligibility(student_id, job_id)

    if not eligibility["eligible"]:
        return {
            "success": False,
            "message": eligibility["reason"]
        }

    create_application(student_id, job_id)

    return {
        "success": True,
        "message": "Application created successfully."
    }