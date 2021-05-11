from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup as bs

import pandas as pd
from time import sleep
from collections import defaultdict


def initialise_driver(window_size='1920,1080'):
  options = webdriver.ChromeOptions()
  # options.add_argument(
  #     '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
  options.add_argument('--no-sandbox')
  options.add_argument('headless')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('log-level=3')
  options.add_argument(f'window-size={window_size}')
  # options.add_argument("--start-maximized")
  options.add_experimental_option(
      'excludeSwitches', ['enable-automation', 'enable-logging'])
  options.add_experimental_option("prefs",
      {"profile.default_content_setting_values.notifications": 2})
  driver = webdriver.Chrome('chromedriver', options=options)
  return driver


def get_reviews(url):
  driver.get(url)
  page = bs(driver.page_source, 'lxml')

  try:
    global PRICE
    PRICE = page.find('div', {'class':'original'}).text
  except:
    pass

  wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'common-reviews__list')))
  try:
    driver.find_element_by_xpath('/html/body/div[1]/div[3]/div[1]/div/div/i').click()
  except:
    pass

  reviews, page_no = [], 1
  while True:
    try:
      print(f'Page {page_no}')
      page = bs(driver.page_source, 'lxml')
      revs = page.find('div', {'class':'common-reviews__list'})
      reviews += revs.find_all('div', {'class':'common-reviews__list-item'})
      try:
        driver.find_element_by_css_selector('span.S-pagination__arrow-next.disable')
        break
      except:
        ele = driver.find_element_by_class_name('S-pagination__arrow-next').click()
        page_no += 1
        sleep(WAIT_TIME)
    except Exception as e:
      print(e)
      break
  return reviews


def scrape_review(review, key):
  info = review.find('div', {'class':'gd-detail'})
  info = info.find_all('span')
  for i in info:
    i = i.parent.text
    if 'More' in i:
      continue
    for k in ['Weight', 'Height', 'Bust']:
      if k in i:
        DATA[key][k] = i.split()[-2]

  rev = review.find('div', {'class':'rate-des'})
  DATA[key]['Review'] = rev.text if rev else ''

  try:
    fit = review.find('div', {'class':'rate-fit'})
    fit = fit.find_all('span')
    try:
      DATA[key]['Size'] = fit[1]['aria-label']
    except:
      pass
    try:
      DATA[key]['Color'] = fit[2]['aria-label']
    except:
      pass
  except:
    pass

  rating = review.find('div', {'class':'rate-star'})
  DATA[key]['Rating'] = rating['aria-label'][-1] if rating else ''

  imgs = review.find('div', {'class':'common-reviews__list-item-pic'})
  DATA[key]['Images'] = ' , '.join(img['data-src'] for img in imgs.find_all('img')) if imgs else ''


if __name__ == '__main__':

  URL = 'https://us.shein.com/Solid-Cut-Out-Back-High-Waist-Dress-p-2146683-cat-1727.html?scici=navbar_WomenHomePage~~tab01navbar05~~5~~webLink~~~~0'
  WAIT_TIME = 0

  DATA = defaultdict(dict)
  PRICE = ''

  with initialise_driver() as driver:
    wait = WebDriverWait(driver, 30)

    reviews = get_reviews(URL)
    for key, review in enumerate(reviews, 1):
      DATA[key]['Item'], DATA[key]['Price'] = URL, PRICE
      scrape_review(review, key)

  DF = pd.DataFrame.from_dict(DATA, orient='index')
  DF.to_excel('output.xlsx', index=False)
