# Interview Prep App - Architecture Overview

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Mobile App    │    │   Admin Panel   │
│   (React)       │    │   (Flutter)     │    │   (React)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Load Balancer        │
                    │      (Nginx/Traefik)      │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      API Gateway          │
                    │      (FastAPI)            │
                    └─────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────┴────────┐    ┌─────────┴─────────┐    ┌─────────┴─────────┐
│   Auth Service │    │  Question Service │    │ Analytics Service │
│   (JWT/OAuth)  │    │  (AI + Scraping)  │    │  (Data Analysis)  │
└────────────────┘    └───────────────────┘    └───────────────────┘
        │                       │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Database Layer       │
                    │      (PostgreSQL)         │
                    └─────────────┬─────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────┴────────┐    ┌─────────┴─────────┐    ┌─────────┴─────────┐
│   Redis Cache  │    │  Background Jobs  │    │  File Storage     │
│   (Sessions)   │    │  (Celery/Redis)   │    │  (AWS S3/Local)   │
└────────────────┘    └───────────────────┘    └───────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Task Queue**: Celery with Redis broker
- **Authentication**: JWT with passlib
- **API Documentation**: OpenAPI/Swagger
- **Testing**: pytest, pytest-asyncio

### Frontend
- **Framework**: React 18 with TypeScript
- **UI Library**: Material-UI (MUI) v5
- **State Management**: React Query + Context API
- **Routing**: React Router v6
- **Forms**: React Hook Form
- **Charts**: Recharts
- **Notifications**: React Hot Toast

### Mobile (Optional)
- **Framework**: Flutter 3.x
- **State Management**: Bloc/Provider
- **HTTP Client**: Dio
- **Local Storage**: Hive/SQLite

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **CI/CD**: GitHub Actions

### External Services
- **AI Models**: OpenRouter API (Claude, GPT-4)
- **Web Scraping**: Firecrawl API
- **Push Notifications**: Firebase Cloud Messaging
- **Email**: SendGrid/AWS SES
- **File Storage**: AWS S3/MinIO

## Database Schema

### Core Tables

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    job_role VARCHAR(100),
    experience_level VARCHAR(50),
    target_companies JSONB,
    notification_enabled BOOLEAN DEFAULT TRUE,
    notification_frequency INTEGER DEFAULT 10,
    notification_time VARCHAR(10) DEFAULT '09:00',
    quiz_completion_goal INTEGER DEFAULT 1,
    timer_enabled BOOLEAN DEFAULT TRUE,
    quiz_difficulty VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Topics table
CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    difficulty_level VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- User topics (many-to-many)
CREATE TABLE user_topics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, topic_id)
);

-- Questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    topic_id INTEGER REFERENCES topics(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'mcq',
    difficulty_level VARCHAR(20) DEFAULT 'medium',
    options JSONB,
    correct_answer VARCHAR(500),
    source_url VARCHAR(500),
    source_name VARCHAR(100),
    company_name VARCHAR(100),
    ai_answer TEXT,
    ai_explanation TEXT,
    ai_confidence_score FLOAT,
    tags JSONB,
    estimated_time INTEGER,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_score FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Quiz attempts
CREATE TABLE quiz_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    quiz_type VARCHAR(20) DEFAULT 'daily',
    total_questions INTEGER NOT NULL,
    completed_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_time_taken INTEGER,
    timer_enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'in_progress',
    score_percentage FLOAT,
    topics_covered JSONB,
    difficulty_breakdown JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Quiz questions (individual question attempts)
CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    quiz_attempt_id INTEGER REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(id) ON DELETE CASCADE,
    user_answer VARCHAR(500),
    is_correct BOOLEAN,
    time_taken INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `GET /api/users/stats` - Get user statistics

### Topics
- `GET /api/topics` - Get all topics
- `POST /api/topics` - Create custom topic
- `GET /api/topics/user` - Get user topics
- `POST /api/topics/user` - Add topic to user
- `DELETE /api/topics/user/{topic_id}` - Remove user topic

### Questions
- `GET /api/questions/topic/{topic_id}` - Get questions by topic
- `GET /api/questions/search` - Search questions
- `POST /api/questions/{question_id}/report` - Report question issue

### Quizzes
- `GET /api/quizzes/daily` - Get daily quiz
- `POST /api/quizzes/start` - Start new quiz
- `POST /api/quizzes/{quiz_id}/questions/{question_id}/answer` - Submit answer
- `POST /api/quizzes/{quiz_id}/complete` - Complete quiz
- `GET /api/quizzes/history` - Get quiz history

### Analytics
- `GET /api/analytics/user` - Get user analytics
- `GET /api/analytics/topics` - Get topic performance
- `GET /api/analytics/trends` - Get progress trends
- `GET /api/analytics/recommendations` - Get personalized recommendations

### Notifications
- `GET /api/notifications` - Get user notifications
- `PUT /api/notifications/{id}/read` - Mark notification as read
- `POST /api/notifications/fcm-token` - Register FCM token

## Data Flow

### Question Sourcing Pipeline
1. **Scraping Service** collects questions from multiple sources
2. **AI Service** generates answers and explanations
3. **Validation Service** verifies answer accuracy
4. **Question Service** stores processed questions in database
5. **Indexing Service** creates searchable indexes

### Daily Quiz Generation
1. **Scheduler Service** runs daily at configured time
2. Selects user's active topics based on priority
3. **Question Service** fetches 1 question per topic
4. Creates `DailyQuizSchedule` record
5. **Notification Service** sends quiz reminder

### Quiz Taking Flow
1. User starts quiz via API call
2. **Quiz Service** creates `QuizAttempt` record
3. Questions served one by one with optional timer
4. User answers stored in `QuizQuestion` records
5. Quiz completion triggers analytics update

### Analytics Pipeline
1. **Analytics Service** processes quiz results
2. Calculates performance metrics and trends
3. **Recommendation Engine** generates personalized suggestions
4. Results cached in Redis for fast access

## Security Considerations

### Authentication & Authorization
- JWT tokens with configurable expiration
- Password hashing using bcrypt
- Role-based access control (RBAC)
- API rate limiting

### Data Protection
- Input validation and sanitization
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Content Security Policy)
- HTTPS enforcement

### Privacy
- User data anonymization for analytics
- GDPR compliance features
- Data retention policies
- Secure data deletion

## Scalability Features

### Horizontal Scaling
- Stateless API design
- Database connection pooling
- Redis clustering support
- Load balancer ready

### Performance Optimization
- Database indexing strategy
- Query optimization
- Caching layers (Redis, CDN)
- Async/await patterns

### Monitoring & Observability
- Health check endpoints
- Metrics collection (Prometheus)
- Distributed tracing
- Error tracking (Sentry)

## Deployment Architecture

### Development
```
docker-compose up -d
```

### Production
```
┌─────────────────┐
│   Load Balancer │
│   (Nginx/HAProxy)│
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │  App Tier │
    │ (Multiple │
    │ FastAPI   │
    │ instances)│
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │ Data Tier │
    │(PostgreSQL│
    │  Cluster) │
    └───────────┘
```

### CI/CD Pipeline
1. Code push triggers GitHub Actions
2. Run tests and security scans
3. Build Docker images
4. Deploy to staging environment
5. Run integration tests
6. Deploy to production with blue-green strategy

## Future Enhancements

### Phase 2 Features
- Video explanations for questions
- Peer-to-peer learning features
- Company-specific interview prep tracks
- Mock interview simulator

### Phase 3 Features
- AI-powered interview coach
- Resume analysis and suggestions
- Job matching based on skills
- Collaborative study groups

### Technical Improvements
- GraphQL API option
- Real-time collaboration features
- Advanced analytics with ML
- Multi-language support