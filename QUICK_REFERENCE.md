# 🚀 Quick Deployment Reference

## One-Command Clone & Deploy

```bash
# 1. Clone repository
git clone <your-repo-url>
cd neighborhood-library-platform

# 2. Quick Start (Development/Demo)
./start.sh

# OR Manual Setup:
cp .env.example .env
nano .env  # Update SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS
docker-compose up -d

# Done! Access at http://localhost:3000
```

## Deployment Scripts

### Development/Demo (Automated)
```bash
./start.sh
# This script will:
# - Check prerequisites
# - Create .env if missing
# - Build and start all services
# - Run migrations and seed data
# - Create admin user
```

### Production Deployment
```bash
./start-prod.sh
# This script will:
# - Validate production configuration
# - Backup existing data
# - Deploy with production settings
# - Verify deployment
# - Provide post-deployment checklist
```

### Validation Only
```bash
./validate-docker.sh
# Run before deployment to catch configuration issues
```

## Essential Commands

### Startup
```bash
docker-compose up -d              # Start all services
docker-compose --profile production up -d  # With Nginx
docker-compose -f docker-compose.prod.yml up -d  # Production mode
```

### Management
```bash
docker-compose ps                 # Check status
docker-compose logs -f            # View logs
docker-compose logs -f api        # View API logs
docker-compose restart api        # Restart service
docker-compose down               # Stop all services
```

### Maintenance
```bash
# Update code and rebuild
docker-compose down
git pull
docker-compose up -d --build

# Run migrations
docker-compose exec api python manage.py migrate

# Create superuser
docker-compose exec api python manage.py createsuperuser

# Access database
docker-compose exec postgres psql -U postgres -d neighborhood_library
```

### Backup & Restore
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres neighborhood_library > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres neighborhood_library < backup.sql
```

### Debugging
```bash
# Shell access
docker-compose exec api bash
docker-compose exec frontend sh

# Check health
curl http://localhost:8000/api/health/

# View specific logs
docker-compose logs --tail=100 api | grep ERROR
```

## Port Configuration

| Service    | Default Port | Environment Variable |
|------------|-------------|---------------------|
| Frontend   | 3000        | FRONTEND_PORT       |
| API        | 8000        | API_PORT            |
| Nginx      | 80          | NGINX_PORT          |
| PostgreSQL | 5432        | POSTGRES_PORT       |

## Critical Environment Variables

```bash
# Security (MUST CHANGE!)
SECRET_KEY=<generate-secure-key>
DB_PASSWORD=<strong-password>
DJANGO_SUPERUSER_PASSWORD=<admin-password>

# Configuration
DEBUG=False                              # Production only
ALLOWED_HOSTS=yourdomain.com,localhost
CORS_ALLOWED_ORIGINS=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://yourdomain.com/api/v1
```

## Health Check URLs

- Frontend: http://localhost:3000/
- API: http://localhost:8000/api/health/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/schema/swagger-ui/

## Common Issues & Quick Fixes

### Database Connection Error
```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Port Already in Use
```bash
# Edit .env and change port
API_PORT=8001
# Then restart
docker-compose up -d
```

### Permission Denied
```bash
sudo chown -R $USER:$USER .
docker-compose down
docker-compose up -d
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

## Pre-Deployment Checklist

```bash
./validate-docker.sh  # Run validation script
```

Manual checks:
- [ ] .env file configured
- [ ] SECRET_KEY is unique and strong
- [ ] DEBUG=False for production
- [ ] Database password changed
- [ ] ALLOWED_HOSTS updated
- [ ] Ports available
- [ ] Docker and Docker Compose installed

## File Structure

```
neighborhood-library-platform/
├── docker-compose.yml         # Main compose file
├── docker-compose.prod.yml    # Production config
├── .env                       # Your configuration (create from .env.example)
├── .env.example               # Template
├── Dockerfile                 # Backend
├── nginx.conf                 # Reverse proxy
├── validate-docker.sh         # Validation script
├── frontend/
│   └── Dockerfile            # Frontend
└── backend/
    └── ...                   # Django app
```

## Access Points After Deployment

### Development Mode
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Admin: http://localhost:8000/admin

### Production Mode (with Nginx)
- Application: http://localhost (or your domain)
- All routes through Nginx proxy

## Default Credentials

**⚠️ Change immediately in production!**

- Username: admin (or DJANGO_SUPERUSER_USERNAME)
- Password: admin123 (or DJANGO_SUPERUSER_PASSWORD)

## Support Resources

1. **Detailed Documentation**
   - [README.md](README.md) - Complete guide
   - [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment details
   - [DOCKER_IMPROVEMENTS.md](DOCKER_IMPROVEMENTS.md) - What's included

2. **Validation**
   - Run `./validate-docker.sh` before deploying

3. **Logs**
   - `docker-compose logs -f` for live logs
   - `docker-compose logs --tail=100 api` for recent logs

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.
