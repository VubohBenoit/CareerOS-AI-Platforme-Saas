# 📊 Monitoring & Alerts Setup

## System Architecture

```
Application → Prometheus → Grafana
             ↓
             AlertManager → Slack/Email/PagerDuty
             ↓
             CloudWatch → AWS Dashboard
             ↓
             ELK Stack → Log aggregation
```

---

## 1. Prometheus Setup (Metrics Collection)

### Install Prometheus

```bash
# In terraform/monitoring.tf
resource "aws_instance" "prometheus" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.small"
  key_name      = aws_key_pair.deployer.key_name

  security_groups = [aws_security_group.monitoring.name]

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update
              sudo apt-get install -y prometheus
              
              sudo systemctl start prometheus
              sudo systemctl enable prometheus
              EOF
}
```

### Configure Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'careerosai-api'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'careerosai-db'
    static_configs:
      - targets: ['localhost:5432']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']
```

---

## 2. Grafana Dashboards

### Main Dashboard

```json
{
  "dashboard": {
    "title": "CareerOS AI - Main Dashboard",
    "panels": [
      {
        "title": "API Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~'5..'}[5m])"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "active_users_gauge"
          }
        ]
      },
      {
        "title": "Database Queries/sec",
        "targets": [
          {
            "expr": "rate(pg_stat_statements_calls[1m])"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "redis_keyspace_hits_total / (redis_keyspace_hits_total + redis_keyspace_misses_total)"
          }
        ]
      }
    ]
  }
}
```

### Business Metrics Dashboard

```
Signups (Today)
↓
Job Applications (Today)
↓
Premium Conversions (Today)
↓
MRR
↓
Active Users (30-day)
↓
Referral Rate
↓
NPS Score
```

---

## 3. Alert Rules

### Critical Alerts (Page On-Call)

```yaml
groups:
  - name: careerosai-critical
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~'5..'}[5m]) > 0.01
        for: 2m
        annotations:
          severity: critical
          summary: "High error rate (>1%)"
          description: "{{ $value | humanizePercentage }} errors in last 5m"

      - alert: APIDowntime
        expr: up{job="careerosai-api"} == 0
        for: 1m
        annotations:
          severity: critical
          summary: "API is down"
          description: "API has been down for {{ $value }} minutes"

      - alert: DatabaseDown
        expr: up{job="careerosai-db"} == 0
        for: 1m
        annotations:
          severity: critical
          summary: "Database is down"
          description: "Database connection lost"

      - alert: DiskSpaceAlarm
        expr: node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.1
        for: 5m
        annotations:
          severity: critical
          summary: "Low disk space (<10%)"
```

### Warning Alerts

```yaml
  - name: careerosai-warning
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        annotations:
          severity: warning
          summary: "High P95 latency (>1s)"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1073741824 > 1
        for: 5m
        annotations:
          severity: warning
          summary: "High memory usage (>1GB)"

      - alert: CacheHitRateLow
        expr: |
          (redis_keyspace_hits_total) / 
          (redis_keyspace_hits_total + redis_keyspace_misses_total) < 0.8
        for: 10m
        annotations:
          severity: warning
          summary: "Low cache hit rate (<80%)"

      - alert: DatabaseConnectionPoolHigh
        expr: pg_stat_activity_count > 80
        for: 5m
        annotations:
          severity: warning
          summary: "Database connection pool usage high"
```

---

## 4. Slack Integration

### Setup AlertManager for Slack

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m

route:
  receiver: 'slack'
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#careerosai-alerts'
        title: 'CareerOS AI Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
        send_resolved: true
```

### Slack Alert Templates

```
🔴 CRITICAL: API is down
Status: 🔴 Down for 2 minutes
Service: careerosai-api
Action: Page on-call engineer immediately
Link: https://grafana.careerosai.com/d/api-status

🟡 WARNING: High memory usage
Memory: 1.2GB / 2GB (60%)
Service: careerosai-api
Recommendation: Monitor and plan scaling
Link: https://grafana.careerosai.com/d/memory
```

---

## 5. CloudWatch Integration

### AWS CloudWatch Logs

```python
# backend/app/logging.py
import logging
import watchtower

# Setup CloudWatch logging
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    log_group='careerosai-api',
    stream_name='main'
)

logger = logging.getLogger(__name__)
logger.addHandler(cloudwatch_handler)

# Log events
logger.info('Application started', extra={
    'user_id': user_id,
    'action': 'login',
    'timestamp': datetime.now().isoformat()
})
```

### CloudWatch Alarms

