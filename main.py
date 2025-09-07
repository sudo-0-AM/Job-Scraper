import undetected_chromedriver as uc
from selenium.common import NoAlertPresentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import lxml
import requests

import os
import time
from datetime import datetime
from variables import *
import pandas as pd
import re
import argparse

# Setup Output
def setup_output():
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "Job-Search-Results")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%m_%d-%H_%M_")
    file_path = os.path.join(output_dir, "Job-Search-Results-" + timestamp + ".csv")
    log_print(":} Output Setup Done!!")
    return file_path

def log_print(msg):
    print(f"{datetime.now().strftime('%H-%M-%S')}| {msg}")


def handle_google(iframe_google, driver):
    try:
        driver.switch_to.frame(iframe_google)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "close"))).click()
        log_print(":} Google Popup was taken care of ;)")
    except Exception as e:
        log_print(":} Couldn't handle the Popup :(\nError:", e)

# Initialize the driver and look for the job
def initialize_and_begin(job,exp,loc):

    log_print(":} Initializing the Driver")
    options  = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)

    driver.get(URL)
    log_print(":} Landed on the Search Page")
    time.sleep(2)

    try:
        alert = driver.switch_to.alert
        log_print(f":- Alert Popped Up: {alert.text}")
        alert.dismiss()
    except NoAlertPresentException:
        pass

    try:
        found_google = driver.find_elements(By.CLASS_NAME, GOOGLE_POPUP)
        if found_google:
            handle_google(found_google[0], driver)
        driver.find_element(By.XPATH, JOB_SEARCH_BOX).send_keys(job)
        driver.find_element(By.XPATH, JOB_SEARCH_LOCATION).send_keys(loc)

        driver.find_element(By.XPATH, JOB_EXP_DROPDOWN).click()
        exp = temp.replace("REPLACE_ME", f"{exp}")
        driver.find_element(By.XPATH, exp).click()

        log_print(":} Entered your Job Preferences on the Search Page")
        WebDriverWait(driver,5).until(EC.element_to_be_clickable((By.XPATH, JOB_SEARCH_BUTTON))).click()
        time.sleep(4)
        log_print(":} Landed on the Main Page")
        found_job_alert = driver.find_elements(By.ID, JOB_ALERT_POPUP)
        if found_job_alert:
            driver.find_element(By.XPATH, JOB_ALERT_CLOSE).click()
            log_print(":} Job Alert Popup taken care of ;)")

        html = driver.page_source
    finally:
        driver.quit()
    return html

# Parsing the details page of jobs mentioned in the main page
def scraper_details_Page(link):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(link, headers=headers).text
    soup = BeautifulSoup(html, "lxml")
    job_description = soup.find("div", class_=JOB_DISC).text

    lines = job_description.splitlines()
    lines = lines[4:]
    lines = (line.strip() for line in lines if line.strip())
    job_description = "\n".join(lines)

    key_details = soup.find("div", class_=KEY_DETAILS)
    details = key_details.find_all("li", class_="clearfix")
    detail = dict()
    for d in details:
        detail[d.find("label").text.replace(":", "")] = d.find("span").text.replace(":", ";")


    key_skills = soup.find("div", class_=KEY_SKILLS)
    skills = key_skills.find_all("span", class_="jd-skill-tag")
    skill = list()
    for s in skills:
        skill.append(s.text)

    more = soup.find("div", class_=MORE)
    about = more.find_all("li", class_="clearfix")
    about_comp = dict()
    for a in about:
        about_comp[a.find("label").text.replace(":", "")] = a.find("span").text

    return job_description, detail, skill, about_comp

# Parsing the 1st search page for all jobs and pages associated to those jobs
def scraper_main_Page(html):
    log_print(":} Scraping the Main Page")

    soup = BeautifulSoup(html, "lxml")
    job_cards = soup.find_all("li", class_=JOB_CARD_CLASS)

    results = {"Job Title":[],"Company Name":[],"Job":[],"Job Description":[],
               "Concerned":[],"Key Skills":[],"Related":[]}
    for count, job_card in enumerate(job_cards, start=1):
        job_title = job_card.find("h2").text

        if not job_title:
            continue

        company_name = job_card.find("h3").text
        details = job_card.find("div", class_=DETAILS)
        info = details.find_all("li")
        details = dict()
        keys = ['City','Experience','Salary']
        for j,i in enumerate(info):
            details[keys[j]] = i.text

        link = job_card.find("a")["href"]

        job_description, detail, skill, about_comp = scraper_details_Page(link)

        results["Job Title"].append(job_title)
        results["Company Name"].append(company_name)
        results["Job"].append(details)
        results["Job Description"].append(job_description)
        results["Concerned"].append(detail)
        results["Key Skills"].append(skill)
        results["Related"].append(about_comp)

        log_print(f":- Scraped {count} Job")

    return results

# Handle the raw data and convert into a csv
def clean_text(value):
    if isinstance(value, str):
        # Replace tabs and carriage returns with space
        value = re.sub(r'[\t\r]+', ' ', value)
        # Collapse multiple newlines into ONE newline
        value = re.sub(r'\n+', '\n', value)
        return value.strip()
    elif isinstance(value, list):
        return [clean_text(v) for v in value]
    elif isinstance(value, dict):
        return {k: clean_text(v) for k, v in value.items()}
    return value

def data_handler(raw_data):
    df = pd.DataFrame(raw_data)

    log_print(":} Formatting data for a cleaner look")

    # Clean everything
    for col in df.columns:
        df[col] = df[col].apply(clean_text)

    new_cols = []
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, dict)).all():
            expanded = pd.json_normalize(df[col].tolist())
            expanded.columns = pd.MultiIndex.from_product([[col], expanded.columns])
            new_cols.append(expanded)
        else:
            new_cols.append(df[[col]])

    df = pd.concat(new_cols, axis=1)
    df.columns = [' '.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
    return df


def save_to_csv_file(df, file_path):
    df.to_csv(file_path, index=False, encoding='utf-8')
    log_print(f"Saved results to CSV file.")

def save_to_xlsx_file(df, file_path):
    df.to_excel(file_path, index=False)
    log_print(f"Saved results to Excel file.")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Job Scraper using Selenium")
    parser.add_argument("--job", type=str, required=True, help="Job title to search")
    parser.add_argument("--exp", type=str, required=True, help="Experience level")
    parser.add_argument("--loc", type=str, required=True, help="Job location('Entry Level', '1 Year', '2 Years','3 Years'...)")
    args = parser.parse_args()

    log_print(f"Searching for: {args.job}")
    log_print(f"Experience: {args.exp}")
    log_print(f"Location: {args.loc}")

    file_path = setup_output()

    html = initialize_and_begin(args.job,args.exp,args.loc)
    raw_data = scraper_main_Page(html)

    if not raw_data["Job Title"]:
        log_print(":} No Jobs found for your search :(\n:}Try Again Maybe")
        exit()

    data_frame = data_handler(raw_data)
    print(data_frame)
    save_to_csv_file(data_frame, file_path)
    save_to_xlsx_file(data_frame, file_path.replace(".csv",".xlsx"))
