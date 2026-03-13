import requests
from bs4 import BeautifulSoup
from plyer import notification


# Companies to monitor
COMPANY_SITES = {
    "Nomura": "https://careers.nomura.com/Nomura/go/Career-Opportunities-Asia-Pacific/9051000/",
    "Citi": "https://jobs.citi.com/",
    "Deloitte": "https://jobs.deloitte.com/",
    "MUFG": "https://careers.mufgamericas.com/",
    "Honeywell": "https://careers.honeywell.com/"
}


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


def is_relevant(text):

    text = text.lower()

    for keyword in KEYWORDS:
        if keyword in text:
            return True

    return False


def send_notification(job):

    title = job["title"][:60]

    message = f"{job['company']} | {job['location']}"
    message = message[:120]

    notification.notify(
        title=title,
        message=message,
        timeout=10
    )


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
            division = cols[1].get_text(strip=True)
            location = cols[2].get_text(strip=True)

            text = f"{title} {division}"

            if is_relevant(text):

                jobs.append({
                    "company": "Nomura",
                    "title": title,
                    "location": location
                })

    return jobs


def generic_scraper(url, company):

    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    for link in soup.find_all("a"):

        text = link.get_text(strip=True)

        if is_relevant(text):

            jobs.append({
                "company": company,
                "title": text,
                "location": "Check website"
            })

    return jobs


def main():

    all_jobs = []

    for company, url in COMPANY_SITES.items():

        print(f"\nChecking {company}...")

        try:

            if company == "Nomura":
                jobs = scrape_nomura(url)

            else:
                jobs = generic_scraper(url, company)

            all_jobs.extend(jobs)

        except Exception as e:

            print("Error scraping", company, e)

    print("\nRelevant Jobs Found:\n")

    for job in all_jobs:

        print("Company:", job["company"])
        print("Title:", job["title"])
        print("Location:", job["location"])
        print("-" * 40)

        send_notification(job)


if __name__ == "__main__":
    main()