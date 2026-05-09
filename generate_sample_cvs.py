"""
Run this once to generate sample PDF CVs for testing the CV Screening Tool.
Usage: python generate_sample_cvs.py
"""
import subprocess, sys

# Auto-install fpdf2 if needed
try:
    from fpdf import FPDF
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fpdf2"])
    from fpdf import FPDF

import os

OUTPUT_DIR = "sample_cvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


CANDIDATES = [
    {
        "filename": "Ali_Hassan_CV.pdf",
        "content": """Ali Hassan
Email: ali.hassan@email.com | Phone: +91-9876543210
LinkedIn: linkedin.com/in/alihassan | Location: Mumbai, India

PROFESSIONAL SUMMARY
Experienced Python developer with 5 years of experience in machine learning, data analysis,
and building scalable web applications. Led cross-functional teams and managed end-to-end
ML pipelines. Passionate about NLP and computer vision.

SKILLS
Programming: Python, SQL, JavaScript, R
Frameworks: TensorFlow, PyTorch, scikit-learn, Flask, Django, FastAPI
Tools: Docker, Kubernetes, Git, AWS, Azure, Jupyter Notebook
Other: Machine Learning, Deep Learning, NLP, Data Analysis, REST APIs

WORK EXPERIENCE
Senior Machine Learning Engineer — TechCorp India (2021–Present)
- Led a team of 5 engineers to build an NLP-based document classification system
- Managed deployment of ML models using Docker and Kubernetes on AWS
- Improved model accuracy by 18% using ensemble techniques
- Worked on large-scale data pipelines processing 10M+ records daily

Data Scientist — DataWorks Pvt Ltd (2019–2021)
- Developed predictive models for customer churn using scikit-learn
- Built data analysis dashboards using Python and Tableau
- Collaborated with business teams to translate requirements into ML solutions

EDUCATION
Master of Science in Computer Science — IIT Bombay (2019)
Bachelor of Engineering in IT — University of Mumbai (2017)

CERTIFICATIONS
- AWS Certified Machine Learning Specialty
- Google Professional Data Engineer
- Deep Learning Specialization — Coursera (Andrew Ng)
""",
    },
    {
        "filename": "Priya_Sharma_CV.pdf",
        "content": """Priya Sharma
Email: priya.sharma@email.com | Phone: +91-9123456789
Location: Bangalore, India

PROFESSIONAL SUMMARY
Data analyst with 3 years of experience in SQL, Python, and business intelligence tools.
Strong background in statistical analysis, data visualisation, and reporting.
Holds a bachelor's degree in statistics from Delhi University.

SKILLS
Languages: Python, SQL, R
Tools: Power BI, Tableau, Excel, Google Analytics
Libraries: pandas, NumPy, matplotlib, seaborn
Databases: MySQL, PostgreSQL

WORK EXPERIENCE
Data Analyst — Analytics Hub (2022–Present)
- Analysed sales data and produced weekly reports for senior management
- Built interactive Power BI dashboards tracking KPIs for 3 business units
- Wrote complex SQL queries to extract and clean datasets from PostgreSQL
- Worked closely with the marketing team to measure campaign performance

Junior Analyst — FinMetrics (2021–2022)
- Assisted in data cleaning and preparation for financial models
- Maintained Excel-based reporting templates used across departments

EDUCATION
Bachelor of Science in Statistics — Delhi University (2021)

CERTIFICATIONS
- Microsoft Power BI Data Analyst Associate
- Google Data Analytics Certificate
""",
    },
    {
        "filename": "Rohan_Verma_CV.pdf",
        "content": """Rohan Verma
Email: rohan.verma@gmail.com | Phone: +91-9988776655
Location: Hyderabad, India

SUMMARY
Fresh graduate with strong academic background in computer science.
Completed internship involving basic Python scripting and database management.
Eager to learn machine learning and data science.

SKILLS
Languages: Python (basic), Java, C++
Tools: MySQL, Git, MS Office
Concepts: Object-Oriented Programming, Data Structures, Algorithms

INTERNSHIP
Software Intern — Infosys (Summer 2023)
- Wrote Python scripts to automate report generation
- Worked with MySQL databases to run queries and extract data
- Attended agile standups and contributed to sprint planning

PROJECTS
Student Grade Predictor (Academic Project)
- Built a basic linear regression model using Python and scikit-learn
- Dataset: 500 student records from Kaggle

Inventory Management System
- Developed a Java application with MySQL backend for a local shop

EDUCATION
Bachelor of Engineering in Computer Science — JNTU Hyderabad (2023)

EXTRA-CURRICULAR
- Member of college coding club
- Participated in HackIndia 2022 hackathon
""",
    },
    {
        "filename": "Sara_Khan_CV.pdf",
        "content": """Sara Khan
Email: sara.khan@email.com | Phone: +91-9871234560
Location: Pune, India

PROFESSIONAL SUMMARY
Machine learning engineer with 4 years of hands-on experience developing and deploying
NLP models, recommendation systems, and computer vision applications. Strong Python skills.
Led projects from research to production. MSc in Data Science from University of Pune.

TECHNICAL SKILLS
ML / AI: Transformers, BERT, GPT, LLMs, CNNs, RNNs, Reinforcement Learning
Python Libraries: scikit-learn, TensorFlow, Keras, PyTorch, NLTK, spaCy, Hugging Face
MLOps: MLflow, DVC, Docker, Kubernetes, CI/CD pipelines
Cloud: AWS SageMaker, Google Cloud AI Platform
Databases: MongoDB, Redis, PostgreSQL

WORK EXPERIENCE
Machine Learning Engineer — AIVentures (2020–Present)
- Designed and deployed a BERT-based sentiment analysis system handling 1M+ reviews/day
- Built a product recommendation engine increasing conversion rate by 22%
- Managed end-to-end ML lifecycle using MLflow and DVC
- Led team of 3 junior engineers on NLP projects
- Worked with stakeholders to define model requirements and KPIs

ML Research Intern — CDAC Pune (2020)
- Researched transformer architectures for text summarisation
- Published one internal technical report on few-shot learning

EDUCATION
Master of Science in Data Science — University of Pune (2020)
Bachelor of Engineering in Computer Engineering — Savitribai Phule Pune University (2018)

CERTIFICATIONS
- TensorFlow Developer Certificate — Google
- AWS Certified Machine Learning Specialty
- Natural Language Processing Specialization — Coursera
""",
    },
    {
        "filename": "James_Okafor_CV.pdf",
        "content": """James Okafor
Email: james.okafor@email.com | Phone: +234-8012345678
Location: Lagos, Nigeria (Open to remote)

PROFILE
Backend developer with 6 years of experience building REST APIs and microservices
using Python, Node.js, and Go. Experience managing cloud infrastructure on AWS.
Strong understanding of software architecture, CI/CD, and DevOps practices.

TECHNICAL SKILLS
Languages: Python, JavaScript (Node.js), Go, Bash
Frameworks: FastAPI, Flask, Express.js
DevOps: Docker, Kubernetes, Terraform, GitHub Actions, Jenkins
Cloud: AWS (EC2, S3, Lambda, RDS), GCP
Databases: PostgreSQL, MongoDB, Redis
Other: REST API design, GraphQL, Microservices, gRPC

EXPERIENCE
Senior Backend Engineer — FinTech Solutions (2020–Present)
- Architected and led development of a payment processing microservices platform
- Managed AWS infrastructure using Terraform, reducing cloud costs by 30%
- Implemented CI/CD pipelines using GitHub Actions and Jenkins
- Worked with product teams to define API contracts and data models
- Mentored 2 junior engineers

Backend Developer — WebSoft Ltd (2018–2020)
- Built REST APIs using Flask and FastAPI for e-commerce platforms
- Integrated third-party payment gateways (Stripe, PayStack)
- Optimised PostgreSQL queries reducing page load time by 40%

EDUCATION
Bachelor of Science in Computer Science — University of Lagos (2018)

CERTIFICATIONS
- AWS Solutions Architect Associate
- Docker Certified Associate
""",
    },
]


