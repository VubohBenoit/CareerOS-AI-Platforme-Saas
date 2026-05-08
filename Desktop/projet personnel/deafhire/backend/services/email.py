"""
Email Service — DeafHire
Sends interview invitations via SMTP.
Falls back to console logging if SMTP is not configured.
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from datetime import datetime
from typing import Optional

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def send_interview_invitation(
    to_email: str,
    candidate_name: str,
    session_id: str,
    scheduled_at: Optional[datetime],
    join_url: str,
) -> bool:
    """
    Send an interview invitation email to the candidate.
    Returns True on success, False on failure.
    """
    subject = f"Invitation à votre entretien — DeafHire ({session_id})"

    scheduled_str = (
        scheduled_at.strftime("%A %d %B %Y à %H:%M")
        if scheduled_at else "Dès que vous êtes prêt(e)"
    )

    html_body = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <style>
    body {{ font-family: Inter, Arial, sans-serif; background:#F9FAFB; margin:0; padding:32px; }}
    .card {{ background:#fff; border-radius:16px; padding:40px; max-width:560px; margin:0 auto; border:1px solid #E5E7EB; }}
    .logo {{ display:flex; align-items:center; gap:10px; margin-bottom:32px; }}
    .logo-mark {{ width:36px; height:36px; background:linear-gradient(135deg,#5B21B6,#06B6D4); border-radius:9px; display:flex; align-items:center; justify-content:center; }}
    .logo-text {{ font-size:1.2rem; font-weight:800; color:#111827; }}
    h1 {{ color:#111827; font-size:1.5rem; margin-bottom:8px; }}
    p {{ color:#6B7280; line-height:1.7; }}
    .info-box {{ background:#F5F3FF; border:1px solid #DDD6FE; border-radius:10px; padding:20px; margin:24px 0; }}
    .info-row {{ display:flex; gap:12px; margin-bottom:8px; }}
    .info-label {{ color:#7C3AED; font-weight:700; font-size:.85rem; min-width:100px; }}
    .info-value {{ color:#374151; font-size:.85rem; }}
    .btn {{ display:inline-block; background:#5B21B6; color:#fff; padding:14px 28px; border-radius:8px; text-decoration:none; font-weight:700; font-size:1rem; margin:24px 0; }}
    .btn:hover {{ background:#7C3AED; }}
    .footer {{ margin-top:32px; font-size:.75rem; color:#9CA3AF; border-top:1px solid #F3F4F6; padding-top:20px; }}
    .join-code {{ font-family:monospace; background:#F3F4F6; padding:4px 10px; border-radius:4px; font-size:.9rem; color:#5B21B6; font-weight:700; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="logo">
      <div class="logo-mark">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2">
          <path d="M11 6.5V4a2 2 0 0 0-4 0v5a2 2 0 0 0 4 0zm2 4V8a2 2 0 0 1 4 0v5a2 2 0 0 1-4 0zm-5 5.5a5 5 0 0 0 8 0"/>
        </svg>
      </div>
      <span class="logo-text">Deaf<strong>Hire</strong></span>
    </div>

    <h1>Bonjour {candidate_name} 👋</h1>
    <p>Vous êtes invité(e) à participer à un entretien via la plateforme <strong>DeafHire</strong>. La traduction LSF ↔ Texte sera active tout au long de l'entretien.</p>

    <div class="info-box">
      <div class="info-row">
        <span class="info-label">Code session</span>
        <span class="info-value"><span class="join-code">{session_id}</span></span>
      </div>
      <div class="info-row">
        <span class="info-label">Date</span>
        <span class="info-value">{scheduled_str}</span>
      </div>
    </div>

    <a href="{join_url}" class="btn">Rejoindre l'entretien →</a>

    <p>Ou copiez ce lien dans votre navigateur :<br/>
    <small style="color:#7C3AED;word-break:break-all">{join_url}</small></p>

    <p><strong>Avant l'entretien :</strong></p>
    <ul style="color:#6B7280;line-height:2">
      <li>Assurez-vous d'être dans un endroit bien éclairé</li>
      <li>Vérifiez que votre caméra est fonctionnelle</li>
      <li>Utilisez Chrome ou Edge pour une meilleure compatibilité</li>
    </ul>

    <div class="footer">
      <p>Ce message a été envoyé automatiquement par DeafHire.<br/>
      Pour toute question, contactez votre recruteur.</p>
    </div>
  </div>
</body>
</html>
"""

    text_body = (
        f"Bonjour {candidate_name},\n\n"
        f"Vous êtes invité(e) à un entretien via DeafHire.\n"
        f"Code de session : {session_id}\n"
        f"Date : {scheduled_str}\n\n"
        f"Lien de connexion :\n{join_url}\n\n"
        f"Rejoignez également via : join.html?session={session_id}\n\n"
        f"— L'équipe DeafHire"
    )

    if not settings.SMTP_HOST:
        logger.info(
            "[Email] SMTP non configuré — simulation envoi\n"
            f"  To      : {to_email}\n"
            f"  Subject : {subject}\n"
            f"  Link    : {join_url}"
        )
        return True  # Simulate success in demo mode

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = formataddr(("DeafHire", settings.SMTP_FROM))
        msg["To"]      = formataddr((candidate_name, to_email))

        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html",  "utf-8"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())

        logger.info(f"[Email] Invitation envoyée à {to_email}")
        return True

    except Exception as exc:
        logger.error(f"[Email] Échec envoi à {to_email}: {exc}")
        return False
