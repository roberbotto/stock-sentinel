import requests
import re
import time
from urllib.parse import urljoin
from datetime import datetime

from bs4 import BeautifulSoup


base_url = "https://iqtrends.com/"


def get_timestamp(xlsx_path):
    pattern = r'\/(\d{10})__'
    match = re.search(pattern, xlsx_path)
    return int(match.group(1)) if match else None


def get_excel_links(raw_html: str):
    soup = BeautifulSoup(raw_html, 'html.parser')
    xlsx_links = []

    # Buscar la sección "Data Table Spreadsheets"
    if section_title := soup.find('h3', string="Data Table Spreadsheets"):
        if data_table_section := section_title.find_next('ul'):
            # Extraer los enlaces dentro de la sección
            for li in data_table_section.find_all('li'): # type: ignore
                a_tag = li.find('a', href=True)
                if a_tag and a_tag['href'].endswith('.xlsx'):
                    xlsx_links.append(a_tag['href'])

    return {get_timestamp(x):x for x in xlsx_links if get_timestamp(x) is not None}


def get_last_timestamp(ts_l: list):
    return sorted([i for i in ts_l])[-1]


def download_report(endpoint: str, session):
    url = urljoin(base_url, endpoint)
    r = session.get(url)
    if r.status_code == 200 and r.content:
        with open(f"{endpoint.split('/')[-1]}", "wb") as fd:
            fd.write(r.content)


def get_special_reports_html(session):
    session.headers.update({
        "Host": "iqtrends.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Referer": "https://iqtrends.com/index.php",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i"
    })

    print("- GET index.php")
    session.get(urljoin(base_url, "index.php"))
    time.sleep(1)

    print("- GET login_existing2.php")
    session.headers.update({"Referer": "https://iqtrends.com/"})
    r = session.get(urljoin(base_url, "login_existing2.php"))
    if r.status_code != 200:
        print(f"Error querying 'login_existing2.php' endpoint: {r.status_code}")
        return
    
    time.sleep(1)
    
    print("- POST login_existing2.php")
    session.headers.update({
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": "70",
        "Origin": "https://iqtrends.com",
        "Referer": "https://iqtrends.com/login_existing2.php",
    })
    data = {
        "frmAction": "1",
        "user-name": "roberbotto",
        "password":	"HEG4iRwKRiHGsC3EmtLP",
        "submit": ""
    }
    r = session.post(urljoin(base_url, "login_existing2.php"), data=data)
    if r.status_code != 200 or not r.history or r.history[0].status_code != 302:
        print(f"Error while login into IQTrends: {r.status_code}")
        return
    
    time.sleep(1)
    
    print("- GET members_home.php")
    session.headers.update({"Referer": "https://iqtrends.com/members_home.php"})
    del session.headers["Content-Type"]
    del session.headers["Content-Length"]

    r = session.get(urljoin(base_url, "members_home.php"))
    if r.status_code != 200:
        print(f"Error querying 'members_special_reports.php' endpoint: {r.status_code}")
        return
    
    time.sleep(1)

    print("- GET members_special_reports.php")
    session.headers.update({"Referer": "https://iqtrends.com/members_home.php"})
    r = session.get(urljoin(base_url, "members_special_reports.php"))
    if r.status_code != 200:
        print(f"Error querying 'members_special_reports.php: {r.status_code}")
        return
    
    return r.text
    
def main():
    
    with requests.Session() as session:
        
        print("Querying HTTP endpoint...")
        html = get_special_reports_html(session)
        if not html:
            print("Error: HTML not extracted from endpoint")
            return
        
        print("Extracting Excel links from HTML...")
        links = get_excel_links(html)
        last_timestamp = get_last_timestamp(list(links.keys()))
        # record last_timestamp
        
        if datetime.now().timestamp() > last_timestamp:  # FIXME esta comprobacion no es valida (siempre se va a cumplir)
            print(f"Downloading {links[last_timestamp]}")
            download_report(links[last_timestamp], session)

if __name__ == "__main__":
    main()
