# Security Digest System

An automated cybersecurity news monitoring system that:
- Fetches security RSS feeds
- Filters and scores threats
- Generates summaries
- Stores articles in a database
- Sends daily digest emails
- Sends critical security alerts automatically


# Project Structure

## Core Application Files

### main.py
Main daily digest workflow.

Functions:
- Fetches latest security news
- Extracts article content
- Filters articles
- Generates AI summaries
- Scores security risk
- Saves articles to database
- Sends daily digest email

Schedule:
- Runs every day at 07:00 AM through scheduler.py


### scheduler.py
Main automation controller.

Functions:
- Starts scheduled jobs
- Runs daily digest
- Runs security alert checks
- Logs execution status

Schedule:
- Daily digest → 07:00 AM
- Alert monitoring → Every hour


### alert_check.py
Hourly security monitoring system.

Functions:
- Fetches new RSS articles
- Checks for Critical severity
- Generates summaries for critical threats
- Saves critical articles
- Sends alert emails


### alert.py
Security alert email module.

Functions:
- Checks whether an article should trigger an alert
- Sends Critical security notifications
- Prevents duplicate alerts


### database.py
Database management module.

Functions:
- Creates database tables
- Saves articles
- Retrieves critical articles
- Marks alerts as sent


### config.py
Configuration settings.

Contains:
- Email configuration
- Environment variables
- API settings


# Data Processing Files


### fetcher.py
RSS feed collection module.

Functions:
- Reads RSS feeds
- Downloads articles
- Returns article data


### extractor.py
Article content extraction.

Functions:
- Extracts full article text from URLs


### filter.py
Article filtering system.

Functions:
- Removes irrelevant articles
- Keeps security-related content


### summariser.py
AI summary generator.

Functions:
- Converts long articles into short summaries


### scorer.py
Security risk scoring engine.

Functions:
- Calculates threat score
- Assigns severity:
  - Low
  - Medium
  - High
  - Critical


# Email Files


### emailer.py
Daily digest email sender.

Functions:
- Creates email content
- Sends digest emails


### html_email_test.py
Tests HTML email formatting.


### email_check.py
Checks email configuration and delivery.


### alert_test.py
Tests alert email functionality.


### alert_runner.py
Helper script for running alert testing.


# Database Files


### save_data.db
SQLite database.

Stores:
- Article title
- URL
- Source
- Category
- Summary
- Severity
- Score
- Alert status
- Creation time


### check_db.py
Database inspection tool.

Used to view saved articles.


### clear_db.py
Database cleanup tool.

Deletes stored data for testing.


### update_database.py
Database update/migration utility.


# Configuration Files


### rss_feeds.json
List of RSS security news sources.


### requirements.txt
Python dependencies required by the project.


### .env
Stores private configuration:

- Email credentials
- API keys


### .gitignore
Files excluded from Git:

- Virtual environment
- Database files
- Secret configuration files


# Dashboard


### dashboard/
Contains the web dashboard application.

Used for:
- Viewing security articles
- Monitoring threat information
- Displaying collected data


# Virtual Environment


### venv/
Python virtual environment.

Contains:
- Installed packages
- Project dependencies


# Running the System

Activate environment:

Windows:

venv\Scripts\activate


Install dependencies:

pip install -r requirements.txt


Start scheduler:

python scheduler.py


The scheduler will automatically:

1. Run daily digest at 07:00 AM
2. Check critical security alerts every hour
3. Log execution results