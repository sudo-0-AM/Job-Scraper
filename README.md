# 🕵️ Job Scraper Project

***This project scrapes job listings (title, company, description, skills, etc.) from job portals and exports the results into a clean CSV file for analysis.***

---

## 🚀 Features

- *Scrapes job listings* using ***Selenium + undetected-chromedriver***

- *Parses detailed job descriptions & company info* with ***BeautifulSoup***

- Cleans and structures the raw data into a formatted ***CSV***

- *Handles popups, alerts, and bot detection measures*

- Stores results with timestamped file names for organization

---

## 🛠️ Tech Stack

- Python

- Selenium (undetected-chromedriver)

- BeautifulSoup4

- Pandas

- LXML

- Requests

---

## 📖 Project Workflow

### User Input

- Job domain

- Location

- Experience level

### Scraping

- Selenium navigates to the site, fills forms, handles alerts & popups

- BeautifulSoup parses job cards and detail pages

### Data Handling

- Results stored as raw dicts/lists

- Cleaned & normalized with Pandas

- Exported as CSV with UTF-8 encoding

#### 🔍 Example Output (CSV Columns)

- Job Title

- Company Name

- City

- Experience

- Salary

- Job Description

- Key Skills

- Company Details

---

## 🤝 Collaboration Note

I built the scraping logic (navigation, parsing, popups, job detail extraction) entirely myself.
For the data formatting & structuring, I collaborated with ChatGPT, which helped me refine the raw scraped data into a clean dataset using Pandas.

This way, the project reflects both my problem-solving skills and my ability to collaborate with AI tools for better results.

---

## 📂 Project Structure
```
Job-Scraper/
│── main.py # Main automation script (execution flow)
│── variables.py # Variables (locators, URLs)
│── requirements.txt # Dependencies
│── Job-Search-Results # Auto-created folders with CSVs
    │── Job-Search-Results-*.csv
```

---

## 📂 Repo Setup
1. **Clone the repository**
    ```bash
   git clone https://github.com/sudo-0-AM/Job-Scraper.git
   cd Job-Scraper
2. **Install Dependencies**
    ```bash
    pip install -r requirements.txt
3. **Run the script**
    ```bash
   python main.py
   
---