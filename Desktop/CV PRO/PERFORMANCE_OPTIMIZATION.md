# ⚡ Performance Optimization Guide

## Backend Optimization

### 1. Database Query Optimization

#### Problem: N+1 Queries
```python
# ❌ BAD: N+1 queries
applications = db.query(Application).all()
for app in applications:
    user = db.query(User).filter(User.id == app.user_id).first()  # N queries!

# ✅ GOOD: JOIN query
applications = db.query(Application).join(User).all()
```

#### Solution: SQLAlchemy Eager Loading
```python
# Load related data in single query
applications = db.query(Application).options(
    joinedload(Application.user),
    joinedload(Application.job)
).all()
```

### 2. Database Indexing

```sql
-- Add indexes to frequently queried columns
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_application_user_id ON applications(user_id);
CREATE INDEX idx_application_status ON applications(status);
CREATE INDEX idx_job_company ON jobs(company);
CREATE INDEX idx_job_created_at ON jobs(created_at);

-- Composite indexes for common queries
CREATE INDEX idx_app_user_status ON applications(user_id, status);
CREATE INDEX idx_job_location_salary ON jobs(location, salary_min);
```

### 3. Redis Caching

```python
# backend/app/services/cache_service.py
from redis import Redis
import json
import hashlib

class CacheService:
    def __init__(self):
        self.redis = Redis(host='localhost', port=6379)
        self.ttl = 3600  # 1 hour
    
    def get_cached(self, key):
        """Get value from cache"""
        value = self.redis.get(key)
        return json.loads(value) if value else None
    
    def set_cached(self, key, value, ttl=None):
        """Set value in cache"""
        self.redis.setex(
            key,
            ttl or self.ttl,
            json.dumps(value)
        )
    
    def cache_key(self, prefix, *args):
        """Generate cache key"""
        data = f"{prefix}:{':'.join(str(a) for a in args)}"
        return hashlib.md5(data.encode()).hexdigest()

# Usage
cache = CacheService()

@app.get("/api/recommendations/{user_id}")
async def get_recommendations(user_id: str, db: Session):
    cache_key = cache.cache_key("recommendations", user_id)
    
    # Try cache first
    cached = cache.get_cached(cache_key)
    if cached:
        return cached
    
    # Compute if not cached
    recommendations = recommendation_service.get_recommendations(user_id, db)
    
    # Store in cache
    cache.set_cached(cache_key, recommendations)
    
    return recommendations
```

### 4. Query Pagination

```python
@app.get("/api/applications")
async def list_applications(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Paginate to avoid loading all data
    applications = db.query(Application).offset(skip).limit(limit).all()
    return applications

# Usage
# GET /api/applications?skip=0&limit=20
# GET /api/applications?skip=20&limit=20  # Next page
```

### 5. Async/Await Optimization

```python
# ❌ Blocking code
@app.post("/applications")
async def create_application(app_data, db: Session):
    db.add(app_data)
    db.commit()  # BLOCKING - waits for database
    
    # Send email - BLOCKING
    send_email(app_data.user_email, "Application submitted")
    
    return {"status": "success"}

# ✅ Non-blocking code
@app.post("/applications")
async def create_application(app_data, db: Session):
    db.add(app_data)
    db.commit()
    
    # Send email asynchronously
    await background_tasks.add_task(
        send_email,
        app_data.user_email,
        "Application submitted"
    )
    
    return {"status": "success"}
```

### 6. Connection Pooling

```python
# backend/app/db.py
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:password@localhost/careerosai",
    pool_size=20,  # Max connections
    max_overflow=10,  # Extra connections when needed
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections hourly
    echo=False  # Don't log SQL in production
)
```

---

## Frontend Optimization

### 1. Code Splitting

```typescript
// pages/dashboard.tsx
import dynamic from 'next/dynamic';

const RecommendationsComponent = dynamic(
  () => import('@/components/Recommendations'),
  { loading: () => <div>Loading...</div> }
);

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <RecommendationsComponent />
    </div>
  );
}
```

### 2. Image Optimization

