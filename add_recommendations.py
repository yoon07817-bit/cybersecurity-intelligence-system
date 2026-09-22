from database import (
    create_table,
    save_recommendation
)



def add_default_recommendations():

    create_table()


    recommendations = [

        # ======================================
        # Vulnerability
        # ======================================

        (
            "Vulnerability",
            "Critical",
            "Immediately apply vendor security patches, update affected software, restrict unnecessary access, and monitor systems for exploitation attempts."
        ),

        (
            "Vulnerability",
            "High",
            "Install available security updates, review affected systems, remove unnecessary services, and monitor suspicious activity."
        ),

        (
            "Vulnerability",
            "Medium",
            "Schedule security updates, review system configurations, and monitor affected applications for unusual behaviour."
        ),



        # ======================================
        # Phishing
        # ======================================

        (
            "Phishing",
            "Critical",
            "Block malicious email sources, reset compromised credentials, enable multi-factor authentication, and investigate affected accounts."
        ),

        (
            "Phishing",
            "High",
            "Enable email security filtering, train users to identify phishing attempts, and review suspicious links and attachments."
        ),

        (
            "Phishing",
            "Medium",
            "Improve security awareness training, verify unexpected email requests, and enable MFA for important accounts."
        ),



        # ======================================
        # Malware
        # ======================================

        (
            "Malware",
            "Critical",
            "Immediately isolate infected devices, perform malware analysis, remove malicious software, and restore systems from clean backups."
        ),

        (
            "Malware",
            "High",
            "Run endpoint security scans, remove detected malware, review system logs, and monitor affected devices."
        ),

        (
            "Malware",
            "Medium",
            "Maintain updated antivirus protection, monitor suspicious files, and perform regular security scans."
        ),



        # ======================================
        # Ransomware
        # ======================================

        (
            "Ransomware",
            "Critical",
            "Disconnect affected systems, activate incident response procedures, restore data from secure backups, and investigate attacker entry points."
        ),

        (
            "Ransomware",
            "High",
            "Review backup availability, patch vulnerable systems, restrict access permissions, and monitor unusual encryption activity."
        ),



        # ======================================
        # Data Breach
        # ======================================

        (
            "Data Breach",
            "Critical",
            "Investigate exposed information, reset compromised credentials, review access logs, and apply additional data protection controls."
        ),

        (
            "Data Breach",
            "High",
            "Change affected passwords, review authentication activity, improve access controls, and monitor further exposure."
        ),

        (
            "Data Breach",
            "Medium",
            "Review data handling procedures, reduce unnecessary data exposure, and improve security monitoring."
        ),



        # ======================================
        # AI Security
        # ======================================

        (
            "AI Security",
            "High",
            "Review AI system permissions, protect sensitive information, monitor AI misuse, and apply security controls for AI services."
        ),

        (
            "AI Security",
            "Medium",
            "Review AI usage policies, monitor unusual AI behaviour, and improve security monitoring."
        ),



        # ======================================
        # Privacy
        # ======================================

        (
            "Privacy",
            "High",
            "Review exposed personal information, strengthen privacy controls, and ensure proper protection of sensitive data."
        ),

        (
            "Privacy",
            "Medium",
            "Review data collection processes, reduce unnecessary information storage, and improve privacy settings."
        ),



        # ======================================
        # Compliance
        # ======================================

        (
            "Compliance",
            "High",
            "Review security policies, perform compliance audits, update procedures, and ensure regulatory requirements are followed."
        ),

        (
            "Compliance",
            "Medium",
            "Monitor regulatory changes, improve documentation, and maintain security reporting processes."
        ),



        # ======================================
        # General Security
        # ======================================

        (
            "General Security",
            "Low",
            "Maintain regular security updates, monitor threat intelligence sources, and follow cybersecurity best practices."
        ),

    ]



    for category, severity, advice in recommendations:

        save_recommendation(
            category,
            severity,
            advice
        )



    print(
        "Security recommendations added successfully."
    )





if __name__ == "__main__":

    add_default_recommendations()