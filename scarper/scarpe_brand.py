#it should be the first step in scarpe 

import re
import csv
import requests
import time
import sys
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import os

def get_html(url):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get('https://www.nosetime.com' + url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return None
    except requests.exceptions.Timeout:
        print("Timeout error")
        return None
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return None
    return response

def get_brand_urls():
    lst = ['/pinpai/2-a.html', '/pinpai/3-b.html', '/pinpai/4-c.html',
           '/pinpai/5-d.html', '/pinpai/6-e.html', '/pinpai/7-f.html',
           '/pinpai/8-g.html', '/pinpai/9-h.html', '/pinpai/10-i.html',
           '/pinpai/11-j.html', '/pinpai/12-k.html', '/pinpai/13-l.html',
           '/pinpai/14-m.html', '/pinpai/15-n.html', '/pinpai/16-o.html',
           '/pinpai/17-p.html', '/pinpai/18-q.html', '/pinpai/19-r.html',
           '/pinpai/20-s.html', '/pinpai/21-t.html', '/pinpai/22-u.html',
           '/pinpai/23-v.html', '/pinpai/24-w.html', '/pinpai/25-x.html',
           '/pinpai/26-y.html', '/pinpai/27-z.html']
    count = 0
    brand_urls = []
    brand_names = {}
    for url in lst:
        response = get_html(url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            result = soup.find_all('a', {'class': 'imgborder'})
            for r in result:
                href = r.attrs['href']
                brand_urls.append(href)
                name_element = r.find_next_sibling()
                if name_element:
                    name = name_element.text.strip()
                    brand_names[href] = name
                    print(f"Extracted: {href} -> {name}")  # Debug print
            print(f"Scraped {len(result)} urls from {url}")
        else:
            print(f"Failed to fetch {url}")
        time.sleep(5)
        count += 1
    return brand_urls, brand_names

if __name__ == '__main__':
    brands, brand_names = get_brand_urls()
    print("Writing CSV file...")
    os.makedirs('data', exist_ok=True)  # Ensure the directory exists
    with open('data/brand_names.csv', 'w', newline='', encoding='utf-8') as resultFile:
        wr = csv.writer(resultFile)
        for key, value in brand_names.items():
            wr.writerow([key, value])
            print(f"Wrote to CSV: {key} -> {value}")  # Debug print
    print("CSV file writing completed.")
