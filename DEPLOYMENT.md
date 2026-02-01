# Deployment Quick Reference

## 🚀 Fresh Deployment Checklist

Use this checklist when deploying to a new environment:

### Step 1: Prerequisites
- [ ] Docker installed (version 20.10+)
- [ ] Docker Compose installed (version 2.0+)
- [ ] Git installed
- [ ] Domain name configured (for production)
- [ ] SSL certificates ready (for production)

### Step 2: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd neighborhood-library-platform

# Create environment file
cp .env.example .env

# Edit configuration
nano .env
```

### Step 3: Update .env File

**Required Changes:**
```bash
# Security (CRITICAL!)
DEBUG=False
SECRET_KEY=<generate-new-key>
DJANGO_SUPERUSER_PASSWORD=<strong-password>

# Database (CHANGE DEFAULTS!)
DB_PASSWORD=<strong-password>

# Networking
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,localhost
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1
```

### Step 4: Deploy

**Development:**
```bash
docker-compose up -d
```

**Production (with Nginx):**
```bash
docker-compose --profile production up -d
```

### Step 5: Initialize Database

```bash
# Migrations are automatic, but verify:
docker-compose exec api python manage.py migrate

# Create superuser (if not auto-created)
docker-compose exec api python manage.py createsuperuser

# Optional: Load sample data
docker-compose exec api python manage.py loaddata sample_data.json
```

### Step 6: Verify Deployment

```bash
# Check all services are healthy
docker-compose ps

# Test API
curl http://localhost:8000/api/health/

# Test frontend
curl http://localhost:3000/

# View logs
docker-compose logs -f
```

## 🔒 Production Security Hardening

### 1. SSL/TLS Configuration

Update `nginx.conf` for HTTPS:

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # ... rest of config
}
```

### 2. Firewall Rules

```bash
# Allow only necessary ports
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 3. Database Security

```bash
# Change postgres port or disable external access
POSTGRES_PORT=  # Leave empty to disable external port

# Use strong password
DB_PASSWORD=$(openssl rand -base64 32)
```

### 4. Environment Variables

**NEVER commit .env file!**

Add to `.gitignore`:
```
.env
.env.*
!.env.example
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Run new migrations
docker-compose exec api python manage.py migrate
docker-compose exec api python manage.py collectstatic --noinput
```

### Database Backups

**Automated backup script** (`backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec -T postgres pg_dump -U postgres neighborhood_library > $BACKUP_DIR/db_$DATE.sql

# Volume backups
docker run --rm \
  -v neighborhood-library-platform_postgres_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/postgres_data_$DATE.tar.gz /data

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Monitoring

```bash
# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a

# Monitor resource usage
docker stats

# Check logs for errors
docker-compose logs --tail=100 api | grep ERROR
```

## 🌐 Cloud Platform Deployment

### AWS EC2

1. Launch EC2 instance (Ubuntu 22.04 LTS recommended)
2. Configure security groups (ports 80, 443, 22)
3. Install Docker and Docker Compose
4. Clone repository and follow deployment steps
5. Optional: Use RDS for PostgreSQL, S3 for media files

### DigitalOcean Droplet

```bash
# One-liner setup
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER

# Clone and deploy
git clone <repo-url>
cd neighborhood-library-platform
cp .env.example .env
# Edit .env
docker-compose --profile production up -d
```

### Google Cloud Platform

1. Create Compute Engine instance
2. Enable Cloud SQL for PostgreSQL (optional)
3. Configure firewall rules
4. Install Docker
5. Deploy application

## 📊 Performance Optimization

### Django Settings

```python
# In production settings
CONN_MAX_AGE = 600  # Database connection pooling
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}
```

### Docker Compose with Redis

Add to `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: library_redis
  restart: unless-stopped
  networks:
    - library_network
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### Scaling

```bash
# Scale API workers
docker-compose up -d --scale api=3

# Use load balancer in nginx config
upstream api_backend {
    server api_1:8000;
    server api_2:8000;
    server api_3:8000;
}
```

## 🐛 Common Deployment Issues

### Issue: Database connection refused

**Solution:**
```bash
# Check postgres is running
docker-compose ps postgres

# Check connectivity
docker-compose exec api nc -zv postgres 5432

# Restart postgres
docker-compose restart postgres
```

### Issue: Static files not loading

**Solution:**
```bash
# Collect static files
docker-compose exec api python manage.py collectstatic --noinput --clear

# Check permissions
docker-compose exec api ls -la /app/staticfiles

# Restart nginx
docker-compose restart nginx
```

### Issue: Permission denied errors

**Solution:**
```bash
# Fix ownership
sudo chown -R 1000:1000 backend/logs backend/media

# Or adjust in Dockerfile
USER appuser
```

### Issue: Out of memory

**Solution:**
```bash
# Limit container memory
docker-compose.yml:
  api:
    deploy:
      resources:
        limits:
          memory: 1G
```

## 📋 Environment-Specific Configurations

### Development
```bash
DEBUG=True
DJANGO_LOG_LEVEL=DEBUG
```

### Staging
```bash
DEBUG=False
DJANGO_LOG_LEVEL=INFO
ALLOWED_HOSTS=staging.yourdomain.com
```

### Production
```bash
DEBUG=False
DJANGO_LOG_LEVEL=WARNING
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
```

## ✅ Post-Deployment Verification

```bash
# 1. Health checks
curl http://yourdomain.com/health/

# 2. API endpoints
curl http://yourdomain.com/api/v1/books/

# 3. Static files
curl http://yourdomain.com/static/admin/css/base.css

# 4. Database connection
docker-compose exec api python manage.py dbshell

# 5. Logs are clean
docker-compose logs --tail=50 | grep -i error

# 6. SSL certificate (if applicable)
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## 🆘 Rollback Procedure

```bash
# 1. Tag current state
git tag -a v1.0.1 -m "Before deployment"

# 2. If deployment fails, rollback
git checkout v1.0.0  # Previous stable version

# 3. Rebuild
docker-compose down
docker-compose up -d --build

# 4. Restore database if needed
docker-compose exec -T postgres psql -U postgres neighborhood_library < backup.sql
```

---

**Need help?** Check the main [README.md](../README.md) or open an issue.
