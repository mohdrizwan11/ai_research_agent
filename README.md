# AI Research Agent 🔍

Autonomous multi-agent research report generator using Groq LLM.

This repository features a complete full-stack application safely partitioned into `frontend/` and `backend/` directories, making it easy to deploy on modern cloud platforms. The backend uses Python and FastAPI to orchestrate multiple AI agents. The frontend is built with React and Vite, featuring a minimalistic, Claude-inspired design to easily submit prompts and read generated markdown reports.

## Features

- **Multi-Agent Pipeline**: Specialized agents handle distinct steps (Search -> Extract -> Summarize -> Report).
- **FastAPI Backend**: Exposes endpoints for executing research and viewing cache.
- **Modern React UI**: Claude-inspired minimalistic design, dark/light mode, and smooth interactions.
- **Local Caching**: Stores generated reports in `data/cache` for lightning-fast subsequent retrievals.
- **Free Open Sources**: Leverages Wikipedia, arXiv, and DuckDuckGo for data gathering.

## Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Groq API Key**: Get one for free at [console.groq.com](https://console.groq.com/).

## Local Development Quick Start

### 1. Setup the Backend (FastAPI)

```bash
# Enter the backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Copy the example env file and add your key
cp .env.example .env
# Edit .env and set GROQ_API_KEY=your_key_here

# Run the FastAPI server
uvicorn src.api.main:app --reload
# The API will be available at http://localhost:8000
```

### 2. Setup the Frontend (React + Vite)

```bash
# Open a new terminal and navigate to the frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the frontend development server
npm run dev
# The UI will be available at http://localhost:5173
```

## Deployment Guide 🚀

The project is structured to easily deploy the backend to **Render** and the frontend to **Vercel** or **Netlify**.

### Deploying the Backend (Render)

We have included a `render.yaml` Blueprint to make deploying the backend a 1-click process.

1. Push your repository to GitHub.
2. Sign up / Log in to [Render](https://render.com/).
3. Click **New** -> **Blueprint**.
4. Connect your GitHub repository. Render will automatically detect the `render.yaml` file.
5. In the Render Dashboard for your new Web Service, go to **Environment** and add your `GROQ_API_KEY`.
6. Your backend will deploy and give you a public URL (e.g., `https://ai-research-backend.onrender.com`).

### Deploying the Frontend (Vercel)

1. Sign up / Log in to [Vercel](https://vercel.com/).
2. Click **Add New** -> **Project**.
3. Import your GitHub repository.
4. **Important**: In the configuration settings, set the **Framework Preset** to `Vite` and the **Root Directory** to `frontend`.
5. *Wait! Before deploying*, you need to point your frontend to your new Render backend URL instead of `localhost`. You can either:
   - Update `frontend/src/App.jsx` to fetch from your Render URL.
   - Or, better yet, use an Environment Variable for the API URL in Vercel.
6. Click **Deploy**.

## Project Structure

```
ai_research_agent/
├── backend/
│   ├── config/          # YAML config files
│   ├── data/cache/      # Auto-created runtime cache
│   ├── prompts/         # Prompt templates for agents
│   ├── scripts/         # CLI runner tools
│   ├── src/             # Core Python logic (API, Agents, Memory)
│   ├── render.yaml      # Render deployment configuration
│   ├── .env.example     # Environment variable template
│   └── requirements.txt # Python dependencies
├── frontend/            # React + Vite web application
│   ├── src/             # UI components and styles
│   └── package.json
├── .gitignore           # Source control ignore rules
└── README.md            # You are here
```

## Free Sources Used

| Source     | Data                        | API Key? |
|------------|-----------------------------|----------|
| Wikipedia  | General summaries           | No       |
| arXiv      | Academic paper abstracts    | No       |
| DuckDuckGo | Web search snippets         | No       |
| Groq       | LLM (llama-3.3-70b-versatile)| Yes (free)|
