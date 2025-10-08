# Deployment Guide

## Quick Start (Development)

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### 1. Clone Repository
```bash
git clone https://github.com/Arman202p2/interview-prep-app.git
cd interview-prep-app
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

## Production Deployment

### Option 1: Docker Compose (Single Server)

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/Arman202p2/interview-prep-app.git
cd interview-prep-app

# Create production environment file
cp .env.example .env.prod

# Edit production environment
nano .env.prod
```

#### 3. Production Environment Variables
```bash
# Database
DATABASE_URL=postgresql://postgres:your_secure_password@db:5432/interview_prep

# Security
JWT_SECRET_KEY=your-super-secure-jwt-key-256-bits-long
DEBUG=False

# External APIs
OPENROUTER_API_KEY=your-openrouter-api-key
FIRECRAWL_API_KEY=your-firecrawl-api-key

# Firebase (for notifications)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-firebase-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-firebase-client-email
FIREBASE_CLIENT_ID=your-firebase-client-id

# CORS (add your domain)
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

#### 4. Production Docker Compose
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: interview_prep
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    networks:
      - app-network

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/interview_prep
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - app-network

  celery:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/interview_prep
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - app-network

  celery-beat:
    build: ./backend
    command: celery -A app.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/interview_prep
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

#### 5. SSL Setup with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 6. Deploy
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Option 2: Kubernetes Deployment

#### 1. Kubernetes Manifests
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: interview-prep

---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: interview-prep
data:
  DATABASE_URL: "postgresql://postgres:password@postgres:5432/interview_prep"
  REDIS_URL: "redis://redis:6379"

---
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: interview-prep
type: Opaque
stringData:
  JWT_SECRET_KEY: "your-jwt-secret-key"
  OPENROUTER_API_KEY: "your-openrouter-key"
  FIRECRAWL_API_KEY: "your-firecrawl-key"

---
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: interview-prep
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: interview_prep
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          value: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: interview-prep
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/interview-prep-backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: interview-prep
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: interview-prep
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: app-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
```

#### 2. Deploy to Kubernetes
```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment
kubectl get pods -n interview-prep
kubectl get services -n interview-prep
kubectl get ingress -n interview-prep

# View logs
kubectl logs -f deployment/backend -n interview-prep
```

### Option 3: Cloud Deployment (AWS)

#### 1. AWS ECS with Fargate
```yaml
# ecs-task-definition.json
{
  "family": "interview-prep",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/interview-prep-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://username:password@rds-endpoint:5432/interview_prep"
        }
      ],
      "secrets": [
        {
          "name": "JWT_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:interview-prep/jwt-secret"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/interview-prep",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 2. Infrastructure as Code (Terraform)
```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "interview-prep-vpc"
  }
}

