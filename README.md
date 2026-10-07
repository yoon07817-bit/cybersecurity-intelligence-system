# Security Digest System

An automated cybersecurity threat intelligence monitoring system that collects security news, analyses threats, generates summaries, stores intelligence data, and sends security notifications to registered users.

The system provides a Flask-based dashboard where authenticated users can view security intelligence, manage notification preferences, and administrators can manage user accounts.

---

# Project Features

## Automated Security Monitoring

The system automatically:

- Collects cybersecurity news from RSS feeds
- Filters security-related information from the previous 24 hours
- Detects duplicate articles using article URLs
- Extracts article information
- Generates AI-assisted summaries using the Groq API
- Calculates security threat scores
- Classifies threats by severity:
  - Low
  - Medium
  - High
  - Critical
- Detects CVE identifiers when available
- Generates protection recommendations
- Stores processed intelligence data in a PostgreSQL database
- Sends security notifications to registered users

---

# User Features

Users can:

- Register an account
- Login
- Access the security dashboard
- View collected threat intelligence
- Search security articles
- Filter articles by:
  - Severity
  - Category
- View article summaries
- View CVE information
- View protection recommendations
- Manage notification preferences

## User Notification Settings

Users can configure their notification preferences.

### Daily Security Digest

Receives a daily summary of collected cybersecurity intelligence.

### Critical Security Alerts

Receives email notifications when Critical security information is detected.

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
- Review Critical security information
- Review CVE details
- Review protection recommendations
- Review alert status

Admin accounts use:

```text
role = Admin
```

Normal users use:

```text
role = User
```

---

# System Architecture

```text
Security Digest System

                 Scheduler
                     |
        +------------+------------+
        |                         |
        ↓                         ↓

 Feed Ingestion            Alert Monitoring

        |                         |
        ↓                         ↓

 RSS Collection         Critical Threat Detection

        |                         |
        ↓                         ↓

 24-Hour Filtering        Alert Evaluation

        |                         |
        ↓                         ↓

Duplicate Detection       Email Notification

        |
        ↓

Content Extraction

        |
        ↓

AI-Assisted Summarisation

        |
        ↓

Threat Classification

        |
        ↓

Severity Scoring

        |
        ↓

CVE Detection

        |
        ↓

Protection Recommendations

        |
        ↓

PostgreSQL Database

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

- Processes the main security information workflow
- Coordinates article processing
- Generates AI-assisted summaries
- Calculates threat scores
- Processes CVE information
- Stores processed information
- Supports the daily digest workflow

---

## scheduler.py

Automation controller.

Functions:

- Runs scheduled background tasks
- Starts feed ingestion
- Executes Critical security monitoring
- Sends daily digest emails
- Supports Test Mode for scheduler testing

Schedule:

```text
Feed Ingestion

Every 10 minutes


Critical Alert Monitoring

Every hour


Daily Digest Email

07:00 AM daily
```

---

## alert_check.py

Critical threat monitoring module.

Functions:

- Checks processed security articles
- Performs threat scoring
- Identifies Critical severity threats
- Processes Critical security information
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

- Creates and manages database tables
- Stores security articles
- Stores user accounts
- Manages notification preferences
- Supports admin user management
- Stores CVE information
- Stores protection recommendations
- Tracks alert delivery status

The final deployed system uses PostgreSQL.

---

## config.py

Configuration module.

Contains:

- Email configuration
- API settings
- Database configuration
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

- Extracts available article content from URLs
- Provides article content for further processing

---

## filter.py

Security filtering module.

Functions:

- Filters articles based on the configured time period
- Removes unrelated information
- Supports duplicate prevention
- Keeps relevant cybersecurity information

---

## summariser.py

AI summarisation module.

Functions:

- Processes article content using the Groq API
- Converts long security reports into concise summaries

---

## scorer.py

Threat scoring engine.

Functions:

- Identifies predefined security indicators
- Calculates security threat scores
- Assigns severity levels:

```text
Low

Medium

High

Critical
```

The scoring system uses multiple predefined indicators and keywords for different threat types.

---

## severity_filter.py

Severity filtering module.

Functions:

- Filters articles according to severity
- Supports severity-based dashboard and notification filtering

---

## cve_detector.py

CVE detection module.

Functions:

- Identifies CVE identifiers from processed security information
- Extracts available CVE information
- Stores detected CVE information

---

## add_recommendations.py

Protection recommendation module.

Functions:

- Generates protection recommendations
- Associates recommendations with relevant articles
- Stores recommendations in the database

---

# Dashboard

The system provides a Flask-based web dashboard.

Dashboard features:

- User authentication
- Security article viewing
- Search functionality
- Severity filtering
- Category filtering
- Article summaries
- CVE information
- Protection recommendations
- User settings management
- Admin user management

Admin users can:

- View users
- Enable accounts
- Disable accounts
- Delete users

---

# Database

The final deployed system uses PostgreSQL.

PostgreSQL stores:

- Security articles
- User accounts
- Notification preferences
- Threat scores
- Severity information
- CVE details
- Protection recommendations
- Alert status

## Why PostgreSQL?

SQLite was used during the earlier local development stage because it was simple to set up and suitable for initial development and testing.

The project was later migrated to PostgreSQL for the final deployed system because the application is a web-based system with multiple related data types, persistent data storage, scheduled processing, and a production deployment environment.

PostgreSQL provides a more suitable database environment for the final deployed application and works well with the Render deployment environment.

The migration was supported by:

```text
migrate_sqlite_to_postgres.py
```

The earlier SQLite database file is:

```text
save_data.db
```

The final deployed system uses PostgreSQL as its primary database.

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
- Notification preferences

Example fields:

```text
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

