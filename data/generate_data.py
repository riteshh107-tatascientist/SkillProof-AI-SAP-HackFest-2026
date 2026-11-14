"""Generates the SYNTHETIC sample datasets used by SkillProof AI. Run: python data/generate_data.py"""
import math, random
from pathlib import Path
import numpy as np, pandas as pd
random.seed(2026); np.random.seed(2026)
D = Path(__file__).parent
SKILLS = """Python;Programming;py|python3;Pandas|NumPy|Scikit-learn
Java;Programming;core java;OOP|SQL
JavaScript;Programming;js|es6|ecmascript;React|Node.js|TypeScript
TypeScript;Programming;;JavaScript|React
C++;Programming;cpp;Data Structures|Algorithms
C#;Programming;csharp;Unity|OOP
SQL;Databases;mysql|t-sql|structured query language;PostgreSQL|SQLite|Data Analysis
SQLite;Databases;;SQL
PostgreSQL;Databases;postgres;SQL
MongoDB;Databases;mongo|nosql;Node.js
Pandas;Data & ML;;Python|NumPy|Data Analysis
NumPy;Data & ML;;Python|Pandas
Scikit-learn;Data & ML;sklearn|scikit learn;Machine Learning|Python
Machine Learning;Data & ML;ml|predictive modelling|predictive modeling;Scikit-learn|Statistics|Deep Learning
Deep Learning;Data & ML;neural networks|cnn|lstm;TensorFlow|PyTorch|Machine Learning
TensorFlow;Data & ML;keras;Deep Learning
PyTorch;Data & ML;torch;Deep Learning
NLP;Data & ML;natural language processing|text mining;Machine Learning|Generative AI
Computer Vision;Data & ML;opencv|mediapipe|image processing;Deep Learning
Data Analysis;Data & ML;data analytics|eda|exploratory data analysis;Pandas|Statistics|Data Visualization
Data Visualization;Data & ML;plotly|matplotlib|seaborn|power bi|tableau|dashboards;Data Analysis
Statistics;Data & ML;statistical analysis|hypothesis testing;Data Analysis|R
R;Data & ML;r programming|rstudio;Statistics
Generative AI;Data & ML;genai|llm|llms|large language models|prompt engineering|gemini api|openai api;NLP
Data Engineering;Data & ML;etl|data pipelines|data pipeline|airflow|apache spark;SQL|Python
Streamlit;Web & Cloud;;Python|Data Visualization
Flask;Web & Cloud;;Python|REST API
FastAPI;Web & Cloud;;Python|REST API
Django;Web & Cloud;;Python|REST API
REST API;Web & Cloud;restful|api development|apis|rest apis;Flask|Node.js
React;Web & Cloud;reactjs|react.js;JavaScript|HTML/CSS
Next.js;Web & Cloud;nextjs;React
Node.js;Web & Cloud;nodejs|express.js;JavaScript|REST API
HTML/CSS;Web & Cloud;html|css|html5|css3|tailwind|tailwind css;JavaScript
Cloud Computing;Web & Cloud;aws|azure|gcp|vercel|supabase;Docker
Docker;Tools & DevOps;containers|containerization;Cloud Computing|Linux
Git;Tools & DevOps;github|version control|gitlab;CI/CD
CI/CD;Tools & DevOps;github actions|jenkins|continuous integration;Git|Docker
Linux;Tools & DevOps;ubuntu|bash|shell scripting;Docker
Testing;Tools & DevOps;pytest|unit testing|unittest|test automation|selenium;Python
Data Structures;Computer Science;dsa|data structures and algorithms;Algorithms
Algorithms;Computer Science;competitive programming;Data Structures
OOP;Computer Science;object oriented programming|object-oriented programming;Java|C++
Computer Networks;Computer Science;networking|tcp/ip;Cloud Computing|Cybersecurity
SAP;Enterprise;sap erp|s/4hana|sap btp|sap abap|abap|successfactors|sap fiori;ERP|SQL
ERP;Enterprise;enterprise resource planning|erp systems;SAP|Business Analysis
Business Analysis;Enterprise;requirements gathering|business analyst|stakeholder analysis;Excel|ERP
Excel;Enterprise;ms excel|advanced excel|excel formulas|spreadsheets|vlookup|pivot tables;Data Analysis
Project Management;Enterprise;agile|scrum|jira|kanban;Communication|Leadership
Unity;Game Development;unity3d|unity 3d;C#|Game Design
Game Design;Game Development;gameplay design|game development;Unity
UI/UX Design;Design;ui design|ux design|figma|wireframing|user research;HTML/CSS
Communication;Soft Skills;public speaking|presentation skills|written communication|presentations;Teamwork
Teamwork;Soft Skills;collaboration|team player|team collaboration;Communication
Leadership;Soft Skills;team lead|led a team|mentoring|mentored;Teamwork|Project Management
Problem Solving;Soft Skills;analytical thinking|critical thinking|troubleshooting;Algorithms
Adaptability;Soft Skills;quick learner|learning agility|self-learner|fast learner;Problem Solving
Cybersecurity;Security;infosec|network security|ethical hacking|owasp|penetration testing;Computer Networks|Linux"""
JOBS = """1;Data Analyst;Analytics;Turn business data into insights and dashboards using SQL, Excel and visualisation tools.;SQL|Data Analysis|Data Visualization|Excel|Statistics;Python|Pandas|Communication
2;Machine Learning Engineer;AI & Data;Build, evaluate and deploy machine-learning models for production use.;Python|Machine Learning|Scikit-learn|Pandas|Statistics|Git;Deep Learning|Docker|NLP|Testing
3;Python Developer;Engineering;Develop and maintain backend services and automation in Python.;Python|REST API|SQL|Git|Testing|OOP;Flask|FastAPI|Docker|CI/CD
4;Full-Stack Developer;Engineering;Build responsive web applications across frontend and backend.;JavaScript|React|Node.js|HTML/CSS|REST API|Git|SQL;TypeScript|Next.js|MongoDB|Docker
5;SAP Business Analyst;Enterprise Solutions;Translate business processes into SAP-enabled solutions together with stakeholders.;SAP|ERP|Business Analysis|Excel|Communication|SQL;Project Management|Data Analysis|Problem Solving
6;Cloud & DevOps Engineer;Platform;Automate delivery pipelines and run reliable cloud infrastructure.;Cloud Computing|Docker|Linux|Git|CI/CD;Python|Computer Networks|Cybersecurity|Testing
7;Data Engineer;AI & Data;Design reliable data pipelines and warehouses for analytics teams.;Python|SQL|Data Engineering|Cloud Computing|Git;PostgreSQL|Docker|Linux|Testing
8;Generative AI Engineer;AI & Data;Build LLM-powered applications with evaluation and safety controls.;Python|Generative AI|NLP|REST API|Git;Streamlit|FastAPI|Docker|Machine Learning|Testing
9;QA Automation Engineer;Quality;Design automated tests that protect product quality.;Testing|Python|Git|CI/CD|Problem Solving;Java|REST API|Linux|Communication
10;UI/UX Designer;Design;Craft usable, accessible interfaces backed by user research.;UI/UX Design|HTML/CSS|Communication|Problem Solving;JavaScript|Teamwork|Adaptability
11;Game Developer;Interactive;Build performant gameplay systems for mobile games.;Unity|C#|Game Design|OOP|Algorithms;Git|Problem Solving|Teamwork
12;Cybersecurity Analyst;Security;Monitor, assess and reduce security risk across systems.;Cybersecurity|Computer Networks|Linux|Problem Solving;Python|Cloud Computing|Communication"""
RES = """Python;Python Official Tutorial;python.org;Docs;10;Yes;https://docs.python.org/3/tutorial/
Pandas;10 Minutes to pandas;pandas.pydata.org;Docs;3;Yes;https://pandas.pydata.org/docs/user_guide/10min.html
NumPy;NumPy Absolute Beginners;numpy.org;Docs;3;Yes;https://numpy.org/doc/stable/user/absolute_beginners.html
SQL;SQLBolt Interactive Lessons;sqlbolt.com;Interactive;6;Yes;https://sqlbolt.com/
PostgreSQL;PostgreSQL Tutorial;postgresql.org;Docs;6;Yes;https://www.postgresql.org/docs/current/tutorial.html
Machine Learning;Kaggle Learn: Intro to ML;kaggle.com;Course;4;Yes;https://www.kaggle.com/learn/intro-to-machine-learning
Scikit-learn;scikit-learn User Guide;scikit-learn.org;Docs;8;Yes;https://scikit-learn.org/stable/user_guide.html
Deep Learning;Kaggle Learn: Intro to Deep Learning;kaggle.com;Course;4;Yes;https://www.kaggle.com/learn/intro-to-deep-learning
TensorFlow;TensorFlow Tutorials;tensorflow.org;Docs;8;Yes;https://www.tensorflow.org/tutorials
PyTorch;PyTorch Tutorials;pytorch.org;Docs;8;Yes;https://pytorch.org/tutorials/
NLP;Hugging Face LLM/NLP Course;huggingface.co;Course;10;Yes;https://huggingface.co/learn
Generative AI;Google Cloud Skills Boost: Generative AI;cloudskillsboost.google;Course;6;Mixed;https://www.cloudskillsboost.google/
Data Analysis;Kaggle Learn: Data Cleaning;kaggle.com;Course;4;Yes;https://www.kaggle.com/learn/data-cleaning
Data Visualization;Plotly Python Documentation;plotly.com;Docs;4;Yes;https://plotly.com/python/
Statistics;Khan Academy Statistics and Probability;khanacademy.org;Course;12;Yes;https://www.khanacademy.org/math/statistics-probability
R;R for Data Science (2e);r4ds.hadley.nz;Book;12;Yes;https://r4ds.hadley.nz/
Streamlit;Streamlit Documentation;docs.streamlit.io;Docs;3;Yes;https://docs.streamlit.io/
FastAPI;FastAPI Tutorial;fastapi.tiangolo.com;Docs;4;Yes;https://fastapi.tiangolo.com/tutorial/
Flask;Flask Quickstart;flask.palletsprojects.com;Docs;3;Yes;https://flask.palletsprojects.com/
React;Learn React;react.dev;Docs;8;Yes;https://react.dev/learn
Next.js;Learn Next.js;nextjs.org;Course;6;Yes;https://nextjs.org/learn
Node.js;Learn Node.js;nodejs.org;Docs;5;Yes;https://nodejs.org/en/learn
JavaScript;MDN JavaScript Guide;developer.mozilla.org;Docs;10;Yes;https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide
HTML/CSS;MDN Learn Web Development;developer.mozilla.org;Docs;10;Yes;https://developer.mozilla.org/en-US/docs/Learn
Docker;Docker Get Started;docs.docker.com;Docs;3;Yes;https://docs.docker.com/get-started/
Git;Pro Git Book;git-scm.com;Book;6;Yes;https://git-scm.com/book
Linux;Linux Journey;linuxjourney.com;Interactive;8;Yes;https://linuxjourney.com/
Testing;pytest Getting Started;docs.pytest.org;Docs;2;Yes;https://docs.pytest.org/en/stable/getting-started.html
Data Structures;CS50x Introduction to CS;cs50.harvard.edu;Course;20;Yes;https://cs50.harvard.edu/x/
Algorithms;Practice problems on LeetCode;leetcode.com;Practice;15;Mixed;https://leetcode.com/
SAP;SAP Learning (official);learning.sap.com;Course;10;Mixed;https://learning.sap.com/
Unity;Unity Learn;learn.unity.com;Course;12;Yes;https://learn.unity.com/
UI/UX Design;Figma Learn Design;figma.com;Course;5;Yes;https://www.figma.com/resources/learn-design/
Cybersecurity;OWASP Top Ten;owasp.org;Docs;3;Yes;https://owasp.org/www-project-top-ten/
Computer Vision;OpenCV Tutorials;docs.opencv.org;Docs;6;Yes;https://docs.opencv.org/4.x/d9/df8/tutorial_root.html
MongoDB;MongoDB University;learn.mongodb.com;Course;6;Yes;https://learn.mongodb.com/
Communication;Practice: record a 3-minute walkthrough of your best project and ask a peer for feedback;self-practice;Practice;2;Yes;"""
def main():
    rows = [l.split(";") for l in SKILLS.splitlines()]
    sk = pd.DataFrame(rows, columns=["skill", "category", "synonyms", "related"]); sk.to_csv(D / "skills.csv", index=False)
    jb = pd.DataFrame([l.split(";") for l in JOBS.splitlines()], columns=["job_id", "title", "department", "description", "required_skills", "preferred_skills"]); jb.to_csv(D / "jobs.csv", index=False)
    pd.DataFrame([l.split(";") for l in RES.splitlines()], columns=["skill", "title", "provider", "type", "hours", "free", "url"]).to_csv(D / "learning_resources.csv", index=False)
    syn = {r[0]: [x for x in r[2].split("|") if x] for r in rows}
    names = [r[0] for r in rows]
    first = "Aarav Diya Kabir Meera Rohan Sneha Vihaan Ananya Ishaan Tara Arjun Nisha Dev Pooja Yash Riya Karan Isha Neel Kavya".split()
    last = "Verma Patel Nair Gupta Rao Mishra Joshi Khan Iyer Das Menon Bose".split()
    pairs = random.sample([(a, b) for a in first for b in last], 40)
    edus = ["B.Tech CSE", "B.Tech CSE (Data Science)", "B.Tech IT", "BCA", "MCA", "B.Sc Computer Science", "B.Tech ECE"]
    verbs = ["Built", "Developed", "Implemented", "Designed", "Automated", "Deployed"]
    kinds = ["dashboard", "web application", "analysis pipeline", "prototype", "internal tool", "mobile feature"]
    cands = []
    for i, (fn, ln) in enumerate(pairs, 1):
        job = jb.iloc[(i - 1) % len(jb)]
        req, pref = job.required_skills.split("|"), job.preferred_skills.split("|")
        true = {s for s in req if random.random() < 0.75} | {s for s in pref if random.random() < 0.3} | set(random.sample(names, random.randint(1, 3)))
        true = sorted(true)
        def term(s):
            opts = syn[s]
            if s in ("R", "Excel"): return random.choice(opts)
            return random.choice(opts) if opts and random.random() < 0.35 else s
        listed = [s for s in true if random.random() < 0.5]; proj = [s for s in true if s not in listed]
        lines = ["SUMMARY", f"{random.choice(edus)} student with hands-on project work.", "SKILLS", ", ".join(term(s) for s in listed) or "Self-taught learner", "PROJECTS"]
        for j in range(0, len(proj), 2):
            ch = proj[j:j + 2]
            lines.append(f"{random.choice(verbs)} a {random.choice(kinds)} using " + " and ".join(term(s) for s in ch) + f", improving turnaround by {random.randint(10, 60)}%.")
        if random.random() < 0.35:
            d = random.choice([n for n in names if n not in true]); lines.append(f"Currently curious about {d} and planning to explore it.")
        cands.append(dict(candidate_id=f"SYN-{i:03d}", name=f"{fn} {ln}", headline=f"Aspiring {job.title}", education=random.choice(edus), target_job_id=job.job_id, true_skills="|".join(true), resume_text="\n".join(lines)))
    pd.DataFrame(cands).to_csv(D / "candidates.csv", index=False)
    n = 600; out = []
    for i in range(n):
        tier = random.choices(["Tier-1", "Tier-2", "Tier-3"], [.25, .40, .35])[0]; reg = random.choices(["Metro", "Tier-2 city", "Rural"], [.45, .35, .20])[0]
        score = float(np.clip(np.random.normal(62, 14), 0, 100))
        logit = 0.06 * (score - 62) + {"Tier-1": 1.1, "Tier-2": 0.1, "Tier-3": -0.9}[tier] + {"Metro": .2, "Tier-2 city": 0, "Rural": -.5}[reg] - 0.9
        out.append(dict(applicant_id=f"A{i+1:04d}", gender=random.choices(["Female", "Male", "Non-binary"], [.44, .54, .02])[0], age_group=random.choices(["21-24", "25-29", "30+"], [.5, .35, .15])[0], region=reg, institution_tier=tier, skill_score=round(score, 1),
                        legacy_screen_shortlisted=int(random.random() < 1 / (1 + math.exp(-logit))), skills_screen_shortlisted=int(score >= 70)))
    pd.DataFrame(out).to_csv(D / "fairness_demo.csv", index=False)
if __name__ == "__main__": main()