# RDS Instance
resource "aws_db_instance" "postgres" {
  identifier     = "interview-prep-db"
  engine         = "postgres"
  engine_version = "15.3"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = true
  
  db_name  = "interview_prep"
  username = "postgres"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
  
  tags = {
    Name = "interview-prep-db"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "interview-prep"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "interview-prep-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = aws_subnet.public[*].id
  
  enable_deletion_protection = false
  
  tags = {
    Name = "interview-prep-alb"
  }
}
```

## Monitoring and Logging

### 1. Application Monitoring
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  grafana_data:
  elasticsearch_data:
```

### 2. Health Checks
```python
# backend/app/api/routes/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
import redis
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION
    }

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    checks = {}
    
    # Database check
    try:
        await db.execute("SELECT 1")
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
    
    # Redis check
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    # External APIs check
    try:
        # Check OpenRouter API
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                timeout=5.0
            )
            checks["openrouter"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        checks["openrouter"] = f"unhealthy: {str(e)}"
    
    overall_status = "healthy" if all(
        status == "healthy" for status in checks.values()
    ) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

## Backup and Recovery

### 1. Database Backup
```bash
#!/bin/bash
# backup.sh

# Configuration
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="interview_prep"
DB_USER="postgres"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  --no-password --verbose --format=custom \
  --file="$BACKUP_DIR/interview_prep_$DATE.backup"

# Compress backup
gzip "$BACKUP_DIR/interview_prep_$DATE.backup"

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "interview_prep_*.backup.gz" -mtime +7 -delete

echo "Backup completed: interview_prep_$DATE.backup.gz"
```

### 2. Automated Backup with Cron
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

### 3. Restore Process
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="interview_prep"
DB_USER="postgres"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c $BACKUP_FILE > temp_backup.backup
    BACKUP_FILE="temp_backup.backup"
fi

# Drop existing database
dropdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

# Create new database
createdb -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME

# Restore backup
pg_restore -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME \
  --verbose --clean --no-acl --no-owner $BACKUP_FILE

# Clean up
rm -f temp_backup.backup

echo "Restore completed from: $BACKUP_FILE"
```

## Performance Optimization

### 1. Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_username ON users(username);
CREATE INDEX CONCURRENTLY idx_questions_topic_id ON questions(topic_id);
CREATE INDEX CONCURRENTLY idx_questions_difficulty ON questions(difficulty_level);
CREATE INDEX CONCURRENTLY idx_quiz_attempts_user_id ON quiz_attempts(user_id);
CREATE INDEX CONCURRENTLY idx_quiz_attempts_created ON quiz_attempts(started_at);
CREATE INDEX CONCURRENTLY idx_notifications_user_id ON notifications(user_id, created_at);

-- Partial indexes for active records
CREATE INDEX CONCURRENTLY idx_users_active ON users(id) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_user_topics_active ON user_topics(user_id, topic_id) WHERE is_active = true;
```

### 2. Caching Strategy
```python
# backend/app/services/cache.py
import redis
import json
from typing import Any, Optional
from app.core.config import settings

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
    
    async def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        try:
            self.redis_client.setex(
                key, 
                expire, 
                json.dumps(value, default=str)
            )
        except Exception:
            pass
    
    async def delete(self, key: str):
        try:
            self.redis_client.delete(key)
        except Exception:
            pass
```

## Security Checklist

### Application Security
- [ ] JWT tokens with proper expiration
- [ ] Password hashing with bcrypt
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] HTTPS enforcement
- [ ] Secure headers (HSTS, CSP, etc.)
- [ ] API authentication and authorization

### Infrastructure Security
- [ ] Firewall configuration
- [ ] Database access restrictions
- [ ] SSL/TLS certificates
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Log monitoring
- [ ] Intrusion detection
- [ ] Vulnerability scanning

### Data Protection
- [ ] Data encryption at rest
- [ ] Data encryption in transit
- [ ] Personal data anonymization
- [ ] GDPR compliance
- [ ] Data retention policies
- [ ] Secure data deletion
- [ ] Access logging
- [ ] Data backup verification

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database status
docker-compose exec db pg_isready -U postgres

# View database logs
docker-compose logs db

# Connect to database
docker-compose exec db psql -U postgres -d interview_prep
```

#### 2. Redis Connection Issues
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# View Redis logs
docker-compose logs redis

# Monitor Redis
docker-compose exec redis redis-cli monitor
```

#### 3. Application Errors
```bash
# View application logs
docker-compose logs backend
docker-compose logs frontend

# Check application health
curl http://localhost:8000/health

# Debug mode
docker-compose exec backend python -c "from app.main import app; print(app.debug)"
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats

# Database performance
docker-compose exec db psql -U postgres -d interview_prep -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"

# Redis memory usage
docker-compose exec redis redis-cli info memory
```

### Log Analysis
```bash
# Search for errors in logs
docker-compose logs backend | grep -i error

# Monitor real-time logs
docker-compose logs -f --tail=100

# Export logs for analysis
docker-compose logs backend > backend.log
```

This deployment guide provides comprehensive instructions for deploying the Interview Prep App in various environments, from development to production, with monitoring, backup, and security considerations.