# Personalized Learning Path Generator

**Google AI Agents Capstone Project - Concierge Agents Track**

This is a multi-agent system built with the Google Agent Development Kit (ADK) that acts as an expert curriculum designer. It takes any learning topic and generates a complete, actionable learning plan in minutes.

## 📌 Important Note

**You need a Google AI API key to run this project.** Get one for free at [Google AI Studio](https://makersuite.google.com/app/apikey). Add it to the `.env` file before running.

## The Problem
Learning a new, complex skill (like "Python for Data Analysis" or "Product Management") is overwhelming. A user has to manually sift through hundreds of articles, videos, and courses, and it's difficult to know *what* to learn *in what order*. This research phase can take days and often discourages learners before they even start.

## The Solution
This project provides an AI agent system that automates the entire research and planning process. The user provides a single topic, and the system generates a complete roadmap, including:
1.  A step-by-step list of 5-7 core learning modules.
2.  For each module, 2-3 high-quality, free web resources (articles, docs, videos).
3.  A final "capstone" project idea to help the user apply their new skills.

This turns a vague goal into a structured, daily plan, saving the user hours of work.

## Architecture
The system uses a sequential, multi-agent architecture where a main `main.py` script orchestrates the flow of data (state) between three specialized agents.

```
[User Input] -> [main.py] -> [CurriculumAgent]
[main.py] <- (Module List)

[main.py] -> (Loop) -> [ResourceFinderAgent]
[main.py] <- (Resources)

[main.py] -> [ProjectPlannerAgent]
[main.py] <- (Project Idea)

[main.py] -> (Format & Print Final Plan)
```

- **`CurriculumAgent`**: Takes the user's topic and generates a Python list of 5-7 learning modules.
- **`ResourceFinderAgent`**: Takes a *single* module and uses the **Google Search tool** to find 2-3 relevant resources.
- **`ProjectPlannerAgent`**: Takes the full list of modules and generates a single, relevant project idea.
- **`main.py` (Orchestrator)**: Manages the session and the flow of data between agents. It calls each agent, gets the response, parses it, and passes the necessary data to the next agent in the sequence.

## How to Run

### 1. Set up the environment

Clone the repository and create a virtual environment:

```bash
cd "Capstone Project"
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API credentials

You need a Google AI API key to run this project.

**Option A: Google AI Studio (Recommended for testing)**

1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

3. Edit `.env` and add your API key:

```
GOOGLE_API_KEY=your_actual_api_key_here
```

**Option B: Google Cloud Vertex AI (For production)**

If you have a Google Cloud project, you can use Vertex AI instead:

```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### 4. Run the application

**Option A: Web Interface (Recommended - Streamlit)**

```bash
streamlit run app.py
```

This will open a web interface in your browser where you can:
- Enter any learning topic
- See the generation process in real-time
- View the complete learning plan with modules and resources
- Download your plan as a text file

**Option B: Command Line**

```bash
python main.py
```

You can change the `topic_to_learn` variable inside `main.py` to test different topics.

## Capstone Project Requirements
This project meets the following key requirements:

1.  **Multi-agent system:** It uses three distinct agents (`CurriculumAgent`, `ResourceFinderAgent`, `ProjectPlannerAgent`) that collaborate in a sequence.
2.  **Tools:** The `ResourceFinderAgent` is explicitly given and uses the `Google Search` tool to find real-time, relevant web resources.
3.  **Sessions & State Management:** The `main.py` script acts as the orchestrator, initializing a `Session` and manually managing the state by passing the output from one agent as the input to the next.
4.  **Web Interface:** A Streamlit web interface (`app.py`) provides an easy-to-use UI for generating learning plans.
5.  **Cloud Deployment:** Ready to deploy to Google Cloud Run for the 5 bonus points (see `DEPLOYMENT.md`).

## Deployment

For instructions on deploying this application to Google Cloud Run, see [DEPLOYMENT.md](DEPLOYMENT.md).

The Streamlit interface makes it perfect for cloud deployment - just deploy and share the URL!