def sanitize(text: str) -> str:
    """Remove non-latin1 characters that Helvetica cannot render."""
    return text.encode("latin-1", errors="ignore").decode("latin-1")


def create_pdf(filename: str, text: str):
    from fpdf.enums import XPos, YPos

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=10)
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    first_line = True
    for line in text.strip().split("\n"):
        stripped = sanitize(line.strip())
        if not stripped:
            pdf.ln(3)
            continue

        is_section = (
            line == line.lstrip()
            and stripped.isupper()
            and len(stripped) > 3
            and not first_line
        )

        if first_line:
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(page_width, 8, stripped, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", size=10)
            first_line = False
        elif is_section:
            pdf.set_font("Helvetica", "B", 11)
            pdf.ln(2)
            pdf.cell(page_width, 6, stripped, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(page_width, 5, stripped)

    path = os.path.join(OUTPUT_DIR, filename)
    pdf.output(path)
    print(f"  Created: {path}")


if __name__ == "__main__":
    print(f"Generating {len(CANDIDATES)} sample CVs in '{OUTPUT_DIR}/'...")
    for c in CANDIDATES:
        create_pdf(c["filename"], c["content"])
    print(f"\nDone! Upload the PDFs from the '{OUTPUT_DIR}/' folder into the app.")
    print("\nSample Job Description to test with:")
    print("-" * 60)
    print("""We are looking for a Machine Learning Engineer with 3+ years of experience.
The ideal candidate should have strong Python skills and hands-on experience with
scikit-learn, TensorFlow or PyTorch. Experience with NLP, deep learning, and
deploying ML models using Docker and Kubernetes is required.
The candidate must have a bachelor or master degree in Computer Science, Data Science,
or a related field. Experience managing teams and working in agile environments is a plus.
Familiarity with AWS or GCP cloud platforms and MLflow for experiment tracking is preferred.
Strong communication skills and the ability to work with cross-functional teams is essential.""")
    print("-" * 60)
