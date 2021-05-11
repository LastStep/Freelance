from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import time, sleep
import os, requests, re
from bs4 import BeautifulSoup as bs
import pandas as pd
from collections import defaultdict
from sys import argv


search = 'https://www.officeworks.com.au/shop/officeworks/c/technology'


try:
  search = argv[1]
except:
  pass

def get_data(category):
  global data
  while True:
    for _ in range(5):
      sleep(1)
      chrome.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    # chrome.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    site = bs(chrome.page_source, 'lxml')
    
    try:
      results = site.find('div', {'class':'sc-bdVaJa sc-bwzfXH TileGrid__TileGridContainer-s1wbzn-0 kTADFA'})
      results = results.find_all('div', {'class':'ProductTile__Wrapper-sc-1dlojg1-0 epQByh'})
    except:
      break

    for res in results:
      data['Category'].append(category)
      try:
        data['Name'].append(res.find('h5').text.strip())
      except:
        data['Name'].append(None)
      try:
        data['Price'].append(res.find('div', {'class':'ProductPrice__Wrapper-sc-1ye3dgu-0 guXOLt'}).text.strip())
      except:
        data['Price'].append(None)

    try:
      flag = chrome.find_elements_by_xpath('//*[@id="product-view-container-browse"]/div[2]/div/div[3]/div/div/div/div[2]/div[2]/div[1]/div[2]/div/ul/ul/li')
      if flag[-1].text.strip() == 'Next':
        flag[-1].click()
        sleep(2)
      else:
        break
    except:
      break


if __name__ == '__main__':

  base = 'https://www.officeworks.com.au'

  options = webdriver.ChromeOptions()
  options.add_argument('--no-sandbox')
  options.add_argument('headless')
  options.add_argument('--window-size=1920,1080')
  options.add_argument('--start-maximized')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('log-level=3')
  options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
  with webdriver.Chrome('chromedriver', options = options) as chrome:
    chrome.get(search)
    sleep(2)
    site = bs(chrome.page_source, 'lxml')

    sub_categories = site.find_all('div', {'class':'sc-bdVaJa sc-bwzfXH eVPJMi'})[1]
    sub_categories = [(i.text.strip(), base + i['href']) for i in sub_categories.find_all('a')]

    for sub_category in sub_categories[2:]:
      data = defaultdict(list)
      main_category, sub_category = sub_category
      chrome.get(sub_category)
      sleep(2)
      site = bs(chrome.page_source, 'lxml')

      sub_sub_categories = site.find_all('div', {'class':'sc-bdVaJa sc-bwzfXH eVPJMi'})[2]
      sub_sub_categories = [(i.text.strip(), base + i['href']) for i in sub_sub_categories.find_all('a')]
      
      if len(sub_sub_categories) != 0:
        for sub_sub_category in sub_sub_categories:
          category, sub_sub_category = sub_sub_category
          chrome.get(sub_sub_category)
          sleep(2)

          try:
            site = bs(chrome.page_source, 'lxml')
            sub_sub_sub_categories = site.find_all('div', {'class':'sc-bdVaJa sc-bwzfXH eVPJMi'})[3]
            sub_sub_sub_categories = [(i.text.strip(), base + i['href']) for i in sub_sub_sub_categories.find_all('a')]

            if len(sub_sub_sub_categories) != 0:
              for sub_sub_sub_category in sub_sub_sub_categories:
                category, sub_sub_sub_category = sub_sub_sub_category
                chrome.get(sub_sub_sub_category)
                sleep(2)
                get_data(category)
            else:
              get_data(category)

          except Exception as e:
            print(e)
            get_data(category)
            
      else:
        get_data(main_category)

  
      df = pd.DataFrame.from_dict(data)
      df.to_csv('OfficeWorks - {}.csv'.format(main_category))
      print('Made File OfficeWorks - {}.csv'.format(main_category))