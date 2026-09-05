# AI SkinCare Analyzer – Setup Guide

## Step 1: Install Python packages

```bash
pip install -r requirements.txt
```

## Step 2: MySQL Database Setup

1. Open MySQL Workbench or command line
2. Run the schema file:

```sql
source database/schema.sql
```

## Step 3: Set your MySQL password in config.py

Open `config.py` and update:

```python
MYSQL_PASSWORD = 'your_mysql_password'
```

## Step 4: Seed the product database

```bash
python database/seed.py
```

## Step 5: Run the app

```bash
python app.py
```

Open browser: **http://localhost:5000**

---

## Project Structure

```
skincare_ai/
├── app.py                  # Flask entry point
├── config.py               # Configuration
├── requirements.txt
├── database/
│   ├── schema.sql          # MySQL tables
│   ├── seed.py             # Product data seeder
│   └── db.py               # DB helper
├── modules/
│   ├── auth.py             # Login / Register
│   ├── skin_ai.py          # AI skin analysis
│   ├── recommendation.py   # Routine + Product engine
│   ├── chatbot.py          # AI Chatbot logic
│   └── ingredients.py      # Ingredient analyzer
├── routes/
│   ├── analysis_routes.py
│   ├── product_routes.py
│   ├── chatbot_routes.py
│   └── history_routes.py
├── templates/              # HTML pages
└── static/
    ├── css/style.css
    └── uploads/            # User face photos
```
