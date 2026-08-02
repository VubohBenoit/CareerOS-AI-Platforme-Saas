# 🌐 Domain & SSL Setup Guide

## 1. Custom Domain Registration

### Option 1: Using Route 53 (AWS)
```bash
# Register domain through AWS Route 53
# Cost: $12/year for most domains

1. Go to AWS Route 53 Console
2. Click "Registered domains"
3. Register your domain (e.g., careerosai.com)
4. Wait for 1-2 days for registration to complete
```

### Option 2: Using Namecheap/GoDaddy
```bash
# Register at external registrar
# Then update nameservers to point to Route 53

1. Register domain at Namecheap.com
2. Go to Route 53 → Hosted Zones
3. Create hosted zone for your domain
4. Copy nameservers from Route 53
5. Update nameservers in Namecheap dashboard
6. Wait 24 hours for DNS propagation
```

## 2. SSL Certificate Setup

### Option 1: AWS Certificate Manager (FREE)
```bash
# Best option - completely free!

1. Go to AWS Certificate Manager (ACM)
2. Click "Request certificate"
3. Add domain names:
   - careerosai.com
   - *.careerosai.com
4. Choose DNS validation
5. Validate via Route 53 (automatic)
6. Certificate issued in ~30 minutes
```

### Option 2: Let's Encrypt (FREE via Certbot)
```bash
# For manual EC2 setup

sudo apt update
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d careerosai.com -d www.careerosai.com
```

## 3. CloudFront Distribution (CDN)

### Setup CloudFront for Frontend
```bash
# In AWS CloudFront Console

1. Create distribution
2. Origin domain: your-s3-bucket.s3.amazonaws.com
3. Viewer protocol policy: Redirect HTTP to HTTPS
4. Add certificate from ACM
5. Add alternate domain name: careerosai.com
6. Default root object: index.html
7. Create distribution

# Copy CloudFront domain name from distribution
# Add as CNAME in Route 53
```

## 4. Route 53 DNS Records

### Configure DNS Routing
```bash
# Create records in Route 53

# A Record (IPv4)
Type: A
Name: careerosai.com
Alias: Yes
Alias target: <EC2 Public IP>

# WWW Subdomain (CNAME)
Type: CNAME
Name: www.careerosai.com
Value: careerosai.com

# CloudFront Distribution
Type: A (Alias)
Name: careerosai.com
Alias target: <CloudFront Distribution>

# API Subdomain (if separate)
Type: A (Alias)
Name: api.careerosai.com
Alias target: <EC2 Load Balancer>
```

## 5. Elastic Load Balancer Setup

### Create ALB for Auto-scaling
```bash
# In EC2 → Load Balancers

1. Create Application Load Balancer
2. Name: careerosai-alb
3. Availability zones: Select 2+
4. Security group: Allow 80 (HTTP), 443 (HTTPS)
5. Target group: port 8000 (FastAPI backend)
6. Listener rules:
   - HTTPS (443): FastAPI backend
   - HTTP (80): Redirect to HTTPS
7. Add SSL certificate from ACM
8. Create load balancer

# Get ALB DNS name → Add to Route 53
```

## 6. Terraform Configuration

### Update terraform/main.tf
```hcl
# Add Route 53 records
resource "aws_route53_record" "website" {
  zone_id = aws_route53_zone.main.zone_id
  name    = "careerosai.com"
  type    = "A"
  alias {
    name                   = aws_lb.main.dns_name
    zone_id                = aws_lb.main.zone_id
    evaluate_target_health = true
  }
}

# Add SSL certificate
resource "aws_acm_certificate" "main" {
  domain_name       = "careerosai.com"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

# Add CloudFront distribution
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

    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }
  }

  restriction {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.main.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }
}
```

## 7. Environment Variables

### Update .env files
```bash
# backend/.env
DOMAIN=careerosai.com
API_URL=https://api.careerosai.com
ALLOWED_ORIGINS=https://careerosai.com,https://www.careerosai.com

# frontend/.env.local
NEXT_PUBLIC_API_URL=https://api.careerosai.com
NEXT_PUBLIC_DOMAIN=careerosai.com
```

## 8. Deploy & Test

```bash
# 1. Update DNS records
cd terraform
terraform apply

# 2. Test HTTPS
curl -I https://careerosai.com

# 3. Check certificate
openssl s_client -connect careerosai.com:443

# 4. Test DNS resolution
nslookup careerosai.com
dig careerosai.com

# 5. Verify CloudFront
curl -I https://careerosai.com -H "Host: careerosai.com"
```

## 9. SSL/TLS Best Practices

```bash
# Force HTTPS
# Add to nginx config
server {
    listen 80;
    server_name _;
    return 301 https://$server_name$request_uri;
}

# Add security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
```

## 10. Monitor & Maintain

```bash
# Monthly: Check certificate expiration
aws acm describe-certificate --certificate-arn <arn>

# Monitor DNS propagation
https://www.whatsmydns.net

# Test SSL rating
https://www.ssllabs.com/ssltest/

# Monitor uptime
https://uptimerobot.com
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DNS not resolving | Wait 24h, check nameserver, verify Route 53 records |
| SSL certificate error | Verify ACM certificate status, clear CloudFront cache |
| Mixed content warning | Ensure all resources use HTTPS, update API_URL in .env |
| High latency | Enable CloudFront caching, check region, optimize assets |

## Estimated Costs (Monthly)

- Route 53 domain: $12/year ($1/month)
- Route 53 hosted zone: $0.50
- ACM certificate: FREE
- CloudFront: $0.085/GB (varies)
- **Total: ~$2-5/month for domain & SSL**

---

**Next Steps:**
1. [ ] Register domain
2. [ ] Request SSL certificate in ACM
3. [ ] Create CloudFront distribution
4. [ ] Update Route 53 DNS records
5. [ ] Test HTTPS connection
6. [ ] Deploy to production
7. [ ] Enable HTTP → HTTPS redirect
8. [ ] Monitor certificate expiration

