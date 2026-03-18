import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import pytz
import os

KEYWORDS = [
    "data scientist",
    "analytics",
    "quant",
    "quantitative",
    "model validation",
    "stress testing",
    "risk",
    "machine learning",
    "data science"
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
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def scrape_nomura(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []
    rows = soup.select("table tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            title = cols[0].get_text(strip=True).split("\n")[0]
            location = cols[2].get_text(strip=True)
            link_tag = cols[0].find("a")
            if link_tag:
                link = "https://careers.nomura.com" + link_tag.get("href")
            else:
                link = url

            if is_relevant(title):
                jobs.append({
                    "Company": "Nomura",
                    "Title": title,
                    "Location": location,
                    "Link": link
                })
    return jobs

def generic_scraper(url, company):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    jobs = []

    for link in soup.find_all("a", href=True):
        text = link.get_text(strip=True)
        if is_relevant(text) and len(text) > 10:
            href = link["href"]
            if href.startswith("/"):
                href = url.rstrip("/") + href
            jobs.append({
                "Company": company,
                "Title": text,
                "Location": "Check site",
                "Link": href
            })
    return jobs

def main():
    all_jobs = []
    # This is the single file that will be updated every day
    master_filename = "Job_Listings_Master.xlsx"

    # 1. Scrape all sites
    for company, url in COMPANY_SITES.items():
        print(f"Checking: {company}")
        try:
            if company == "Nomura":
                jobs = scrape_nomura(url)
            else:
                jobs = generic_scraper(url, company)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"Error scraping {company}: {e}")

    # 2. Process newly scraped jobs
    df_new = pd.DataFrame(all_jobs)
    if df_new.empty:
        print("No new jobs found today.")
        return

    # Add a timestamp so you know when a job was first detected
    ist = pytz.timezone('Asia/Kolkata')
    df_new['Date Found'] = datetime.now(ist).strftime('%Y-%m-%d')

    # 3. Handle persistent storage (the Excel file)
    if os.path.exists(master_filename):
        print(f"Found existing master file. Merging data...")
        df_existing = pd.read_excel(master_filename)
        
        # Combine old and new data
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        print("Master file not found. Creating a new one.")
        df_final = df_new

    # 4. Remove Duplicates
    # We use 'Link' as the unique ID. 'keep=first' ensures that if a job 
    # was already there, we keep the original entry (and its 'Date Found').
    df_final = df_final.drop_duplicates(subset=["Link"], keep="first")

    # 5. Save the updated master list
    df_final.to_excel(master_filename, index=False)
    print(f"\nUpdate complete! {len(df_final)} unique jobs currently in {master_filename}")

if __name__ == "__main__":
    main()
