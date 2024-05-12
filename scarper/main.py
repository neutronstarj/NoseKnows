import re
import csv
import requests
import time
import sys
import  urllib3 ##PoolManager, Request, httperror
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pymongo import MongoClient
import os

# Load your environment variables (assuming you have python-dotenv installed)
#from dotenv import load_dotenv
#load_dotenv()

# Setup MongoDB connections
#client_root = MongoClient(os.getenv('MONGO_URI_ROOT'))
#db_root = client_root.test  # Access the database with root user privileges

#client_fragrance = MongoClient(os.getenv('MONGO_URI_FRAGRANCE'))
#db_fragrance = client_fragrance.test  # Access the database with fragrance user privileges
#get back to here, what is this?
#fragrance_un= os.environ.get('FRAGRANCE_UN')
#fragrance_ps=os.environ.get('FRAGRANCE_PW')

def read_data(filename):
    with open(filename) as f:
        lines= f.read().split('.')

    return lines

def get_html(url):
    ua = UserAgent()
    headers={'User-Agent':ua.random}
    try:
        response=requests.get('https://www.nosetime.com'+url,headers)
    except requests.exceptions.HTTPError as e:
        print("URL cannot be found")
        return None
    except requests.exceptions.Timeout:
        print("Timeout error") #set up a retry, continue loop later
        return None
    except requests.exceptions.TooManyRedirects:
        print("too many redirects")
        return None
    except requests.exceptions.RequestException:
        print("request exceptions")
        return None
    return response


def get_brand_urls():
    """
    input : list of brand name alphabetical webpages url
    output : perfume brands name urls in a list 
    A dictionary of perfumes EN and Chinese name
    """
    ##example, click on d , see the urls, https://www.nosetime.com/pinpai/5-d.html
    lst = ['/pinpai/2-a.html','/pinpai/3-b.html','/pinpai/4-c.html',
           '/pinpai/5-d.html','/pinpai/6-e.html','/pinpai/7-f.html',
           '/pinpai/8-g.html','/pinpai/9-h.html','/pinpai/10-i.html',
           '/pinpai/11-j.html','/pinpai/12-k.html','/pinpai/13-i.html',
           '/pinpai/14-m.html','/pinpai/15-n.html','/pinpai/16-o.html',
           '/pinpai/17-p.html','/pinpai/18-q.html','/pinpai/19-r.html',
           '/pinpai/20-s.html','/pinpai/21-t.html','/pinpai/22-u.html',
           '/pinpai/23-v.html','/pinpai/24-w.html','/pinpai/25-x.html',
           '/pinpai/26-y.html','/pinpai/27-z.html']
    count =0
    brand_urls=[]
    brand_names=[]
    for url in lst:
        response=get_html(url)
        soup=BeautifulSoup(response.text,'html.parser')
        result = soup.find_all('a', {'class': 'imgborder'})
        for r in result:
            brand_urls.append(r.attrs['href'])
            name = r.next_sibling.text
            split = re.split(r'([a-zA-Z])+',name)
            brand_names[split[0]]=''.join(split[1:])
        time.sleep(5)
        print("scraped {} urls".format(count))
        count+=1
    return brand_urls,brand_names 

def scrape_first_page(brand_urls, range_start,range_end):
    """
    usage: go through each brand_url, scarpe the first page return all other page urls 
    then fo each page_url return the fragrance names
    """
    count =0
    for url in brand_urls[range_start,range_end]:
        response= get_html(url)
        if response==None:
            print("Get HTML break at #{} url".format(count))
            break
        soup = BeautifulSoup(response.text,'html.parser')
        perfume= soup.find_all('a',{'class':'imgborder'}) #scrape all 1st pages(brand)
        pages_raw= soup.find_all('div',{'class':'next_news'})
        with open ('data/perfumes_2.csv','a') as resultFile: 
            #iterate through each page , fetch perfume urls and store to csv
            wr=csv.writer(resultFile)
            for p in perfume:
                wr.writerow([p.attrs['href']])
        with open ('data/pages.csv','a') as resultFile:
            wr=csv.writer(resultFile)
            for page in pages_raw[0].find_all('a')[1:-2]:
                wr.writerows([page['href']])
        
        time.sleep(10)
        count+=1
        if count%10==0:
            print("scarped{] page urls}".format(count))
    print("done writing perfume urls to csv ")



def scarpe_other_pages(page_list):
    """go through each page other than the firstnpage
    at the bottom of first page it says how many pages left i mean """
    count =0
    for url in page_list:
        response=get_html(url)
        if response == None:
            print("Get HTML response breaked at {}".format(count))
            break
        soup=BeautifulSoup(response.text,'html.parser')
        perfume=soup.find_all('a',{'class':'imgborder'})
        with open ('data/perfumes_2.csv','a') as resultFile:
            wr=csv.writer(resultFile)
            for p in perfume:
                wr.writerow([p.attrs['href']])
        time.sleep(10)
        count+=1
        if count %10==0:
            print("Scarpe {} page urls".format(count))
        if count %90==0:
            print("take a break for 8 mins")
            time.sleep(60*8)
    print("Doen writing perfumes urls to csv")
    

def scarpe_perfume_page(perfume_urls):
    """Dcarpe one page html and store into mongodb
    input: list of perfume urls
    output: url,html, stored into mongoDb ec2 instance 
    """
    client =  MongoClient("mongodb+srv://<fragrance>:<fragrance954>@cluster0.8jtzc6g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    fragrance = client.fragrance
    perfume_html= fragrance.perfume_html
    count =0
    for url in perfume_urls:
        html_text = get_html(url).text
        if html_text==None:
            print("get HTML break at #{} url".format(count))
            break
        perfume_html.insert({'url':url,'html':html_text})
        count+=1

        if count %100 ==0:
            print("Scarped {} pages html ..".format(count))
    client.close()


def get_url_list(filename):
    """convert a csv file with \r\n delimiter to a list of strings
    input : csv file with \r\n delinminaer
    output : a list of urls
    """
    f = open(filename)
    data =[]
    for line in f:
        data_line= line.rstrip().split('\r\n')
        data.append(data_line[0])
    return data

if __name__ == '__main__':
    brands,brand_names = get_brand_urls()
    print ("writing csv file...")
    with open('data/brand_names.csv','wb') as resultFile:
        wr= csv.writer(resultFile,dialect='excel')
        for key, value in brand_names.items():
            wr.writerow([key.encode('utf-8'),value.encode('utf-8')])



    

