"""Sample job listings, inserted on first start if the jobs table is empty.
Replace or extend these through the Jobs page (or import your Job Hunt data via POST /api/jobs)."""

SEED_JOBS = [
    {"title": "Frontend Developer", "company": "Pixel Labs", "location": "Remote",
     "description": "We need a frontend developer experienced with React, JavaScript, TypeScript, HTML, CSS and Tailwind CSS. You will build responsive interfaces, consume REST APIs, write unit tests with Jest and collaborate using Git and Agile practices."},
    {"title": "Backend Python Developer", "company": "DataForge", "location": "Bangalore, India",
     "description": "Looking for a backend engineer skilled in Python, FastAPI or Django, PostgreSQL, REST API design, Docker and AWS. Experience with CI/CD, Redis, microservices and writing unit tests is a plus."},
    {"title": "Machine Learning Engineer", "company": "NeuralWorks", "location": "Hyderabad, India",
     "description": "Join us to build ML models using Python, PyTorch or TensorFlow, scikit-learn, Pandas and NumPy. You will work on NLP and deep learning problems, deploy models with Docker and Kubernetes, and communicate findings to stakeholders."},
    {"title": "Full Stack Engineer", "company": "LaunchPad", "location": "Remote",
     "description": "Full stack role using React, Node.js, Express, MongoDB, TypeScript and REST API. Deploy on AWS or Vercel, use Git and GitHub Actions for CI/CD, and follow Agile and Scrum practices."},
    {"title": "Data Analyst", "company": "InsightIQ", "location": "Kolkata, India",
     "description": "Analyze business data with SQL, Python, Pandas and Excel. Build dashboards in Tableau or Power BI, perform statistics and data visualization, and present insights with strong communication and problem solving."},
    {"title": "DevOps Engineer", "company": "CloudNest", "location": "Pune, India",
     "description": "Own our infrastructure using AWS, Docker, Kubernetes, Terraform and Linux. Build CI/CD pipelines with Jenkins or GitHub Actions, monitor services, write Bash and Python scripts and improve reliability."},
    {"title": "Software Engineer Intern", "company": "Brightbyte", "location": "Remote",
     "description": "Internship for students with knowledge of data structures, algorithms, Java or Python, Git, SQL and OOP. Willingness to learn, teamwork, and good communication are important."},
    {"title": "Generative AI Developer", "company": "PromptCraft", "location": "Remote",
     "description": "Build LLM applications with Python, FastAPI, LangChain, OpenAI and Hugging Face. Experience with NLP, vector search, REST API, Docker and React for prototypes is preferred."},
]
