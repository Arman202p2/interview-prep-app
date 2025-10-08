# Interview Prep App

A comprehensive interview and placement preparation platform with AI-powered questions, daily quizzes, and performance analytics.

## Features

- **User Registration & Profile Management**: Custom topic selection and profile customization
- **Daily Quiz System**: Personalized quizzes with timer options and progress tracking
- **AI-Powered Questions**: Scraped questions with AI-generated answers and validation
- **Smart Notifications**: Customizable daily quiz reminders
- **Performance Analytics**: Detailed insights and personalized recommendations
- **Multi-Source Content**: Questions from tcyonline.com, prepinsta.com, indiabix.com, and Reddit

## Architecture

```
Frontend (React/Flutter) ↔ REST API ↔ Backend (FastAPI) ↔ PostgreSQL
                                    ↕
                            AI Services (OpenRouter)
                                    ↕
                            Web Scraping (Firecrawl)
                                    ↕
                            Notifications (Firebase)
```

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React.js / Flutter
- **Database**: PostgreSQL
- **AI**: OpenRouter API
- **Scraping**: Firecrawl
- **Notifications**: Firebase Cloud Messaging
- **Deployment**: Docker + Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/Arman202p2/interview-prep-app.git
cd interview-prep-app
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run with Docker:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
interview-prep-app/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configurations
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utilities
│   ├── package.json
│   └── Dockerfile
├── mobile/                 # Flutter mobile app
├── docker-compose.yml
└── README.md
```

## License

MIT License