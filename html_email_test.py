from alert import send_alert_email

# Create a mock critical article payload for testing
mock_article = {
    "id": 9999,
    "title": "TEST SECURITY ALERT: System Delivery Verification",
    "summary": "This is a test notification to verify that the email dispatch pipeline and SMTP credentials are fully functional.",
    "severity": "Critical",
    "score": "10.0",
    "link": "https://www.google.com"
}

print("[TEST] Dispatching manual test alert email...")
send_alert_email(mock_article)
print("[TEST] Test execution complete. Check your inbox (and spam folder)!")