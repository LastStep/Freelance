from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup as bs
from collections import defaultdict
from json import dump
from re import compile

def check_comments():
  link = chrome.current_url
  link_id = link[link.find('=') + 1:link.find('&')]
  try:
    chrome.find_element_by_xpath('//*[@id="m_story_permalink_view"]')
    return link_id
  except:
    chrome.execute_script("window.history.go(-1)")
    return False

def get_comments(link_id):
  comms = []
  try:
    site = bs(chrome.page_source, 'lxml')
    comments = site.find('div', {'id':'ufi_{}'.format(link_id)})
    comments = comments.find_all('div', {'class':compile('\w{2}$'), 'id':compile('\d{16}$')})
    for comment in comments:
      try:
        int(comment['id'])
      except:
        continue
      try:
        comment = comment.find('div')
        comment = comment.find('div')
        comment = comment.text.strip()
        if comment:
          comms.append(comment)
      except:
        pass
    return comms
  except:
    return comms

if __name__ == '__main__':

  email = input('Email : ')
  password = input('Password : ')
  company_url = input('Page URL in the form https://mbasic.facebook.com/pagename : ')
  # company_url = 'https://mbasic.facebook.com/epicgamesinc'
  number_of_pages = int(input('Number of Pages to scrape (5 Posts per Page) : '))
  output = input('Output File Name : ')
  posts = []
  
  base_url = 'https://mbasic.facebook.com'

  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  with webdriver.Chrome(options = options) as chrome:

    print('Logging in ...')
    chrome.get(base_url)
    chrome.find_element_by_id('m_login_email').send_keys(email + Keys.TAB + password + Keys.ENTER)

    chrome.get(company_url)
    for k in range(number_of_pages):
      sleep(1)
      print('Scraping Page {}'.format(k + 1))
      post_text, post_time, post_link, post_media = [], [], [], []
      posts_url = chrome.current_url
      for i in range(1, 6):
        try:
          Text = chrome.find_element_by_xpath('//*[@id="u_0_{}"]/div[1]/div[2]'.format(i))
          post_text.append(Text.text.strip())
        except:
          post_text.append(None)
        try:
          Time = chrome.find_element_by_xpath('//*[@id="u_0_{}"]/div[2]/div[1]/abbr'.format(i))
          post_time.append(Time.text.strip())
        except:
          post_time.append(None)
        try:
          Link = chrome.find_element_by_xpath('//*[@id="u_0_{}"]/div[2]/div[2]/a[1]'.format(i))
          post_link.append(Link.get_attribute('href'))
        except:
          post_link.append(None)
        try:
          Media = chrome.find_element_by_xpath('//*[@id="u_0_{}"]/div[1]/div[3]/div[1]/a/img'.format(i))
          post_media.append(Media.get_attribute('src'))
        except:
          try:
            Media = chrome.find_element_by_xpath('//*[@id="u_0_{}"]/div[1]/div[3]/div[1]/div/a'.format(i))
            post_media.append(Media.get_attribute('href'))
          except:
            post_media.append(None)

      for Link, Text, Time, Media in zip(post_link, post_text, post_time, post_media):
        post = defaultdict()
        back_times, post_comms, link_id = 1, [], True
        if Link:
          chrome.get(Link)
          while link_id:
            sleep(1)
            link_id = check_comments()
            if not link_id:
              continue
            post_comms.extend(get_comments(link_id))
            try:
              chrome.find_element_by_xpath('//*[@id="see_next_{}"]/a'.format(link_id)).click()
              back_times += 1
            except:
              break
          if not link_id:
            continue
        else:
          continue

        post['Post'] = Text
        post['Time'] = Time
        post['Comments'] = post_comms
        post['Comments Link'] = Link
        post['Media'] = Media
        posts.append(post)

      chrome.get(posts_url)
      chrome.find_element_by_xpath('//*[@id="structured_composer_async_container"]/div[2]/a').click()

    if '.json' not in output:
      output += '.json'
    with open('Scraped Data\{}'.format(output), '+w') as f:
      dump(posts, f, indent = 4)
    print('File Made {}'.format(output))

	

