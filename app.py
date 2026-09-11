import streamlit as st
import sqlite3
import pandas as pd

from agent import PlacementAgent
from database import get_connection


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Placement Command Agent",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# DATABASE ANALYTICS
# ============================================================

def get_dashboard_stats():

    conn = get_connection()

    students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    companies = conn.execute(
        "SELECT COUNT(DISTINCT company) FROM jobs"
    ).fetchone()[0]

    jobs = conn.execute(
        "SELECT COUNT(*) FROM jobs"
    ).fetchone()[0]

    applications = conn.execute(
        "SELECT COUNT(*) FROM applications"
    ).fetchone()[0]

    conn.close()

    return students, companies, jobs, applications


def get_skill_gaps():

    conn = get_connection()

    rows = conn.execute("""
        SELECT required_skills
        FROM jobs
    """).fetchall()

    conn.close()

    skill_counts = {}

    for row in rows:
        skills = row[0].split(",")

        for skill in skills:
            skill = skill.strip()

            skill_counts[skill] = (
                skill_counts.get(skill, 0) + 1
            )

    return sorted(
        skill_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )


# ============================================================
# GET STUDENTS FROM DATABASE
# ============================================================

def get_students():

    conn = get_connection()

    rows = conn.execute("""
        SELECT id, name, branch, cgpa
        FROM students
        ORDER BY id
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ============================================================
# HEADER
# ============================================================

st.title("🎯 AI Placement Command Agent")

st.caption(
    "Autonomous University Placement Management • PS-02"
)

st.divider()


# ============================================================
# DASHBOARD
# ============================================================

st.subheader("📊 Placement Command Center")

students, companies, jobs, applications = get_dashboard_stats()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "👨‍🎓 Students",
    students
)

col2.metric(
    "🏢 Active Companies",
    companies
)

col3.metric(
    "💼 Open Opportunities",
    jobs
)

col4.metric(
    "📝 Applications",
    applications
)


# ============================================================
# SKILL ANALYTICS
# ============================================================

col_left, col_right = st.columns(2)

with col_left:

    st.markdown("### 📈 Placement Overview")

    overview_data = pd.DataFrame({
        "Metric": [
            "Students",
            "Companies",
            "Open Jobs",
            "Applications"
        ],
        "Count": [
            students,
            companies,
            jobs,
            applications
        ]
    })

    st.dataframe(
        overview_data,
        use_container_width=True,
        hide_index=True
    )


with col_right:

    st.markdown("### 🔍 Industry Skill Demand")

    gaps = get_skill_gaps()

    if gaps:

        skill_df = pd.DataFrame(
            gaps,
            columns=["Skill", "Job Requirements"]
        )

        st.dataframe(
            skill_df,
            use_container_width=True,
            hide_index=True
        )


st.divider()


# ============================================================
# AGENT CONTROL
# ============================================================

st.subheader("🤖 AI Placement Agent")

with st.sidebar:

    st.header("⚙️ Agent Control")

    # Get students directly from database
    students_list = get_students()

    student_options = {
        f"{student['id']} — {student['name']} "
        f"({student['branch']}, CGPA {student['cgpa']})":
        student["id"]
        for student in students_list
    }

    selected_student = st.selectbox(
        "Select Student",
        options=list(student_options.keys())
    )

    student_id = student_options[selected_student]

    st.markdown("---")

    st.info(
        "The agent can retrieve student data, "
        "discover opportunities, evaluate eligibility, "
        "analyze skill gaps and generate recommendations."
    )


request = st.text_area(
    "Placement Request",
    value=(
        f"Find the best placement opportunities for "
        f"student {student_id} and tell me what they "
        f"need to improve before applying."
    ),
    height=100
)


# ============================================================
# RUN AGENT
# ============================================================

if st.button(
    "🚀 Run Placement Agent",
    type="primary",
    use_container_width=True
):

    try:

        agent = PlacementAgent()

        with st.spinner(
            "🧠 Agent is analyzing placement opportunities..."
        ):

            result = agent.run(request)

        st.success(
            "✅ Placement analysis completed successfully."
        )


        # ====================================================
        # AGENT EXECUTION TRACE
        # ====================================================

        st.subheader("⚡ Agent Execution Trace")

        events = result.get("events", [])

        for index, event in enumerate(events, start=1):

            if event["type"] == "agent":

                st.write(
                    f"**{index}. 🧠 Agent** — "
                    f"{event['message']}"
                )

            elif event["type"] == "tool":

                st.write(
                    f"**{index}. 🔧 Tool `{event['tool']}`** — "
                    f"{event['message']}"
                )


        st.divider()


        # ====================================================
        # AI RECOMMENDATION
        # ====================================================

        st.subheader("📋 AI Recommendation")

        st.markdown(
            result.get(
                "answer",
                "No recommendation generated."
            )
        )


        st.divider()


        # ====================================================
        # PLACEMENT MATCHES
        # ====================================================

        st.subheader("🏢 Candidate–Company Matching")

        matches = result.get(
            "data",
            {}
        ).get(
            "matches",
            []
        )


        if matches:

            for job in matches:

                score = job["match_score"]

                if score >= 90:

                    status = "🟢 Excellent Match"

                elif score >= 75:

                    status = "🟡 Good Match"

                else:

                    status = "🔴 Skill Development Required"


                with st.container(border=True):

                    c1, c2, c3, c4 = st.columns(4)

                    c1.metric(
                        "Company",
                        job["company"]
                    )

                    c2.metric(
                        "Match Score",
                        f"{score}%"
                    )

                    c3.metric(
                        "Package",
                        f"₹{job['package_lpa']} LPA"
                    )

                    c4.write(
                        f"**Status**\n\n{status}"
                    )


                    st.write(
                        f"**Role:** {job['role']}  \n"
                        f"**Location:** {job['location']}"
                    )


                    if job.get("matched_skills"):

                        st.write(
                            "**Matched Skills:** "
                            + ", ".join(
                                job["matched_skills"]
                            )
                        )


                    if job.get("skill_gaps"):

                        st.warning(
                            "⚠️ Skill Gaps: "
                            + ", ".join(
                                job["skill_gaps"]
                            )
                        )

                    else:

                        st.success(
                            "✅ No major skill gaps identified."
                        )



        else:

            st.warning(
                "No eligible opportunities found."
            )


    except Exception as e:

        st.error(
            "❌ Agent failed to run."
        )

        st.code(str(e))


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Placement Command Agent • "
    "Explainable • Data-driven • Tool-enabled"
)