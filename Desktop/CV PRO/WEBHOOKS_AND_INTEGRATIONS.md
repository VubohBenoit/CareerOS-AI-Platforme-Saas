# 🔗 Webhooks & Integrations Guide

## Webhook System

### Register Webhook Endpoint

```bash
curl -X POST http://localhost:8000/api/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourapp.com/webhook",
    "events": ["application.created", "application.updated", "offer.received"]
  }'
```

### Response
```json
{
  "webhook_id": "wh_1234567890",
  "url": "https://yourapp.com/webhook",
  "events": ["application.created", "application.updated", "offer.received"],
  "secret": "whsec_1234567890abcdef",
  "status": "active"
}
```

### Webhook Events

#### 1. Application Created
```json
{
  "event": "application.created",
  "user_id": "user_123",
  "application_id": "app_456",
  "job_id": "job_789",
  "company": "Google",
  "position": "Senior Software Engineer",
  "applied_at": "2024-01-08T16:00:00Z"
}
```

#### 2. Application Updated
```json
{
  "event": "application.updated",
  "application_id": "app_456",
  "old_status": "applied",
  "new_status": "phone_screen",
  "updated_at": "2024-01-08T16:05:00Z"
}
```

#### 3. Job Matched
```json
{
  "event": "job.matched",
  "user_id": "user_123",
  "job_id": "job_789",
  "company": "Google",
  "match_score": 0.87,
  "matched_at": "2024-01-08T16:10:00Z"
}
```

#### 4. Offer Received
```json
{
  "event": "offer.received",
  "user_id": "user_123",
  "application_id": "app_456",
  "company": "Google",
  "position": "Senior Software Engineer",
  "salary": 250000,
  "equity": "0.5%",
  "received_at": "2024-01-08T16:15:00Z"
}
```

### Webhook Verification

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    # Create HMAC signature
    expected_sig = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Compare signatures (constant-time comparison)
    return hmac.compare_digest(signature, expected_sig)

# Usage
payload = request.body.decode()
signature = request.headers.get('X-Webhook-Signature')
secret = 'whsec_1234567890abcdef'

if verify_webhook(payload, signature, secret):
    # Process webhook safely
    event_data = json.loads(payload)
else:
    # Invalid signature - reject
    return 403
```

## Integration Examples

### Slack Integration

```python
import requests
import json

def send_slack_notification(webhook_url, event_data):
    """Send job event to Slack"""
    
    if event_data['event'] == 'application.created':
        message = {
            "text": f"New Application: {event_data['position']} at {event_data['company']}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New Job Application*\n{event_data['company']} - {event_data['position']}"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Company:*\n{event_data['company']}"},
                        {"type": "mrkdwn", "text": f"*Position:*\n{event_data['position']}"},
                    ]
                }
            ]
        }
    
    elif event_data['event'] == 'offer.received':
        message = {
            "text": f"🎉 Offer Received from {event_data['company']}!",
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": "🎉 Offer Received"}
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Company:*\n{event_data['company']}"},
                        {"type": "mrkdwn", "text": f"*Salary:*\n${event_data['salary']:,}"},
                        {"type": "mrkdwn", "text": f"*Position:*\n{event_data['position']}"},
                        {"type": "mrkdwn", "text": f"*Equity:*\n{event_data['equity']}"},
                    ]
                }
            ]
        }
    
    response = requests.post(webhook_url, json=message)
    return response.status_code == 200
```

### Email Integration

```python
def send_email_notification(event_data, user_email):
    """Send email for job events"""
    
    subject = ""
    html_content = ""
    
    if event_data['event'] == 'application.created':
        subject = f"Application submitted to {event_data['company']}"
        html_content = f"""
        <html>
            <body>
                <h2>Application Submitted</h2>
                <p>You've successfully applied to:</p>
                <h3>{event_data['position']} at {event_data['company']}</h3>
                <p>Applied on: {event_data['applied_at']}</p>
            </body>
        </html>
        """
    
    elif event_data['event'] == 'offer.received':
        subject = f"Job Offer from {event_data['company']}!"
        html_content = f"""
        <html>
            <body style="font-family: Arial;">
                <h2 style="color: green;">Congratulations! 🎉</h2>
                <p>You've received an offer from {event_data['company']}</p>
                
                <div style="background: #f0f0f0; padding: 20px; border-radius: 5px;">
                    <h3>Offer Details</h3>
                    <p><strong>Position:</strong> {event_data['position']}</p>
                    <p><strong>Salary:</strong> ${event_data['salary']:,}/year</p>
                    <p><strong>Equity:</strong> {event_data['equity']}</p>
                </div>
                
                <p style="margin-top: 20px;">Review the offer in your CareerOS dashboard</p>
            </body>
        </html>
        """
    
    # Send via email service
    email_service.send_email(user_email, subject, html_content)
```

### Discord Integration

```python
def send_discord_notification(webhook_url, event_data):
    """Send job event to Discord"""
    
    embed = {
        "title": f"{event_data['event'].replace('_', ' ').title()}",
        "color": 3447003,  # Blue
        "fields": []
    }
    
    if event_data['event'] == 'application.created':
        embed["title"] = "📤 New Application"
        embed["fields"] = [
            {"name": "Company", "value": event_data['company']},
            {"name": "Position", "value": event_data['position']},
            {"name": "Applied", "value": event_data['applied_at']},
        ]
    
    elif event_data['event'] == 'offer.received':
        embed["title"] = "🎉 Offer Received!"
        embed["color"] = 3066993  # Green
        embed["fields"] = [
            {"name": "Company", "value": event_data['company']},
            {"name": "Position", "value": event_data['position']},
            {"name": "Salary", "value": f"${event_data['salary']:,}"},
            {"name": "Equity", "value": event_data['equity']},
        ]
    
    payload = {"embeds": [embed]}
    requests.post(webhook_url, json=payload)
```

### Zapier Integration

```bash
# Connect CareerOS to 1000+ apps via Zapier

1. Go to zapier.com
2. Create new Zap
3. Trigger: "Webhooks by Zapier" → "Catch Hook"
4. Get webhook URL from Zapier
5. Add URL to CareerOS webhooks:
   curl -X POST http://localhost:8000/api/webhooks/register \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://hooks.zapier.com/hooks/catch/...",
       "events": ["application.created", "offer.received"]
     }'
6. Create action (e.g., Google Sheets, Slack, Email)
7. Test webhook
```

## Testing Webhooks

```bash
# 1. Register test endpoint
ngrok http 8000  # Creates public URL for testing

curl -X POST http://localhost:8000/api/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-ngrok-url/webhook",
    "events": ["application.created", "offer.received"]
  }'

# 2. Send test webhook
curl -X POST http://localhost:8000/api/webhooks/test/wh_1234567890

# 3. View logs
curl http://localhost:8000/api/webhooks/wh_1234567890/logs

# 4. Check webhook payload
# Your server will receive:
curl -X POST https://your-webhook-url \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: sha256=..." \
  -d '{
    "event": "application.created",
    "user_id": "user_123",
    ...
  }'
```

## Production Checklist

- [ ] Verify webhook signatures
- [ ] Implement retry logic (3x with exponential backoff)
- [ ] Log all webhook events
- [ ] Monitor webhook delivery success rate
- [ ] Set up alerts for failed webhooks
- [ ] Test webhook at scale
- [ ] Implement rate limiting
- [ ] Use HTTPS for webhook endpoints
- [ ] Validate webhook payload schema
- [ ] Handle duplicate events

