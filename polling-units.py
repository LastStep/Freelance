from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
import pandas as pd

site_url = 'https://www.inecnigeria.org/elections/polling-units/'

DF = pd.DataFrame()

options = webdriver.ChromeOptions()
options.add_argument(
  '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
options.add_argument('--no-sandbox')
# options.add_argument('headless')
options.add_argument('--start-maximized')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('log-level=3')
options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
with webdriver.Chrome('chromedriver', options = options) as chrome:
  chrome.get(site_url)

  wait_time = 5

  a, b, c = 3, 0, 0

  try:
    State = Select(chrome.find_element_by_id("statePoll"))
    for i in range(a, len(State.options)-1):
      State.select_by_index(i+1)

      WebDriverWait(chrome, wait_time).until(EC.presence_of_element_located((By.ID, 'lgaPoll')))
      sleep(2)
      LGA = Select(chrome.find_element_by_id("lgaPoll"))
      for j in range(b, len(LGA.options)-1):
        LGA.select_by_index(j+1)

        WebDriverWait(chrome, wait_time).until(EC.presence_of_element_located((By.ID, 'wardPoll')))
        sleep(2)
        Ward = Select(chrome.find_element_by_id("wardPoll"))
        for k in range(c, len(Ward.options)-1):
          Ward.select_by_index(k+1)

          WebDriverWait(chrome, wait_time).until(EC.presence_of_element_located((By.XPATH, '//*[@id="SearchPoll"]')))
          sleep(1)
          state, lga, ward = State.first_selected_option.text, LGA.first_selected_option.text, Ward.first_selected_option.text
          print(state, lga, ward)
          try:
            chrome.find_element_by_xpath('//*[@id="SearchPoll"]').click()
          except Exception as e:
            print(e)
            continue


          WebDriverWait(chrome, wait_time).until(EC.presence_of_element_located((By.XPATH, '//*[@id="result"]/tbody')))
          sleep(1)
          table = chrome.find_element_by_xpath('//*[@id="result"]').get_attribute('outerHTML')
          df = pd.read_html(table)
          df = df[0]
          df.insert(0, 'State', state)
          df.insert(1, 'LGA', lga)
          df.insert(2, 'Ward', ward)
          DF = DF.append(df)
  except:
    pass
DF.to_excel('polling-units.xlsx', index=False)