```text
Daily at 07:00 AM
```

Workflow:

```text
Database

     ↓

Collect relevant articles

     ↓

Generate email content

     ↓

Check user preferences

     ↓

Send digest email
```

---

## Critical Security Alert

Purpose:

Notifies users about Critical cybersecurity information.

Critical security monitoring runs:

```text
Every hour
```

Triggered when:

- Threat severity is Critical
- User has enabled Critical Alerts
- Alert has not already been sent

Flow:

```text
Critical Threat Detected

        ↓

Process Article

        ↓

Check User Alert Preferences

        ↓

Check Alert Status

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

# Database Configuration

The final system requires a PostgreSQL database.

The database connection is configured using:

```text
DATABASE_URL
```

Example:

```text
DATABASE_URL=your_postgresql_database_url
```

Other required configuration values, such as API and email credentials, are provided through environment variables.

---

# Running the System

## Start Dashboard

Run the Flask application using the configured application entry point:

```bash
python main.py
```

## Start Scheduler

```bash
python scheduler.py
```

The scheduler handles:

- Feed ingestion
- Critical security monitoring
- Daily Digest processing

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

## Test Pipeline

```bash
python test_pipeline.py
```

Test Mode can also be used to test scheduled functions without waiting for the normal production schedule.

---

# Render Deployment

The final web application is deployed using Render.

## Why Render?

Render was used to deploy the Flask web application so that the system could be accessed through a public web URL rather than only running locally.

Using Render also allows the deployed Flask application to connect with the PostgreSQL database and external services used by the system.

Deployment structure:

```text
User
   ↓
Render Public URL
   ↓
Flask Application
   ↓
PostgreSQL Database
```

External services include:

- Groq API for AI-assisted summarisation
- Gmail SMTP for email notifications
- PostgreSQL for persistent data storage

The deployed application uses environment variables for:

- PostgreSQL connection
- Groq API
- Email configuration
- Application secret configuration

A QR code can be provided to access the deployed application during demonstration.

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
- Environment-based configuration for sensitive information

---

# Testing and Evaluation

The system was tested across the main functions, including:

- RSS collection
- 24-hour filtering
- Duplicate detection
- Content extraction
- AI-assisted summarisation
- Threat classification
- Severity scoring
- CVE detection
- Protection recommendations
- PostgreSQL storage
- Dashboard functionality
- Critical Alerts
- Daily Digest
- User notification preferences
- Duplicate alert prevention
- Scheduler behaviour
- Render deployment

The evaluation showed that Security Digest can reduce repetitive monitoring and processing tasks.

Users do not need to continuously check the dashboard for Critical information because the system can send Critical Alerts by email when the configured alert conditions are satisfied.

The system is intended to support human review rather than replace human judgement for important security decisions.

---

# Limitations

## RSS Feed Dependency

The system depends on the availability and quality of third-party RSS feeds.

If a source is unavailable, delayed, or provides incomplete information, the system may not be able to collect or process the article correctly.

---

## AI-Assisted Summarisation

AI-assisted summaries make the review process faster, but they may not always capture every detail from the original article.

Important security information should therefore be checked against the original source.

---

## Rule-Based Threat and Severity Scoring

The threat and severity scoring uses predefined indicators and keywords.

Multiple indicators are included for different threat types to improve coverage, but the rules cannot cover every possible threat or new wording.

Therefore, some threats may not be fully recognised if they do not match the defined indicators.

---

## Email Ownership Verification

The current system does not fully verify whether a registered email address belongs to the user.

A user could therefore register using an email address that they do not control and would not reliably receive the intended security notifications.

---

## Lightweight Scope

Security Digest focuses on cybersecurity information monitoring, processing, prioritisation, CVE detection, recommendations, and alerting.

It is not intended to replace a full enterprise CTI or SIEM platform.

---

# Future Improvements

Possible future improvements:

- Add more threat intelligence sources
- Allow administrators to add and manage intelligence sources through the Admin Dashboard instead of modifying source configuration in code
- Implement email ownership verification
- Strengthen authentication and account verification
- Expand threat indicators and detection patterns
- Incorporate CVSS-based vulnerability analysis where applicable
- Add historical security analytics
- Add more notification channels
- Add advanced dashboard visual analytics
- Add advanced user permission levels
- Integrate additional external threat intelligence APIs
- Improve threat scoring algorithms