```typescript
import Image from 'next/image';

// ❌ Bad
<img src="/company-logo.png" width="100" height="100" />

// ✅ Good
<Image
  src="/company-logo.png"
  width={100}
  height={100}
  priority={false}  // Lazy load
  alt="Company logo"
/>
```

### 3. API Response Caching

```typescript
// frontend/lib/api.ts
const cache = new Map();

export async function fetchJobs(filters) {
  const cacheKey = JSON.stringify(filters);
  
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }
  
  const response = await fetch(`/api/jobs?${new URLSearchParams(filters)}`);
  const data = await response.json();
  
  cache.set(cacheKey, data);
  
  // Invalidate cache after 5 minutes
  setTimeout(() => cache.delete(cacheKey), 5 * 60 * 1000);
  
  return data;
}
```

### 4. Virtual Scrolling (Long Lists)

```typescript
import { FixedSizeList } from 'react-window';

export function JobsList({ jobs }: { jobs: Job[] }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={jobs.length}
      itemSize={100}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style} className="job-item">
          <JobCard job={jobs[index]} />
        </div>
      )}
    </FixedSizeList>
  );
}
```

### 5. Bundle Size Optimization

```bash
# Analyze bundle size
npm run build
npx next-bundle-analyzer

# Output:
# next/image: 25KB
# lucide-react: 50KB
# tailwind: 35KB
# Total: 110KB (gzip)
```

---

## Infrastructure Optimization

### 1. Load Balancer Configuration

```hcl
# terraform/main.tf
resource "aws_lb_target_group" "api" {
  name        = "careerosai-api-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  
  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    path                = "/health"
    matcher             = "200"
  }
}

resource "aws_lb" "main" {
  name               = "careerosai-lb"
  internal           = false
  load_balancer_type = "application"
  
  enable_deletion_protection = true
  enable_http2              = true
  enable_cross_zone_load_balancing = true
}
```

### 2. Auto-Scaling Configuration

```hcl
# terraform/autoscaling.tf
resource "aws_autoscaling_group" "api" {
  name                = "careerosai-api-asg"
  vpc_zone_identifier = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  target_group_arns   = [aws_lb_target_group.api.arn]
  health_check_type   = "ELB"
  
  min_size         = 2
  max_size         = 10
  desired_capacity = 3
  
  launch_template {
    id      = aws_launch_template.api.id
    version = "$Latest"
  }
}

resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 60
  autoscaling_group_name = aws_autoscaling_group.api.name
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "api-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "70"
  alarm_actions       = [aws_autoscaling_policy.scale_up.arn]
}
```

### 3. CloudFront Distribution

```hcl
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "myS3Origin"
  }
  
  enabled = true
  
  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "myS3Origin"
    compress         = true
    
    viewer_protocol_policy = "redirect-to-https"
    
    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
    
    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }
  
  price_class = "PriceClass_100"  # Only US/Europe
}
```

---

## Monitoring Performance

### Key Metrics to Track

```
API Performance:
- Response time: Target <200ms (P95)
- Throughput: 1000+ req/sec
- Error rate: <0.1%
- Uptime: 99.9%+

Database:
- Query time: <100ms (P95)
- Connection pool: <80% usage
- Slow queries: <5/min
- Replication lag: <1s

Frontend:
- Page load: <2s
- TTI: <3s
- CLS: <0.1
- LCP: <2.5s

Infrastructure:
- CPU: <70%
- Memory: <80%
- Network: <80%
- Disk I/O: <70%
```

---

## Performance Checklist

### Before Launch
- [ ] Database indexes created
- [ ] Redis caching configured
- [ ] Load balancer setup
- [ ] Auto-scaling policies
- [ ] CloudFront distribution
- [ ] Code splitting enabled
- [ ] Image optimization
- [ ] Compression enabled

### Monthly Review
- [ ] Analyze slow queries
- [ ] Review database indexes
- [ ] Check cache hit rates
- [ ] Profile frontend bundles
- [ ] Review error logs
- [ ] Load test infrastructure
- [ ] Update documentation
- [ ] Plan optimizations

---

**Performance is a feature. Measure, optimize, repeat.** ⚡

