import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel, Field
from pypdf import PdfReader


# 1. Environment & Groq


load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("Groq API key is not found")

client = Groq(api_key=my_api_key)

model = "llama-3.3-70b-versatile"



# 2. FastAPI App


app = FastAPI()



# 3. CORS


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 4. Resume Schema


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    skills_used: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = Field(default_factory=list)
    experiences: list[Experience] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)


resume_schema = Resume.model_json_schema()



# 5. Chat Request Schema


class ChatRequest(BaseModel):
    question: str



# 6. PDF → TEXT


def read_pdf(file_path: Path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text = text + page_text + "\n"

    return text



# 7. TEXT → STRUCTURED RESUME


def parse_resume(resume_text: str):

    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning,
not only exact section headings.

For example:

- Experience
- Professional Experience
- Work History
- Employment
- Internships

may all contain relevant experience.

Skills may appear in:

- skills section
- work experience
- internships
- projects

Return ONLY valid JSON matching this schema:

{resume_schema}

Rules:

1. Do not invent information.
2. If a value is unavailable, return null.
3. If a list has no information, return an empty list.
4. Include internships inside experiences.
5. Extract skills mentioned across the entire resume.
"""

    user_prompt = f"""
Parse the following resume:

{resume_text}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_object"
        }
    )

    raw_output = response.choices[0].message.content

    data = json.loads(raw_output)

    resume = Resume(**data)

    return resume


# 8. ASK AI ABOUT CANDIDATE


def ask_candidate(question: str, resume: Resume):

    system_prompt = f"""
You are an AI assistant representing a job candidate.

Here is everything you know about the candidate:

{resume.model_dump_json(indent=2)}

RULES:

1. Answer only using this information.
2. Never hallucinate.
3. If information is unavailable, say:

"I don't have enough information to answer that."

4. Be professional.
5. Answer as if HR is interviewing this candidate.
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content



# 9. HOME API


@app.get("/")
def home():

    return {
        "message": "HireMe is running!"
    }



# 10. CHAT API


@app.post("/chat")
def chat(request: ChatRequest):

    # PDF → TEXT
    resume_path = Path(__file__).resolve().parent / "resume.pdf"

    resume_text = read_pdf(resume_path)

    # TEXT → STRUCTURED RESUME
    resume = parse_resume(resume_text)

    # QUESTION + RESUME → AI ANSWER
    answer = ask_candidate(
        request.question,
        resume
    )

    return {
        "answer": answer
    }