"""
Email notification service for German B1 Daily Duel.
Sends notification emails to the other 2 players when someone finishes the quiz.
Includes safe fallback and logging if SMTP is not configured.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List


def notify_other_players(
    active_player_id: str,
    active_player_name: str,
    score: int,
    total: int,
    daily_stats: Dict[str, Any],
    all_players: Dict[str, Any],
    settings: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Sends email to the other 2 players notifying them of the test completion.
    """
    other_players = [
        p for pid, p in all_players.items()
        if pid != active_player_id and p.get("email") and "@" in p.get("email", "")
    ]
    
    if not other_players:
        return {
            "success": True,
            "mode": "skipped",
            "message": "No other player emails registered."
        }
        
    enabled = settings.get("email_notifications_enabled", False)
    smtp_server = settings.get("smtp_server", "")
    smtp_port = settings.get("smtp_port", 587)
    smtp_user = settings.get("smtp_user", "")
    smtp_pass = settings.get("smtp_pass", "")
    
    # If not enabled or no credentials, provide clean simulation/mock log
    if not enabled or not smtp_user or not smtp_pass:
        recipient_names = ", ".join([p["name"] for p in other_players])
        return {
            "success": True,
            "mode": "simulated",
            "message": f"Simulated: Notification for {active_player_name}'s score ({score}/{total}) prepared for {recipient_names} (Enable SMTP in Settings to send live emails)."
        }
        
    # Attempt real SMTP transmission
    try:
        recipients = [p["email"] for p in other_players]
        avg_score = daily_stats.get("average_score", score)
        attempts = daily_stats.get("attempts_count", 1)
        
        subject = f"🇩🇪 [German Duel] {active_player_name} scored {score}/{total} today!"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f7f9fc; padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h2 style="color: #2563eb; margin-top: 0;">🇩🇪 German B1 Daily Duel Update</h2>
                <p style="font-size: 16px; color: #1e293b;">
                    <strong>{active_player_name}</strong> just completed today's 5 questions!
                </p>
                <div style="background-color: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; margin: 16px 0; border-radius: 6px;">
                    <p style="margin: 4px 0; font-size: 15px;"><strong>This Attempt:</strong> {score} / {total}</p>
                    <p style="margin: 4px 0; font-size: 15px;"><strong>Normalized Daily Average:</strong> {avg_score:.2f} / {total}</p>
                    <p style="margin: 4px 0; font-size: 15px;"><strong>Total Attempts Today:</strong> {attempts}</p>
                </div>
                <p style="font-size: 15px; color: #475569;">
                    Can you beat this score? Open the app and conquer today's <strong>Possessivartikel</strong> challenge!
                </p>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                <p style="font-size: 12px; color: #94a3b8; text-align: center;">
                    German B1 Daily Duel • Telugu & Kannada to German Translation Practice
                </p>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(html_content, "html"))
        
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipients, msg.as_string())
            
        return {
            "success": True,
            "mode": "sent",
            "message": f"Real email notifications successfully delivered to: {', '.join(recipients)}"
        }
    except Exception as e:
        return {
            "success": False,
            "mode": "error",
            "message": f"SMTP Error sending notification: {str(e)}"
        }
