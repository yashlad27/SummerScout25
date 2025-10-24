# 🔒 Security Best Practices & Hardening Guide

## Current Security Status

Your job tracker application has several security measures in place. This document outlines improvements and best practices.

---

## 🔐 1. Secrets Management

### ✅ Currently Implemented
- `.env` file for sensitive credentials (NOT committed to Git)
- `.gitignore` includes `.env` to prevent accidental commits
- Docker uses environment variables instead of hardcoded secrets

### 🚨 **CRITICAL: Protect Your Credentials**

#### Your `.env` file contains:
- **SMTP Password**: Gmail app password for email notifications
- **Database Credentials**: PostgreSQL username/password
- **Redis URL**: Connection string

#### Best Practices:

1. **Never commit `.env` to Git**
   ```bash
   # Verify .env is ignored
   git status --ignored | grep .env
   ```

2. **Rotate Gmail App Password if exposed**
   - Go to https://myaccount.google.com/apppasswords
   - Delete old password
   - Generate new one
   - Update `.env` file

3. **Use different credentials for production**
   ```bash
   # Example production .env with stronger passwords
   DATABASE_URL=postgresql+psycopg://jobtracker:STRONG_RANDOM_PASSWORD@db:5432/job_tracker
   SMTP_PASS=your_new_app_password_here
   ```

4. **Consider using a secrets manager** (for production deployments):
   - AWS Secrets Manager
   - HashiCorp Vault
   - 1Password Secrets Automation
   - Google Cloud Secret Manager

---

## 🛡️ 2. Network Security

### Current Setup
- Services run in isolated Docker network
- Only necessary ports exposed (5432, 6379, 8000)

### Improvements for Production

1. **Restrict Database Access**
   ```yaml
   # docker-compose.yml - Remove public port exposure
   db:
     ports:
       # - "5432:5432"  # REMOVE this in production
       # Only internal services can access DB
   ```

2. **Use Firewall Rules**
   ```bash
   # macOS firewall - block external access to Docker ports
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Docker.app
   ```

3. **Enable HTTPS for API** (if exposing publicly)
   - Use Let's Encrypt for free SSL certificates
   - Configure Nginx/Caddy as reverse proxy

---

## 🔍 3. Input Validation & Sanitization

### ✅ Currently Implemented
- Pydantic models validate configuration inputs
- SQL injection protection via SQLAlchemy ORM
- HTML escaping in email templates

### Additional Protections

```python
# Added to scrapers to prevent XSS attacks
from html import escape
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validate URL is safe."""
    try:
        parsed = urlparse(url)
        # Only allow HTTP(S)
        return parsed.scheme in ('http', 'https')
    except:
        return False
```

---

## 📊 4. Logging & Monitoring

### Current Logging
- Structured logging to stdout/stderr
- Docker captures logs automatically

### Security Enhancements

1. **Sensitive Data Redaction**
   - Passwords/tokens never logged
   - Email addresses partially masked in logs

2. **Log Monitoring**
   ```bash
   # Watch for suspicious activity
   docker-compose logs -f worker | grep -i "error\|failed\|unauthorized"
   ```

3. **Log Rotation** (prevent disk space issues)
   ```yaml
   # docker-compose.yml
   services:
     worker:
       logging:
         driver: "json-file"
         options:
           max-size: "10m"
           max-file: "3"
   ```

---

## 🚦 5. Rate Limiting & Anti-Abuse

### Current Protection
- `HTTP_MAX_RPS=2` limits scraping rate
- Playwright headless mode reduces detection
- Delays between requests

### Recommendations

1. **Respect `robots.txt`**
   - Check target site's scraping policies
   - Add User-Agent identification

2. **Implement Exponential Backoff**
   - Retry with increasing delays
   - Stop after max retries

3. **Monitor IP Reputation**
   - Avoid getting blocked/blacklisted
   - Use rotating proxies if needed (not recommended for internships)

---

## 🔒 6. Database Security

### Current Setup
- PostgreSQL with password authentication
- Database in isolated Docker network
- Non-root database user (`jobtracker`)

### Best Practices

1. **Change Default Password**
   ```env
   # In .env - use strong password
   DATABASE_URL=postgresql+psycopg://jobtracker:$(openssl rand -base64 32)@db:5432/job_tracker
   ```

2. **Enable SSL/TLS** (for remote databases)
   ```python
   # Add to database connection
   DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db?sslmode=require
   ```

3. **Regular Backups**
   ```bash
   # Backup database
   docker exec job_tracker_db pg_dump -U jobtracker job_tracker > backup.sql
   
   # Restore if needed
   docker exec -i job_tracker_db psql -U jobtracker job_tracker < backup.sql
   ```

