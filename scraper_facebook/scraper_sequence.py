from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup as bs

import asyncio
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import string
from time import sleep
from collections import defaultdict


def initialise_driver(window_size='1920,1080'):
  options = webdriver.ChromeOptions()
  options.add_argument(
      '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
  options.add_argument('--no-sandbox')
  # options.add_argument('headless')
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


def website_allercatpro(sequence):
  try:
    driver.get('https://allercatpro.bii.a-star.edu.sg/')
    driver.find_element_by_xpath('//*[@id="seq"]').send_keys(f'{sequence[0]} {sequence[1]}')
    driver.find_element_by_xpath('/html/body/center/font/form/input[2]').click()

    ele = '/html/body/font/center/table[1]/tbody/tr[3]/td[9]'
    wait.until(EC.visibility_of_element_located((By.XPATH, ele)))
    result = driver.find_element_by_xpath(ele).text

    data[f'allercatpro'].append(result)
  except Exception as e:
    print('---FAILED---')
    data[f'allercatpro'].append('-')


def website_allermatch(sequence):
  url = 'http://www.allermatch.org/allermatchsearch/search'
  # headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
  for type in ['window', 'wordmatch']:
    form_data = {'seq':f'"{sequence[0]} {sequence[1]}"',
                 'method':type,
                 'cutOff':'35',
                 'wordlength':'6',
                 'database':'AllergenDB_propeptides_removed'}
    site = req.post(url, data=form_data)

    site = bs(site.text, 'lxml')
    try:
      table_length = len(site.find_all('table')[2].find_all('tr'))
      data[f'allermatch.org {type}'].append(False if table_length < 3 else True)
    except Exception as e:
      print(e)
      print('---FAILED---')
      data[f'allermatch.org {type}'].append('-')


def make_excel(data):
  df = pd.DataFrame.from_dict(data)
  cols_to_wrap = ['Sequence']
  writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
  df.to_excel(writer, sheet_name='Sheet1', index=False)

  # workbook = writer.book
  # worksheet = writer.sheets['Sheet1']
  # wrap_format = workbook.add_format({'text_wrap': True})
  #
  # d = dict(zip(range(26), list(string.ascii_uppercase)))
  # for col in df.columns.get_indexer(cols_to_wrap):
  #   excel_header = d[col] + ':' + d[col]
  #   worksheet.set_column(excel_header, None, wrap_format)
  writer.save()


def get_sequences(input_file):
  sequences = []
  with open(input_file, '+r') as file:
    lines = iter(file.readlines())
    for line in lines:
      sequences.append((line.strip(), next(lines).strip()))
  return sequences, len(sequences)


if __name__ == '__main__':
  input_file = 'input field - all.txt'

  data = defaultdict(list)

  sequences, total_sequences = get_sequences(input_file)

  req = requests.Session()

  with initialise_driver() as driver:
    wait = WebDriverWait(driver, 30)

    for k,sequence in enumerate(sequences[:100], 1):
      print(f'{k}/{total_sequences}')
      data['Sequence'].append(f'"{sequence[0]}\n{sequence[1]}"')
      website_allercatpro(sequence)

  make_excel(data)
