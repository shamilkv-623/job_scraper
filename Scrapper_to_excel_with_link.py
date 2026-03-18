import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os

# --- Configuration ---
KEYWORDS = [
    "data scientist", "analytics", "quant", "quantitative", 
    "model validation", "stress testing", "risk", 
    "machine learning", "data science"
]

COMPANY_SITES = {
    "Nomura": "https://careers.nomura.com/Nomura/go/Career-Opportunities-Asia-Pacific/9051000/",
    "Citi": "https://jobs.citi.com/",
    "Deloitte": "https://jobs.deloitte.com/",
    "MUFG": "https://careers.mufgamericas.com/",
    "Honeywell": "https://careers.honeywell.com/",
    "Goldman Sachs": "https://www.goldmansachs.com/careers/",
    "JPMorgan": "https://careers.jpmorgan.com/",
    "Morgan Stanley": "https://www.morganstanley.com/careers/",
    "HSBC": "https://www.hsbc.com/careers/",
    "Barclays": "https://home.barclays/careers/",
    "UBS": "https://www.ubs.com/careers/",
    "BlackRock": "https://careers.blackrock.com/",
    "KPMG": "https://home.kpmg/xx/en/home/careers.html",
    "EY": "https://careers.ey.com/"
}

def is_relevant(text):
    if not text: return False
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def scrape_nomura(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        rows = soup.select("table tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                title = cols[0].get_text(strip=True).split("\n")[0]
                location = cols[2].get_text(strip=True)
                link_tag = cols[0].find("a")
                link = "https://careers.nomura.com" + link_tag.get("href") if link_tag else url
                if is_relevant(title):
                    jobs.append({"Company": "Nomura", "Title": title, "Location": location, "Link": link})
        return jobs
    except Exception as e:
        print(f"Nomura scrape failed: {e}")
        return []

def generic_scraper(url, company):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if is_relevant(text) and len(text) > 10:
                href = link["href"]
                if href.startswith("/"):
                    href = url.rstrip("/") + href
                jobs.append({"Company": company, "Title": text, "Location": "Check site", "Link": href})
        return jobs
    except Exception as e:
        print(f"{company} scrape failed: {e}")
        return []

def main():
    all_jobs = []
    master_filename = "Job_Listings_Master.xlsx"

    # 1. Scrape All Sites
    for company, url in COMPANY_SITES.items():
        print(f"Checking: {company}...")
        if company == "Nomura":
            jobs = scrape_nomura(url)
        else:
            jobs = generic_scraper(url, company)
        all_jobs.extend(jobs)

    # 2. Convert new data to DataFrame
    df_new = pd.DataFrame(all_jobs)
    
    if df_new.empty:
        print("No jobs found today matching keywords.")
        # We don't exit here, because we still want to keep the existing file if it exists
        if not os.path.exists(master_filename): return
        df_new = pd.DataFrame(columns=["Company", "Title", "Location", "Link", "Date Found"])

    # Add timestamp for new entries
    ist = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(ist).strftime('%Y-%m-%d')
    if not df_new.empty:
        df_new['Date Found'] = current_date

    # 3. Merge with Master File
    if os.path.exists(master_filename):
        print(f"Merging with existing {master_filename}...")
        try:
            df_existing = pd.read_excel(master_filename)
            # Ensure the structure matches for a clean concat
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        except Exception as e:
            print(f"Error reading master file: {e}. Starting fresh.")
            df_final = df_new
    else:
        print("Creating new master file...")
        df_final = df_new

    # 4. Deduplicate
    # Keep the FIRST occurrence (preserves the original 'Date Found')
    if not df_final.empty:
        df_final.drop_duplicates(subset=["Link"], keep="first", inplace=True)
        # Optional: Sort by date so new ones are at the bottom (or top)
        df_final.sort_values(by="Date Found", ascending=False, inplace=True)

    # 5. Save
    try:
        df_final.to_excel(master_filename, index=False)
        print(f"Success! {master_filename} now contains {len(df_final)} unique jobs.")
    except Exception as e:
        print(f"Failed to save Excel file: {e}")

if __name__ == "__main__":
    main()
