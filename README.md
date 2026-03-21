# Training ETL Project

A personal ETL pipeline for automating training plan collection, workout sheet generation and progress tracking — backed by PostgreSQL.

## Overview

This project scrapes training plans from a coach's portal, stores them in a relational PostgreSQL database, generates per-session Excel workout sheets, and imports completed workout data back into the database for progress tracking.

## Features

### ETL Pipeline
- Scrapes monthly training plans from a coach's website using Selenium and BeautifulSoup
- Parses and transforms plan data: exercises, sets, reps, weights, rest times
- Loads data into a normalised PostgreSQL schema with relationships between plans, training days and exercises

### Workout Sheet Generation
- Generates a per-session Excel file for each training day
- Each sheet includes: exercises, sets, reps, weight, rest time between sets and after exercise
- Checkboxes for tracking completed sets during the workout

### Progress Import
- After completing a session, import the filled-in Excel back into the database
- Stores actual weights and sets performed for progress tracking over time

## Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python, Selenium, BeautifulSoup |
| Database | PostgreSQL, psycopg2, pgAdmin |
| Export / Import | openpyxl |
| Config | python-dotenv |
| Environment | WSL / Linux |

## Project Structure

```
training-etl-project/
├── db/                  # Database schema
├── src/                 # Core logic: scraper, parser, DB layer, Excel generator
├── config.py            # App configuration
├── main.py              # CLI entry point
├── .env.example         # Environment variable template
└── requirements.txt
```

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL running locally or via pgAdmin
- Chrome + ChromeDriver (for Selenium)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/hubert-nitka/training-etl-project.git
cd training-etl-project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # on WSL/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

5. Set up the database schema:
```bash
psql -U your_user -d your_db -f db/schema.sql
```

6. Run the pipeline:
```bash
python main.py
```

## Database Schema

The schema is fully normalised and includes:
- **Monthly plans** — top-level container for each training cycle
- **Training days** — individual sessions within a plan
- **Exercises** — assigned to training days with sets, reps, weight and rest configuration
- **Completed sessions** — records of actual weights and sets performed, imported from Excel after each workout

## Status

Functional — actively used for personal training tracking.