4. **Limit Database Permissions**
   ```sql
   -- jobtracker user should only have necessary permissions
   GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO jobtracker;
   -- NOT: GRANT ALL PRIVILEGES
   ```

---

## 🐳 7. Docker Security

### Current Setup
- Official Docker images (postgres:16-alpine, redis:7-alpine)
- Non-root user in containers
- Health checks enabled

### Improvements

1. **Scan Images for Vulnerabilities**
   ```bash
   # Scan for CVEs
   docker scan postgres:16-alpine
   docker scan redis:7-alpine
   ```

2. **Use Specific Image Tags**
   ```yaml
   # Instead of 'latest', use specific versions
   db:
     image: postgres:16.1-alpine  # NOT postgres:latest
   ```

3. **Run as Non-Root User**
   ```dockerfile
   # In Dockerfile
   USER nobody:nogroup
   ```

4. **Limit Container Resources**
   ```yaml
   # docker-compose.yml
   services:
     worker:
       deploy:
         resources:
           limits:
             cpus: '1.0'
             memory: 1G
   ```

---

## 📧 8. Email Security

### Current Setup
- Gmail SMTP with app password (not real password)
- TLS encryption (STARTTLS)

### Best Practices

1. **Enable 2FA on Gmail**
   - Required for app passwords
   - Extra account protection

2. **Monitor Email Activity**
   - Check https://myaccount.google.com/device-activity
   - Review authorized apps

3. **Limit Email Rate**
   - Don't send too many emails (spam detection)
   - Current: batch emails (good!)

4. **Validate Email Addresses**
   ```python
   import re
   def is_valid_email(email: str) -> bool:
       pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
       return re.match(pattern, email) is not None
   ```

---

## 🔐 9. API Security (if exposing API publicly)

### Current API (port 8000)
- FastAPI application
- Internal use only (not exposed to internet)

### If Making Public:

1. **Add Authentication**
   ```python
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   
   security = HTTPBearer()
   
   @app.get("/jobs")
   async def get_jobs(credentials: HTTPAuthorizationCredentials = Depends(security)):
       # Verify token
       pass
   ```

2. **Enable CORS Properly**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # NOT "*"
       allow_credentials=True,
       allow_methods=["GET", "POST"],
       allow_headers=["*"],
   )
   ```

3. **Rate Limiting**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.get("/jobs")
   @limiter.limit("10/minute")
   async def get_jobs(request: Request):
       pass
   ```

---

## 🚨 10. Incident Response

### What to Do If Credentials Are Compromised

1. **Immediately rotate all secrets**
   ```bash
   # Change Gmail app password
   # Update .env
   # Restart services
   docker-compose restart worker beat
   ```

2. **Review access logs**
   ```bash
   docker logs job_tracker_db
   docker logs job_tracker_worker
   ```

3. **Check for unauthorized database changes**
   ```sql
   SELECT * FROM jobs ORDER BY created_at DESC LIMIT 50;
   SELECT * FROM alerts ORDER BY sent_at DESC LIMIT 50;
   ```

---

## ✅ Security Checklist

Use this checklist to verify your setup:

- [ ] `.env` file is in `.gitignore`
- [ ] Gmail has 2FA enabled
- [ ] Using Gmail app password (not real password)
- [ ] Strong database password (not `changeme123`)
- [ ] Database port not exposed publicly
- [ ] Docker images use specific tags (not `latest`)
- [ ] Regular database backups scheduled
- [ ] Monitoring logs for errors
- [ ] Email notifications working
- [ ] No credentials in code/Git history
- [ ] `.env.example` has no real secrets
- [ ] Services restart automatically (`restart: unless-stopped`)

---

## 🔄 Regular Maintenance

### Weekly
- Check logs for errors: `docker-compose logs --tail=100 worker`
- Verify email notifications working
- Review job count: Check database has new entries

### Monthly
- Update Docker images: `docker-compose pull && docker-compose up -d`
- Backup database: `docker exec job_tracker_db pg_dump...`
- Review and clean old job data if needed

### Quarterly
- Rotate Gmail app password
- Review and update dependencies
- Audit access logs

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)

---

## 🆘 Need Help?

If you suspect a security issue:
1. Stop all services immediately: `docker-compose down`
2. Review logs for suspicious activity
3. Rotate all credentials
4. Consider professional security audit for production use

---

**Remember**: This is a personal internship tracker. Security is important, but don't over-engineer. The measures above are appropriate for personal use. Production deployments need additional hardening.
