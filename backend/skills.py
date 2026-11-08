"""Skill dictionary: canonical name -> list of aliases (matched case-insensitively)."""
import re

SKILLS = {
    # Languages
    "Python": [], "Java": [], "JavaScript": ["js", "ecmascript", "es6"], "TypeScript": ["ts"],
    "C++": ["cpp"], "C#": ["csharp"], "Go": ["golang"], "Rust": [], "Ruby": [], "PHP": [],
    "Kotlin": [], "Swift": [], "Scala": [], "SQL": [], "Bash": ["shell scripting"],
    "R programming": [], "MATLAB": [], "HTML": ["html5"], "CSS": ["css3"],
    # Frontend
    "React": ["react.js", "reactjs"], "Next.js": ["nextjs"], "Vue": ["vue.js", "vuejs"],
    "Angular": ["angularjs"], "Redux": [], "Tailwind CSS": ["tailwind"], "Bootstrap": [],
    "Sass": ["scss"], "Webpack": [], "Vite": [], "jQuery": [],
    # Backend
    "Node.js": ["nodejs", "node"], "Express": ["express.js", "expressjs"], "FastAPI": [],
    "Django": [], "Flask": [], "Spring Boot": ["spring"], "ASP.NET": [".net", "dotnet"],
    "REST API": ["rest", "restful", "rest apis", "restful apis"], "GraphQL": [],
    "gRPC": [], "Microservices": ["microservice"], "WebSockets": ["websocket"],
    # Data / ML
    "Machine Learning": ["ml"], "Deep Learning": [], "NLP": ["natural language processing"],
    "Computer Vision": [], "TensorFlow": [], "PyTorch": [], "Keras": [],
    "scikit-learn": ["sklearn", "scikit learn"], "Pandas": [], "NumPy": [],
    "Data Analysis": ["data analytics"], "Data Visualization": ["data viz"],
    "Tableau": [], "Power BI": ["powerbi"], "Excel": [], "Statistics": ["statistical analysis"],
    "LLM": ["llms", "large language models"], "OpenAI": [], "LangChain": [],
    "Hugging Face": ["huggingface"], "Spark": ["pyspark", "apache spark"],
    "Hadoop": [], "Airflow": [], "ETL": [], "Data Engineering": [],
    # Databases
    "PostgreSQL": ["postgres"], "MySQL": [], "SQLite": [], "MongoDB": ["mongo"],
    "Redis": [], "Elasticsearch": [], "Firebase": [], "DynamoDB": [], "Cassandra": [],
    "NoSQL": [], "SQLAlchemy": [], "Prisma": [],
    # Cloud / DevOps
    "AWS": ["amazon web services"], "Azure": [], "GCP": ["google cloud"],
    "Docker": [], "Kubernetes": ["k8s"], "Terraform": [], "Jenkins": [],
    "CI/CD": ["cicd", "continuous integration", "continuous deployment"],
    "GitHub Actions": [], "Linux": [], "Nginx": [], "Vercel": [], "Heroku": [],
    "Git": [], "GitHub": [], "GitLab": [],
    # Practices / misc
    "Agile": [], "Scrum": [], "Jira": [], "Unit Testing": ["unit tests", "pytest", "jest"],
    "Test Automation": ["selenium", "cypress"], "System Design": [],
    "Data Structures": [], "Algorithms": [], "OOP": ["object oriented", "object-oriented"],
    "Design Patterns": [], "Cybersecurity": ["information security"], "OAuth": [], "JWT": [],
    "Figma": [], "UI/UX": ["ux design", "ui design"], "Responsive Design": [],
    "Accessibility": ["wcag"], "SEO": [], "Android": [], "iOS": [], "React Native": [],
    "Flutter": [], "Blockchain": [], "Solidity": [],
    # Soft skills
    "Communication": [], "Leadership": [], "Teamwork": ["collaboration", "team player"],
    "Problem Solving": ["problem-solving"], "Project Management": [],
    "Time Management": [], "Critical Thinking": [], "Mentoring": [],
}

_BOUNDARY_L = r"(?<![A-Za-z0-9+#])"
_BOUNDARY_R = r"(?![A-Za-z0-9+#])"


def _build_patterns():
    patterns = {}
    for canonical, aliases in SKILLS.items():
        names = {canonical.lower(), *[a.lower() for a in aliases]}
        # "R programming" should match "R programming" only; "Go" only via golang
        if canonical == "Go":
            names = {"golang"}
        alt = "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True))
        patterns[canonical] = re.compile(_BOUNDARY_L + "(?:" + alt + ")" + _BOUNDARY_R, re.IGNORECASE)
    return patterns


PATTERNS = _build_patterns()
