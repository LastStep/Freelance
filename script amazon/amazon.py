import requests
from bs4 import BeautifulSoup as bs
from collections import defaultdict
import pandas as pd

def load_page(url):
  headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
  }
  return bs(req.get(url, headers=headers).content, 'lxml')

def get_search_results(search, page_limit = 10):
  page_number, search_results = 1, []
  while page_number <= page_limit:
    print('Page : {}'.format(page_number))
    try:
      if page_number == 1:
        url = 'https://www.amazon.es/s?k={}&i=stripbooks'.format(search)
      else:
        url = results.find('li', {'class':'a-last'})
        url = 'https://www.amazon.es' + url.find('a')['href']
      results = load_page(url)
      resultss = results.find('div', {'class':'s-result-list s-search-results sg-row'})
      for link in resultss.find_all('a', {'class':'a-link-normal a-text-normal'}):
        link = link['href']
        search_results.append('https://www.amazon.es'+link)
    except Exception as e:
      print(e)
      return search_results
    page_number += 1
  return search_results

def get_data(urls):
  data = defaultdict(list)
  for row, url in enumerate(urls, 1):
    print(row, url)
    page = load_page(url)

    #Product Name
    try:
      data[row].append(page.find('span', {'id':'productTitle'}).text)
    except:
      try:
        data[row].append(page.find('span', {'id':'ebooksProductTitle'}).text)
      except:
        data[row].append('-')

    #Product Price
    try:
      data[row].append(page.find('span', {'class':'a-size-medium a-color-price offer-price a-text-normal'}).text)
    except:
      try:
        data[row].append(page.find('td', {'class':'a-color-price a-size-medium a-align-bottom'}).text)
      except:
        try:
          data[row].append(page.find('span', {'class':'a-color-price'}).text)
        except:
          data[row].append('-')

    #Product Description
    try:
      data[row].append(page.find('div', {'id':'productDescription'}).text)
    except:
      try:
        data[row].append(page.find('div', {'class':'productDescriptionWrapper'}).text)
      except:
        data[row].append('-')

    #Product Url + Tag
    data[row].append(url+'&testdeoposi07-21')

    #Url of Product Image
    try:
      line = page.find('div', {'id':'img-canvas'})
    except:
      try:
        line = page.find('div', {'id':'ebooks-img-canvas'})
      except:
        line = page
    if line != page and line is not None:
      for img in line.contents:
        try:
          img = img['data-a-dynamic-image']
          end = img.find('.jpg')
          if end == -1:
            end = img.find('.gif')
          data[row].append(img[img.find('http'):end+4])
          break
        except:
          pass
    else:
      data[row].append('-')

  return data

def make_csv(data, output='output'):
  df = pd.DataFrame.from_dict(data, orient = 'index')

  if len(df) > 0:
    df.columns = ['Book Name', 'Price', 'Description', 'URL + Tag', 'Book Image URL']
    df['Book Image URL'] = df['Book Image URL'].apply(filter_img_url)
    df['Book Image URL'] = df['Book Image URL'].apply(lambda x: ''.join([i for i in x if i != ',']))
    df.to_csv('{}.csv'.format(output))
    print('Made file {}.csv'.format(output))

  else:
    print('No Data Found')

def filter_img_url(url):
  left = url.find('._')
  right = url.find('_.')
  if left == -1 or right == -1:
    return url
  else:
    return url[:left] + url[right + 1:]

def search_results_to_txt(search_results):
  with open('results.txt', '+w') as f:
    for result in search_results:
      f.write(result)
      f.write('\n')

def search_results_from_txt(filename='results'):
  search_results = []
  with open('{}.txt'.format(filename), 'r') as f:
    for line in f.readlines():
      search_results.append(line[:-1])
  return search_results

if __name__ == '__main__':

  search = 'oposiciones policia nacional'
  page_limit = 3

  with requests.Session() as req:

    search_results = get_search_results(search, page_limit)

    # search_results_to_txt(search_results)

    # search_results = search_results_from_txt()

    data = get_data(search_results)

    make_csv(data)
