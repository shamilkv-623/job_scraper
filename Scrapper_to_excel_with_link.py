import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


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

    for keyword in KEYWORDS:
        if keyword in text:
            return True

    return False


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

        if is_relevant(text):

            jobs.append({
                "Company": company,
                "Title": text,
                "Location": "Check site",
                "Link": link["href"]
            })

    return jobs


def main():

    all_jobs = []

    for company, url in COMPANY_SITES.items():

        print("Checking:", company)

        try:

            if company == "Nomura":
                jobs = scrape_nomura(url)

            else:
                jobs = generic_scraper(url, company)

            all_jobs.extend(jobs)

        except Exception as e:

            print("Error scraping", company, e)

    df = pd.DataFrame(all_jobs)

    filename = f"jobs_{datetime.today().date()}.xlsx"

    df.to_excel(filename, index=False)

    print("\nSaved jobs to:", filename)


if __name__ == "__main__":
    main()