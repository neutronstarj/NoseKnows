import csv
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def get_html(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get('https://www.nosetime.com' + url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return None
    return response

def read_brand_urls(filename):
    brand_urls = []
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            brand_urls.append(row[0])
    return brand_urls

def scrape_first_page(brand_urls, range_start, range_end):
    count = 0
    for url in brand_urls[range_start:range_end]:
        response = get_html(url)
        if response is None:
            print(f"Get HTML break at #{count} url.")
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        perfume = soup.find_all('a', {'class': 'imgborder'})
        pages_raw = soup.find_all('div', {'class': 'next_news'})

        with open('data/perfumes_2.csv', 'a', newline='') as resultFile:
            wr = csv.writer(resultFile)
            for p in perfume:
                wr.writerow([p.attrs['href']])

        with open('data/pages.csv', 'a', newline='') as resultFile:
            wr = csv.writer(resultFile)
            if pages_raw:
                page_links = pages_raw[0].find_all('a')
                if len(page_links) > 1:
                    for page in page_links[1:-2]:
                        wr.writerow([page['href']])

        time.sleep(10)
        count += 1
        if count % 10 == 0:
            print(f"Scraped {count} page urls...")
    print("Done writing perfume urls to csv! Congrats! Save returned pages_list!")

if __name__ == '__main__':
    brand_urls = read_brand_urls('data/brand_names.csv')
    scrape_first_page(brand_urls, 0, len(brand_urls))
