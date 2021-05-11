from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from time import sleep
from collections import defaultdict

siteUrl = 'https://protoalgonquian.atlas-ling.ca/#!/browse#browse'

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
  chrome.get(siteUrl)

  sleep(30)
