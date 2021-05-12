from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup as bs
import pickle

from time import sleep
from os import mkdir
from os.path import isfile
from pathlib import Path
from collections import defaultdict

from constants import *

def initialise_driver(window_size='1920,1080'):
  options = webdriver.ChromeOptions()
  # options.add_argument(
      # '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
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


def login(driver, email, password):
  try:
    driver.find_element_by_xpath('//*[@id="email"]').send_keys(email + Keys.TAB + password + Keys.ENTER)
    sleep(3)
    save_cookies(driver)
    print('---Login Success---')
  except Exception as e:
    print('---Login Failed---')


def save_cookies(driver):
  pickle.dump(driver.get_cookies(), open(COOKIE_FILE, 'wb'))


def load_cookies(driver):
  cookies = pickle.load(open(COOKIE_FILE, 'rb'))
  for cookie in cookies:
    driver.add_cookie(cookie)
  return driver


def scroll(driver, file_name = '', num_of_scrolls = 10, take_ss = False):
  prev_height = 0
  for num_of_scroll in range(1, num_of_scrolls + 1):
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if prev_height != new_height:
      prev_height = new_height
      sleep(SCROLL_WAIT_TIME)
      if take_ss:
        screenshot(driver, f'{file_name}_{num_of_scroll}')
      driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    else:
      break


def screenshot(driver, file_name):
  driver.save_screenshot(f'{DIR}\{file_name}.png')
  print(f'Created {file_name}.png')


def get_data(driver, dir, username, urls, url_scroll = []):
  for url in urls:
    driver.get(url)
    try:
      sleep(1)
      wait.until(EC.visibility_of_element_located((By.XPATH, '//*[starts-with(@id,"mount")]')))
      file_name = f'{dir}\{username}_{url[url.rfind("/")+1:]}'
      if url in url_scroll:
        scroll(driver, file_name, num_of_scrolls=5, take_ss=True)
      else:
        screenshot(driver, file_name)
    except Exception as e:
      print('---FAILED---')


def get_username(page):
  username = page.find('title').text.strip()
  if 'Facebook' in username:
    left, right = username.find(')'), username.find('|')
    username = username[left+1:right].strip()
  return username


def get_following(driver, url, limit = 36):
  driver.get(url)
  scroll(driver, num_of_scrolls=5)
  page = bs(driver.page_source, 'lxml')

  followings = page.find('div', {'data-pagelet':'ProfileAppSection_0'})
  followings = [following['href'].strip('/') for following in followings.find_all('a', {'aria-hidden':'true', 'role':'link'})] if followings else []
  return followings if len(followings) <= limit else followings[:limit]


def get_following_data(driver, link, username_main):
  driver.get(link)
  username = get_username(bs(driver.page_source, 'lxml'))
  Path(f'{DIR}\{username_main}\{username}').mkdir(parents=True, exist_ok=True)
  print('------------')
  print(username)
  print(link)

  file_name = f'{username_main}\{username}\{username}'
  scroll(driver, file_name, num_of_scrolls=5, take_ss=True)

  urls = [f'{link}/{i}' for i in ['about', 'community']]
  dir = f'{username_main}\{username}'
  get_data(driver, dir, username, urls)


def main(driver, link):
  driver.get(link)
  username = get_username(bs(driver.page_source, 'lxml'))
  Path(f'{DIR}\{username}').mkdir(parents=True, exist_ok=True)
  print(username)
  print(link)

  file_name = f'{username}\{username}'
  scroll(driver, file_name, num_of_scrolls=5, take_ss=True)

  url_profile = link
  url_about = [f'{link}/about_{i}' for i in ['overview', 'work_and_education', 'places', 'contact_and_basic_info', 'family_and_relationships', 'details', 'life_events']]
  url_more = [f'{link}/{i}' for i in ['sports', 'music', 'movies', 'tv', 'books', 'games', 'events']]
  url_scroll = [f'{link}/{i}' for i in ['likes', 'friends']]

  urls = url_about + url_more + url_scroll
  dir = username
  get_data(driver, dir, username, urls, url_scroll)

  try:
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'svg.pzggbiyp[aria-label="{username}"]')))
    driver.find_element_by_css_selector(f'svg.pzggbiyp[aria-label="{username}"]').click()
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'img[data-visualcompletion="media-vc-image"]')))
    file_name = f'{username}\{username}_profile_pic.png'
    driver.save_screenshot(f'{DIR}\{file_name}')
    print(f'Created {file_name}')
  except:
    print('---FAILED---')
  return username


if __name__ == '__main__':

  with initialise_driver(WINDOW_SIZE) as driver:
    wait = WebDriverWait(driver, 30)

    print('---Logging In---')
    driver.get(BASE_URL)
    if isfile(COOKIE_FILE):
      driver = load_cookies(driver)
      print('---Login Success---')
    else:
      login(driver, EMAIL, PASSWORD)
    sleep(2)

    try:
      driver.find_element_by_xpath("//button[text()='Accept All']").click()
    except:
      pass

    for url in profiles:
      print('---Getting Main Profile---')
      username_main = main(driver, url)

      print('---Getting Followings---')
      followings = get_following(driver, f'{url}/following')
      for following in followings:
        get_following_data(driver, following, username_main)
