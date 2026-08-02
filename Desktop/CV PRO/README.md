# CareerOS AI - Intelligent Job Search Platform

AI-powered job search and application tracking platform with personalized recommendations.

## 🚀 Features

✅ **Smart Job Search** - Filter by skills, location, salary  
✅ **AI Recommendations** - ML-based job matching  
✅ **Application Tracking** - Monitor all applications  
✅ **Saved Searches** - Create job alerts  
✅ **Resume Parser** - Extract skills from CV  
✅ **Analytics Dashboard** - Track success rate  
✅ **Modern UI** - Responsive design  
✅ **JWT Authentication** - Secure access  

## 🛠️ Tech Stack

**Backend**: FastAPI + SQLAlchemy + SQLite  
**Frontend**: Next.js 14 + React + TypeScript + Tailwind  
**Auth**: JWT Tokens  
**Deployment**: AWS (EC2 + RDS + Route53)

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# http://localhost:8000
```

### Frontend  
```bash
cd frontend
npm install
npm run dev
# http://localhost:3007
```

## 📊 API Endpoints (All Working ✅)

- `POST /api/v1/auth/signup` - Register
- `POST /api/v1/auth/login` - Login  
- `GET /api/v1/jobs/` - List jobs
- `GET /api/v1/recommendations/` - AI recommendations
- `GET /api/v1/applications/` - Applications
- `GET /api/v1/analytics/dashboard` - Dashboard stats
- `GET /api/v1/favorites/` - Saved jobs
- `GET /api/v1/saved-searches/` - Saved searches

## 🚢 Deployment

See DEPLOYMENT.md for AWS setup with:
- EC2 for backend (Gunicorn + FastAPI)
- RDS PostgreSQL for database
- Vercel for frontend (or S3 + CloudFront)
- Route53 for domain
- SSL with AWS Certificate Manager

**Estimated Cost**: ~$30/month

## ✨ What's Included

✅ Backend: 6 API services (jobs, apps, recommendations, analytics, favorites, searches)  
✅ Frontend: 9 pages (dashboard, jobs, recommendations, applications, favorites, saved searches, analytics, profile, resume parser)  
✅ Error Handling: error boundaries + error messages on all pages
✅ Loading States: spinners on async operations  
✅ Database: SQLite (dev) / PostgreSQL (prod)  
✅ Authentication: JWT signup/login  
✅ Design: Modern UI with Lucide icons + responsive layout

## 📈 Next Steps

- [ ] Deploy to AWS
- [ ] Add dark mode
- [ ] Email notifications  
- [ ] Advanced filters
- [ ] WebRTC video interviews
- [ ] PDF export
- [ ] Mobile app

## 👨‍💻 Status

**MVP Complete** ✅ - All features working  
**Ready for Production** - Can deploy now  
**GitHub**: https://github.com/VubohBenoit/CareerOS-AI-Platforme-Saas

---

Built with ❤️ for smarter job searching
