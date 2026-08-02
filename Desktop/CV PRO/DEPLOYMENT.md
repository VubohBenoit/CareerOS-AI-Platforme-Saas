# CareerOS AI - Deployment Guide

## Quick Deploy to AWS

###  Step 1: Prepare Backend (EC2)
```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@your-instance-ip

# Clone repo
git clone https://github.com/VubohBenoit/CareerOS-AI-Platforme-Saas.git
cd CareerOS-AI-Platforme-Saas/backend

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run production
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Step 2: Prepare Frontend (Vercel/S3+CloudFront)
```bash
cd frontend

# Build
npm run build

# Deploy to Vercel (recommended - automatic)
vercel --prod

# OR Deploy to S3
aws s3 sync .next/static s3://your-bucket/static
aws s3 sync public s3://your-bucket/
```

### Step 3: Database (RDS PostgreSQL)
```bash
# Update backend to use RDS
export DATABASE_URL=postgresql://user:pass@your-rds-endpoint/careerosdb

# Run migrations
# (when you have proper migrations setup)
```

### Step 4: Environment Variables
Set in AWS Systems Manager or EC2:
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
JWT_EXPIRATION_HOURS=24
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## Recommended AWS Stack:
- **Frontend**: Vercel (recommended) or S3 + CloudFront
- **Backend**: EC2 + Gunicorn or Elastic Beanstalk  
- **Database**: RDS PostgreSQL
- **Domain**: Route53
- **SSL**: AWS Certificate Manager (free)

## Production Checklist:
- [ ] Switch to PostgreSQL (RDS)
- [ ] Set production environment variables
- [ ] Enable CORS for your domain only
- [ ] Add database migrations with Alembic
- [ ] Setup CloudWatch monitoring
- [ ] Add SSL/TLS certificate
- [ ] Configure backup strategy
- [ ] Setup email service (SendGrid/SES)

## Commands Cheatsheet:
```bash
# Backend production start
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000

# Frontend production build
npm run build && npm run start

# Database migrations
alembic upgrade head
```

**Est. Costs**: ~$30/month AWS (t3.micro EC2, db.t3.micro RDS, S3)
