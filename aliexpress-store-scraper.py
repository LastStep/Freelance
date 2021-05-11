from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import time, sleep
import os, requests, re
from bs4 import BeautifulSoup as bs
import pandas as pd
from collections import defaultdict

store_url = 'https://zuanhe.aliexpress.com/store/2216017'

email = 'drohanyadav@gmail.com'
password = 'laststep'

products, page = defaultdict(list), 0

def login(email, password):
  login_url = 'https://login.aliexpress.com'
  chrome.get(login_url)
  sleep(2)
  chrome.switch_to_frame(0)
  sleep(2)
  try:
    chrome.find_element_by_xpath('//*[@id="fm-login-id"]').send_keys(email + Keys.TAB + password + Keys.ENTER)
  except:
    chrome.find_element_by_xpath('//*[@id="login"]/div/div/div[3]/button').click()
  sleep(2)

options = webdriver.ChromeOptions()
# options.add_argument('--no-sandbox')
# options.add_argument('headless')
# options.add_argument('--window-size=1920,1080')
# options.add_argument('--start-maximized')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument('log-level=3')
# options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
with webdriver.Chrome('chromedriver', options = options) as chrome:
  # login(email, password)
  last_url = ''
  chrome.get(store_url)
  while True:
    if chrome.current_url == last_url:
      break
    page += 1
    print(page)

    # sleep(1)
    site = bs(chrome.page_source, 'lxml')
    last_url = chrome.current_url
    print(site.prettify())
    results = site.find('div', {'class':'ui-box-body'})
    try:
      products['URL'].extend([i.a['href'][2:] for i in results.find_all('h3')])
      products['Price'].extend([i.text.strip() for i in results.find_all('b')])
    except AttributeError:
      break
    chrome.find_element_by_xpath('//*[@id="node-gallery"]/div[3]/span/ul/li[2]/a').click()
    sleep(2)
      
df = pd.DataFrame.from_dict(products)
df.to_csv('output.csv')
print(len(df))