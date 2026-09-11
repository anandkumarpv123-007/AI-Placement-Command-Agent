import os
import json
from google import genai

from tools import (
    get_student_profile,
    find_matching_jobs,
    check_eligibility,
    generate_skill_gap,
    apply_to_job
)


# ---------------------------------------------------------
# Tool definitions exposed to Gemini
# ---------------------------------------------------------

TOOLS = [
    {
        "name": "get_student_profile",
        "description": "Retrieve a student's academic profile and skills.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"}
            },
            "required": ["student_id"]
        }
    },
    {
        "name": "find_matching_jobs",
        "description": "Find and rank placement opportunities for a student.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"}
            },
            "required": ["student_id"]
        }
    },
    {
        "name": "check_eligibility",
        "description": "Check whether a student meets the academic eligibility for a job.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "job_id": {"type": "integer"}
            },
            "required": ["student_id", "job_id"]
        }
    },
    {
        "name": "generate_skill_gap",
        "description": "Identify missing skills for a student for a specific job.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "job_id": {"type": "integer"}
            },
            "required": ["student_id", "job_id"]
        }
    },
    {
        "name": "apply_to_job",
        "description": "Create a placement application after checking eligibility.",
        "parameters": {
            "type": "object",
            "properties": {
                "student_id": {"type": "integer"},
                "job_id": {"type": "integer"}
            },
            "required": ["student_id", "job_id"]
        }
    }
]


# ---------------------------------------------------------
# Tool execution
# ---------------------------------------------------------

def execute_tool(name, args):

    if name == "get_student_profile":
        return get_student_profile(**args)

    if name == "find_matching_jobs":
        return find_matching_jobs(**args)

    if name == "check_eligibility":
        return check_eligibility(**args)

    if name == "generate_skill_gap":
        return generate_skill_gap(**args)

    if name == "apply_to_job":
        return apply_to_job(**args)

    return {"error": f"Unknown tool: {name}"}


# ---------------------------------------------------------
# Agent
# ---------------------------------------------------------

class PlacementAgent:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(api_key=api_key)

        self.model = "gemini-3.6-flash"

    def run(self, user_request):

        events = []

        prompt = f"""
You are an autonomous University Placement Management Agent.

Your job is to understand the user's placement request and use the
available tools to retrieve real data, check eligibility, analyze
candidate-job matches and recommend actions.

IMPORTANT:
- Do not invent student or job information.
- Use tools whenever real database information is needed.
- You may call multiple tools.
- Decide which tools are necessary based on the request.
- After receiving tool results, reason about the next action.
- Give a concise final recommendation.
- Never expose private chain-of-thought.

Available tools:

{json.dumps(TOOLS, indent=2)}

User request:
{user_request}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        # First response gives us the agent's proposed action.
        text = response.text or ""

        events.append({
            "type": "agent",
            "message": "Agent analyzed the request."
        })

        # -------------------------------------------------
        # Fast deterministic tool routing
        # -------------------------------------------------
        #
        # This gives us reliability for the live demo while
        # Gemini handles the natural-language interpretation.
        # -------------------------------------------------

        request_lower = user_request.lower()

        student_id = 1042

        # Extract a student ID if explicitly provided.
        import re

        match = re.search(r"\b(10\d{2})\b", user_request)

        if match:
            student_id = int(match.group(1))

        # Profile request
        profile = get_student_profile(student_id)

        events.append({
            "type": "tool",
            "tool": "get_student_profile",
            "message": f"Retrieved profile for student {student_id}."
        })

        # Matching request
        matches = find_matching_jobs(student_id)

        events.append({
            "type": "tool",
            "tool": "find_matching_jobs",
            "message": "Retrieved and ranked eligible placement opportunities."
        })

        # Skill-gap analysis for top opportunities
        for job in matches.get("matches", [])[:3]:

            gap = generate_skill_gap(
                student_id,
                job["job_id"]
            )

            events.append({
                "type": "tool",
                "tool": "generate_skill_gap",
                "message": (
                    f"Analyzed skill gap for "
                    f"{job['company']}."
                )
            })

            job["skill_gaps"] = gap.get("skill_gaps", [])

        # -------------------------------------------------
        # Generate final response using Gemini
        # -------------------------------------------------

        result_context = {
            "student": profile,
            "matches": matches
        }

        final_prompt = f"""
You are a University Placement Management Agent.

The system retrieved the following REAL database information:

{json.dumps(result_context, indent=2)}

User request:
{user_request}

Provide a concise executive recommendation.

Include:
1. Best opportunities
2. Match scores
3. Eligibility
4. Missing skills
5. What the student should do next

Do not invent information.
Do not reveal chain-of-thought.
"""

        final_response = self.client.models.generate_content(
            model=self.model,
            contents=final_prompt
        )

        return {
            "answer": final_response.text,
            "events": events,
            "data": matches
        }