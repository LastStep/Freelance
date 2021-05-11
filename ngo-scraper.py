from selenium import webdriver
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from time import sleep
import itertools
from collections import defaultdict
from os.path import isfile


def xpath_soup(element):
  components = []
  child = element if element.name else element.parent
  for parent in child.parents:
    previous = itertools.islice(parent.children, 0, parent.contents.index(child))
    xpath_tag = child.name
    xpath_index = sum(1 for i in previous if i.name == xpath_tag) + 1
    components.append(xpath_tag if xpath_index == 1 else '%s[%d]' % (xpath_tag, xpath_index))
    child = parent
  components.reverse()
  return '/%s' % '/'.join(components)

def get_data():
  soup = bs(chrome.page_source, 'lxml')
  table = soup.find('div', {'class':'modal-dialog modal-lg'})
  table = table.find('div', {'class':'row'})
  headings = list(table.find_all('h3'))
  table = list(table.find_all('table'))

  NGO['NGO Name'].append(headings[0].text)
  print(headings[0].text)
  for i,t in enumerate(table):
    t = t.find('tbody')
    temp = []
    for tr in t.find_all('tr'):
      tmp = []
      for td in tr.find_all('td'):
        tmp.append(td.text)
      if len(tmp) == 0:
        continue
      temp.append(tmp)
    if i in [0, 5]:
      if i == 0:
        NGO['NGO ID'].append(temp[0][-1])
      else:
        try:
          NGO['Achievment'].append(temp[0][-1])
        except:
          NGO['Achievment'].append('-')
      continue

    elif i in [1, 3, 4]:
      for k,j in enumerate(temp):
        if i == 1:
          try:
            registeration[j[0]].append(j[-1])
          except:
            registeration[j[0]].append('-')
        elif i == 3:
          try:
            keyissues[j[0]].append(j[1])
          except:
            keyissues[j[0]].append('-')
        else:
          if len(j) == 2 and type(j) == list:
            fcra['FCRA Available'].append(j[0])
            fcra['FCRA Registration no.'].append(j[1])
          else:
            fcra['FCRA Available'].append('-')
            fcra['FCRA Registration no.'].append('-')
      continue

    elif i in [2, 6, 7]:
      for j in temp:
        if i == 2:
          if len(j) == 4 and type(j) == list:
            members['Name'].append(j[0])
            members['Designation'].append(j[1])
            members['Pan'].append(j[2])
            members['Aadhaar'].append(j[3])
          else:
            members['Name'].append('-')
            members['Designation'].append('-')
            members['Pan'].append('-')
            members['Aadhaar'].append('-')
        elif i == 6:
          if len(j) == 5 and type(j) == list:
            source_of_fund['Department Name'].append(j[0])
            source_of_fund['Source'].append(j[1])
            source_of_fund['Finacial Year'].append(j[2])
            source_of_fund['Amount Sanctioned'].append(j[3])
            source_of_fund['Purpose'].append(j[4])
          else:
            source_of_fund['Department Name'].append('-')
            source_of_fund['Source'].append('-')
            source_of_fund['Finacial Year'].append('-')
            source_of_fund['Amount Sanctioned'].append('-')
            source_of_fund['Purpose'].append('-')
        else:
          try:
            contact[j[0]].append(j[1])
          except:
            contact[j[0]].append('-')
      continue

def get_df():
  dff1 =  [pd.DataFrame.from_dict(NGO),
        pd.DataFrame.from_dict(registeration),
        pd.DataFrame.from_dict(keyissues),
        pd.DataFrame.from_dict(fcra),
        pd.DataFrame.from_dict(contact)]
  dff2 = [pd.DataFrame.from_dict(NGO),
          pd.DataFrame.from_dict(members)]
  dff3 = [pd.DataFrame.from_dict(NGO),
          pd.DataFrame.from_dict(source_of_fund)]

  for i,df in enumerate(dff1):
    if i != 0:
      dff1[0] = pd.concat([dff1[0],df], axis = 1)
  tmp = [dff2[0] for _ in range(len(dff2[1]))]
  dff2[0] = pd.concat(tmp, ignore_index = True)
  tmp = [dff3[0] for _ in range(len(dff3[1]))]
  dff3[0] = pd.concat(tmp, ignore_index = True)

  dff2[0] = pd.concat([dff2[0], dff2[1]], axis = 1)
  dff3[0] = pd.concat([dff3[0], dff3[1]], axis = 1)

  return dff1[0], dff2[0], dff3[0]

def make_csv(output_name = ['NGO', 'Members', 'Source of Fund']):
  print('---------')
  df = [dataframes1[0], dataframes2[0], dataframes3[0]]
  for i,dataframes in enumerate([dataframes1, dataframes2, dataframes3]):
    for DF in dataframes[1:]:
      df[i] = pd.concat([df[i], DF], ignore_index = True)
    if i != 0:
      df[i] = df[i].drop(columns = ['Achievment'])
    if isfile('{}.csv'.format(output_name[i])):
      df[i].to_csv('{}.csv'.format(output_name[i]), mode = 'a', index = False, header = False)
    else:
      df[i].to_csv('{}.csv'.format(output_name[i]), index = False)
    print('Made File {}.csv'.format(output_name[i]))

if __name__ == '__main__':

  url = 'https://ngodarpan.gov.in/index.php/search/'
  pages = 1
  pages_scraped = 0
  dataframes1, dataframes2, dataframes3 = [], [], []

  print('Searching...')

  ops = webdriver.ChromeOptions()
  ops.headless = False
  with webdriver.Chrome(options = ops) as chrome:
    actions = ActionChains(chrome)

    chrome.get(url)
    sleep(1)
    chrome.find_element_by_css_selector('input[class="btn btn-primary pull-left"]').click()
    sleep(2)
    soup = bs(chrome.page_source, 'lxml')
    table = soup.find('table', {'class':'table table-bordered table-striped'})
    table = table.find('tbody')

    for page in range(pages + pages_scraped):
      check = True
      for tr in table.find_all('tr'):
        if page < pages_scraped:
          break

        NGO, registeration, members, keyissues, fcra, source_of_fund, contact = \
          defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(
            list), defaultdict(list)
        try:
          ngo = tr.find('a')
          chrome.find_element_by_xpath(xpath_soup(ngo)).click()
          sleep(6)
          get_data()
          a, b, c = get_df()
          dataframes1.append(a)
          dataframes2.append(b)
          dataframes3.append(c)
        except Exception as e:
          print('---------')
          print(e)
          check = False
          break
        actions.send_keys(Keys.ESCAPE)
        actions.perform()
        sleep(2)

      if not check:
        break
      try:
        soup = bs(chrome.page_source, 'lxml')
        soup = soup.find('ul', {'class':'pagination'})
        soup = soup.find_all('li')[-1]
        path = xpath_soup(soup.find('a'))
        chrome.find_element_by_xpath(path).click()
        sleep(5)
      except:
        break

    make_csv()

