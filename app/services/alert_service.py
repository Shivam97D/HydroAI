def check_and_alert(result):
    if result["risk_level"] == "HIGH":
        print("🚨 ALERT: High Flood Risk!")
        # later: send email