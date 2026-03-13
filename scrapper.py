import requests
from bs4 import BeautifulSoup

# Job site
URL = "https://careers.nomura.com/Nomura/go/Career-Opportunities-Asia-Pacific/9051000/"

# Keywords based on your interest
KEYWORDS = [
    "data scientist",
    "analytics",
    "quant",
    "quantitative",
    "model validation",
    "stress testing",
    "risk model",
    "machine learning",
    "data science"
]

def is_relevant(text):
    text = text.lower()

    for keyword in KEYWORDS:
        if keyword in text:
            return True

    return False


def scrape_jobs():

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    rows = soup.find_all("tr")

    for row in rows:

        cols = row.find_all("td")

        if len(cols) >= 3:

            title = cols[0].text.strip()
            division = cols[1].text.strip()
            location = cols[2].text.strip()

            combined_text = title + " " + division

            if is_relevant(combined_text):

                job = {
                    "title": title,
                    "division": division,
                    "location": location
                }

                jobs.append(job)

    return jobs


def main():

    jobs = scrape_jobs()

    print("\nRelevant Jobs Found:\n")

    for job in jobs:

        print("Title:", job["title"])
        print("Division:", job["division"])
        print("Location:", job["location"])
        print("-" * 40)


if __name__ == "__main__":
    main()