```bash
# Create CloudWatch alarm for API errors
aws cloudwatch put-metric-alarm \
  --alarm-name CareerOS-HighErrorRate \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name HTTPErrorRate \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 60 \
  --threshold 0.05 \
  --comparison-operator GreaterThanThreshold \
  --alarm-actions arn:aws:sns:us-east-1:123456789:alert
```

---

## 6. Performance Monitoring

### Key Metrics to Monitor

```
API Performance:
├── Request latency (P50, P95, P99)
├── Throughput (requests/second)
├── Error rate (5xx errors)
├── Uptime (99.9%+)
└── Response time by endpoint

Database Performance:
├── Query execution time
├── Connection pool usage
├── Slow query log
├── Replication lag
└── Backup completion time

Cache Performance:
├── Hit rate (target: >80%)
├── Eviction rate
├── Memory usage
├── Key expiration rate
└── Latency

Frontend Performance:
├── Page load time (<2s)
├── Time to interactive (<3s)
├── Core Web Vitals
├── Error rate
└── User session duration
```

---

## 7. Custom Application Metrics

### Prometheus Metrics Collection

```python
# backend/app/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
job_applications = Counter(
    'job_applications_total',
    'Total job applications',
    ['status', 'company']
)

job_match_score = Histogram(
    'job_match_score',
    'Job match score distribution'
)

active_users = Gauge(
    'active_users_gauge',
    'Current active users'
)

api_response_time = Histogram(
    'http_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# Usage in endpoints
@app.post("/applications")
async def create_application(app_data):
    job_applications.labels(status='created', company=app_data.company).inc()
    
    start = time.time()
    # ... process application ...
    duration = time.time() - start
    
    api_response_time.labels(
        method='POST',
        endpoint='/applications'
    ).observe(duration)
    
    return {"status": "success"}
```

---

## 8. Error Tracking (Sentry)

### Setup Sentry for Error Tracking

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)

# Errors are automatically captured
@app.post("/applications")
async def create_application(app_data):
    try:
        # ... code ...
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise
```

### Sentry Dashboard

```
All Errors (Last 24h)
├── Database connection timeout (5 errors)
├── Authentication invalid token (3 errors)
├── Job API rate limit (10 errors)
└── PDF generation failed (2 errors)

Error Trends
├── Increasing: PDF generation
├── Stable: Database errors
├── Decreasing: Authentication errors
└── New: Email service timeout
```

---

## 9. Uptime Monitoring

### Uptime Robot

```
Monitor URLs:
- https://careerosai.com (Front-end)
- https://api.careerosai.com/health (Backend)
- https://careerosai.com/api/jobs (API)

Check Interval: Every 5 minutes
Alert: Down for >5 minutes
Contact: Slack + Email

Target: 99.9% uptime
```

---

## 10. Runbook

### On-Call Procedures

#### Alert: API is Down
```
1. Check API health endpoint:
   curl https://api.careerosai.com/health

2. Check logs in CloudWatch:
   aws logs tail careerosai-api --follow

3. Check EC2 instance status:
   aws ec2 describe-instance-status --instance-ids i-xxx

4. Restart service:
   ssh ubuntu@careerosai.com
   sudo systemctl restart careerosai

5. Monitor metrics for 5 minutes

6. If still down: Failover to replica

7. Post-mortem: Add to incident log
```

#### Alert: High Memory Usage
```
1. Check memory usage:
   aws cloudwatch get-metric-statistics \
     --metric-name MemoryUtilization \
     --start-time 2024-01-01T00:00:00Z \
     --end-time 2024-01-01T01:00:00Z \
     --period 60 \
     --statistics Maximum

2. Check for memory leaks:
   top -p $(pgrep -f gunicorn)

3. Check active connections:
   SELECT count(*) FROM pg_stat_activity;

4. Solutions (in order):
   a) Increase instance size (5 min)
   b) Restart service (2 min)
   c) Clear cache (1 min)
   d) Throttle traffic (realtime)

5. Post-incident: Optimize code
```

---

## Monitoring Checklist

Daily:
- [ ] Check Grafana main dashboard
- [ ] Review error logs (Sentry)
- [ ] Monitor uptime (UptimeRobot)
- [ ] Check CPU/Memory usage
- [ ] Verify backups completed

Weekly:
- [ ] Review performance trends
- [ ] Check database query performance
- [ ] Review user-reported issues
- [ ] Update runbooks
- [ ] Test failover procedures

Monthly:
- [ ] Capacity planning review
- [ ] Security audit logs
- [ ] Cost optimization review
- [ ] Disaster recovery drill
- [ ] Team retrospective

---

**Next: Set up monitoring infrastructure in AWS** 🔧

