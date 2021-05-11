from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as bs
import pickle

import pandas as pd
from time import sleep
from os.path import isfile
from collections import defaultdict


def initialise_driver():
  options = webdriver.ChromeOptions()
  options.add_argument(
      '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
  options.add_argument('--no-sandbox')
  options.add_argument('headless')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('log-level=3')
  options.add_argument("--start-maximized")
  options.add_experimental_option(
      'excludeSwitches', ['enable-automation', 'enable-logging'])
  driver = webdriver.Chrome('chromedriver', options=options)
  return driver


def login(driver, username, password, cookie_file):
  url = 'https://www.oddsportal.com/login/'
  driver.get(url)
  try:
    driver.find_element_by_xpath('//*[@id="login-username1"]').send_keys(username + Keys.TAB + password + Keys.ENTER)
    # driver.find_element_by_xpath('//*[@id="login-password1"]').send_keys(password)
    # driver.find_element_by_xpath('//*[@id="col-content"]/div[2]/div/form/div[3]/button').click()
    sleep(3)
    save_cookies(driver, cookie_file)
    print('---Login Success---')
  except Exception as e:
    print('---Login Failed---')


def save_cookies(driver, cookie_file):
  pickle.dump(driver.get_cookies(), open(cookie_file, 'wb'))


def load_cookies(driver, cookie_file):
  cookies = pickle.load(open(cookie_file, 'rb'))
  for cookie in cookies:
    driver.add_cookie(cookie)
  return driver


def get_game_links(driver, url):
  global wait, baseUrl, page_first, page_last
  links, names, page = [], [], page_first

  while True:
    driver.get(url + f'#/page/{page}/')
    wait.until(EC.visibility_of_element_located((By.ID, 'tournamentTable')))
    site = bs(driver.page_source, 'lxml')

    if page == page_first:
      try:
        last_page = site.find('div', {'id':'pagination'})
        last_page = last_page.find_all('a')[-1]
        last_page = int(last_page['x-page'])
      except:
        last_page = 1

      if page_last == 0:
        page_last = last_page

    try:
      table = site.find('table', {'id':'tournamentTable'})
      table = table.find('tbody')
      table_td = table.find_all('td', {'class':'table-participant'})
      for td in table_td:
        names.append(td.text)
        links.append(baseUrl + td.find('a')['href'])
    except:
      break

    if page < last_page:
      if page == page_last:
        break
      page += 1
    else:
      break

  return links, names


def get_data(driver, link):
  global exclude_columns, wait
  data = defaultdict(list)
  driver.get(link)
  try:
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="odds-data-table"]/div[1]/table')))
  except Exception as e:
    print('---FAILED---')
    return None
  site = bs(driver.page_source, 'lxml')

  info = site.find('div', {'id':'col-content'})
  data['Name'] = info.find('h1').text
  time = info.find('p', {'class':lambda x:x and 'date' in x}).text
  time = time.split(', ')
  data['Day'], data['Date'], data['Time'] = time[0], time[1], time[2]
  data['Result'] = info.find('div', {'id':'event-status'}).text

  table = site.find('table', {'class':'table-main detail-odds sortable'})

  table_thead = site.find('thead')
  headers = table_thead.find_all('th')
  headers = [header.text.strip() for header in headers if header.text not in exclude_columns]

  table_tbody = table.find('tbody')
  for tr in table_tbody.find_all('tr'):
    tdd = tr.find_all('td')
    try:
      for key, value in zip(headers, tdd):
        data[key].append(value.text)
    except:
      pass

  try:
    table_tfoot = table.find('tfoot')
    avg = table_tfoot.find('tr', {'class':'aver'})
    avg = avg.find_all('td')
    for key, value in zip(headers, avg):
      data[key].append(value.text)
  except:
    pass
  try:
    table_tfoot = table.find('tfoot')
    hgst = table_tfoot.find('tr', {'class':'highest'})
    hgst = hgst.find_all('td')
    for key, value in zip(headers, hgst):
      data[key].append(value.text)
  except:
    pass

  return pd.DataFrame.from_dict(data)


if __name__ == '__main__':
  # Add a url and file name in variables below
  url = 'https://www.oddsportal.com/baseball/usa/mlb-2018/results/'
  output_filename = 'mlb-2018'
  # Input the range of pages you want to scrape.
  page_first = 1
  # Put page_last value as 0 (Zero), if you want to scrape all the pages
  page_last = 0
  # Add or Remove any specific column you dont want to show up in the result
  exclude_columns = ['', 'Payout']
  # Change username and password in these variables
  username = 'TONYGALE'
  password = 'TONYBOOKMAKER'

  cookie_file = 'cookies.pkl'
  baseUrl = 'https://www.oddsportal.com'

  with initialise_driver() as driver:
    wait = WebDriverWait(driver, 30)
    driver.get(baseUrl)

    print('---Logging In---')
    if isfile(cookie_file):
      driver = load_cookies(driver, cookie_file)
    else:
      login(driver, username, password, cookie_file)
    print('--------------')
    sleep(2)

    DF = pd.DataFrame()
    print(url)
    print('---Grabbing Links---')
    links, names = get_game_links(driver, url)
    print('--------------')

    for k,link in enumerate(links,1):
      print('--------------')
      print(f'{k}/{len(links)}')
      print(names[k-1])
      print(link)
      try:
        df = get_data(driver, link)
        if df is not None:
          DF = pd.concat([DF, df], ignore_index=True)
      except:
        print('---FAILED---')

    DF.to_csv(f'{output_filename}.csv', index=False, encoding='utf-8-sig')
    print('--------------')
    print(f'File Created {output_filename}.csv')
    print('--------------')
