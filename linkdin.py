from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
from itertools import product
from string import ascii_lowercase
import pandas as pd
from os.path import isfile

def load_page(url):
  chrome.get(url)
  return BeautifulSoup(chrome.page_source, 'lxml')

def login(username, password):
  url = 'https://www.linkedin.com/uas/login?trk=guest_homepage-basic_nav-header-signin'
  print('Logging in...')
  chrome.get(url)
  chrome.find_element_by_css_selector("input[id='username']").send_keys(username)
  chrome.find_element_by_css_selector("input[id='password']").send_keys(password + Keys.ENTER)
  sleep(1)
  redirecting_url = 'https://www.freelancer.in/users/l.php?url=https:%2F%2Fwww.linkedin.com%2Fsales%2Fsearch%2Fcompany%3FcompanySize%3DI%252CH%252CG%252CF%252CE%252CD%252CC%26amp;doFetchHeroCard%3Dfalse%26amp;keywords%3Daaa%26amp;page%3D1%26amp;searchSessionId%3DM%252BVNKpKsTC68dFE4i%252BUhBw%253D%253D&sig=253e06ab776d36fe51f641c5041c10c91978de7638fadd5f0394b47445d37f16'
  print('Redirecting...')
  chrome.get(redirecting_url)
  chrome.find_element_by_css_selector("button[id='follow-button']").click()
  sleep(2)

def search(keyword):
  url = 'https://www.linkedin.com/sales/search/company?companySize=C%2CD%2CE%2CF%2CG%2CH%2CI&keywords={}&page=1'.format(keyword)
  result = load_page(url)
  result = result.find('span', {'class':'artdeco-tab-primary-text'})
  return ''.join([i for i in result.text if i.isdigit()])

def get_keyword_list(last_keyword):
  keyword_list = []
  for i, j, k in product(ascii_lowercase, repeat = 3):
    keyword = ''.join([i, j, k])
    keyword_list.append(keyword)
    if keyword == last_keyword:
      return keyword_list

def make_csv(data, output = 'output'):
  df = pd.DataFrame.from_dict(data, orient = 'index')

  if isfile('{}.csv'.format(output)):
    df.to_csv('{}.csv'.format(output), mode = 'a', header = False)
  else:
    df.to_csv('{}.csv'.format(output))
  print('Made File {}.csv'.format(output))

if __name__ == '__main__':
  username = 'robkay@protonmail.com'
  password = 'temppass123!'
  last_keyword = ''
  search_limit = 10
  file_name = 'output'

  if isfile('{}.csv'.format(file_name)):
    df = pd.read_csv('{}.csv'.format(file_name))
    last_keyword = df.iloc[-1, 0]
    last_keyword = last_keyword.strip()

  data = {}
  keyword_list = get_keyword_list(last_keyword) if len(last_keyword) == 3 else []

  with webdriver.Chrome() as chrome:

    login(username, password)

    for _,keyword in zip(range(search_limit + len(keyword_list)), product(ascii_lowercase, repeat = 3)):
      keyword = ''.join(keyword)
      if keyword in keyword_list:
        continue

      try:
        data[keyword] = search(keyword)
        print(keyword, data[keyword])
      except Exception as e:
        print(e)
        break

  make_csv(data, file_name)