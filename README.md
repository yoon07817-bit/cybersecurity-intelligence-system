# Security Digest System

An automated cybersecurity threat intelligence monitoring system that collects security news, analyses threats, generates summaries, stores intelligence data, and sends security notifications to registered users.

The system provides a Flask-based dashboard where authenticated users can view security intelligence, manage notification preferences, and administrators can manage user accounts.

---

# Project Features

## Automated Security Monitoring

The system automatically:

- Collects cybersecurity news from RSS feeds
- Filters security-related information
- Extracts article information
- Generates AI-based summaries
- Calculates security risk scores
- Classifies threats by severity:

  - Low
  - Medium
  - High
  - Critical

- Stores processed articles in a SQLite database

---

# User Features

Users can:

- Register an account
- Login securely
- Access the security dashboard
- View collected threat intelligence
- Search security articles
- Filter articles by:

  - Severity
  - Category

- Manage notification preferences


## User Notification Settings

Users can configure:

### Daily Security Digest

Receives a daily summary of collected cybersecurity intelligence.

### Critical Security Alerts

Receives immediate notifications when critical security threats are detected.

### Minimum Severity Threshold

Users can select the minimum threat level they want to receive:

- Low
- Medium
- High
- Critical

---

# Admin Features

Administrators have additional management capabilities.

Admin users can:

- View registered users
- Enable user accounts
- Disable user accounts
- Delete users
- Manage account status


Admin accounts use:

```
role = Admin
```

Normal users use:

```
role = User
```

---

# System Architecture

```
Security Digest System

                 Scheduler
                     |
        +------------+------------+
        |                         |
        ↓                         ↓

 Feed Ingestion            Alert Monitoring

        |                         |
        ↓                         ↓

 RSS Collection        Critical Threat Detection

        |                         |
        ↓                         ↓

 Threat Processing       Alert Evaluation

        |                         |
        ↓                         ↓

 Severity Scoring        Email Notification

        |
        ↓

 SQLite Database

        |
        ↓

 Flask Dashboard

        |
        ↓

 Authenticated Users
```

---

# Project Structure

# Core Application Files


## main.py

Main security digest workflow.

Functions:

- Fetches latest security articles
- Extracts article information
- Generates AI summaries
- Calculates threat scores
- Stores processed articles
- Executes daily digest workflow


---

## scheduler.py

Automation controller.

Functions:

- Runs scheduled background tasks
- Starts feed ingestion
- Executes Critical security monitoring
- Sends daily digest emails


Schedule:

```
Feed Ingestion

Every 15 minutes


Critical Alert Monitoring

Every hour


Daily Digest Email

07:00 AM daily
```

---

## alert_check.py

Critical threat monitoring module.

Functions:

- Checks newly collected security articles
- Performs threat scoring
- Identifies Critical severity threats
- Generates summaries for critical articles
- Saves Critical security information
- Triggers alert processing


---

## alert.py

Critical security alert notification module.

Functions:

- Evaluates whether an article requires an alert
- Checks user notification preferences
- Sends Critical security alert emails
- Prevents duplicate notifications
- Updates alert delivery status


---

## database.py

Database management module.

Functions:

- Creates database tables
- Stores security articles
- Stores user accounts
- Handles login tracking
- Manages notification preferences
- Supports admin user management
- Tracks alert delivery status


---

## config.py

Configuration module.

Contains:

- Email configuration
- API settings
- Environment variables


---

# Data Processing Modules


## fetcher.py

RSS collection module.

Functions:

- Reads security RSS feeds
- Downloads article metadata
- Returns article information


---

## extractor.py

Article extraction module.

Functions:

- Extracts full article content from URLs


---

## filter.py

Security filtering module.

Functions:

- Removes unrelated information
- Keeps cybersecurity-related articles


---

## summariser.py

AI summarisation module.

Functions:

- Converts long security reports into short summaries


---

## scorer.py

Threat scoring engine.

Functions:

- Calculates security risk score
- Assigns severity levels:

```
Low

Medium

High

Critical
```

---

# Dashboard

The system provides a Flask-based web dashboard.

Dashboard features:

- User authentication
- Security article viewing
- Search functionality
- Severity filtering
- Category filtering
- User settings management
- Admin user management


Admin users can:

- View users
- Enable accounts
- Disable accounts
- Delete users


---

# Database

The system uses SQLite.

Database file:

```
save_data.db
```

---

## Articles Table

Stores:

- Article title
- URL
- Source
- Category
- Published date
- Summary
- Severity
- Threat score
- Alert status
- Creation time


---

## Users Table

Stores:

- Email address
- Password hash
- User role
- Account status
- Login history
- Notification preferences


Example fields:

```
email

password_hash

role

account_status

receive_daily_digest

receive_critical_alerts

minimum_severity
```

---

# Email Notification System

The system provides two notification types.

---

## Daily Digest Email

Purpose:

Provides a daily summary of collected cybersecurity intelligence.

Frequency:

```
Daily at 07:00 AM
```

Workflow:

```
Database

     ↓

Collect today's articles

     ↓

Generate email content

     ↓

Send digest email
```

---

## Critical Security Alert

Purpose:

Immediately informs users about serious cybersecurity threats.

Triggered when:

- Threat severity is Critical
- User enabled Critical Alerts
- Alert has not already been sent


Flow:

```
Critical Threat Detected

        ↓

Store Article in Database

        ↓

Check User Alert Preferences

        ↓

Generate Alert Email

        ↓

Send Critical Notification

        ↓

Update Alert Status
```

---

# Installation

Create virtual environment:

```bash
python -m venv venv
```

Activate environment:

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the System


## Initialize Database

```bash
python database.py
```


## Start Dashboard

```bash
python dashboard/app.py
```


## Start Scheduler

```bash
python scheduler.py
```

---

# Testing


## Test Critical Alert System

```bash
python alert.py
```


## Test Critical Threat Monitoring

```bash
python alert_check.py
```


## Test Daily Digest Workflow

```bash
python main.py
```

---

# Security Implementation

The system implements:

- Password hashing using Werkzeug security
- User authentication
- Role-based access control
- Account status management
- User notification preferences
- Scheduled threat monitoring
- Critical alert notification system
- Duplicate alert prevention


---

# Future Improvements

Possible future improvements:

- Add more threat intelligence sources
- Add advanced dashboard visual analytics
- Add weekly digest functionality
- Add advanced user permission levels
- Integrate external threat intelligence APIs
- Improve threat scoring algorithms