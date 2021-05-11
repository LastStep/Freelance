from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time, sys
from bs4 import BeautifulSoup as bs
import yagmail

def send_email(email_id, tickets_info):
	tickets_info = '\n\n'.join(tickets_info)
	yag = yagmail.SMTP("shek70205@gmail.com")
	yag.send(email_id, 'subject', tickets_info)

def get_categories(page_source):
  soup = bs(page_source, 'lxml')
  category_dict = {}
  all_categories = soup.find('div', class_='css-1w580q7 e1np9i3j0').find_all('a')
  for each_category in all_categories:
    category_name = each_category.find('h4', class_='css-ctuejo eyttag80').text
    category_link = 'https://www.ticketswap.nl' + each_category['href']
    category_dict[category_name] = category_link
  return category_dict

def choose_category(all_categories, category_name):
  for index, key in enumerate(all_categories.keys()):
    print(index, '-', key)
  for key in all_categories.keys():
    if category_name.lower() in key.lower():
      return all_categories[key] 
  category_choice = input("Choose category for the tickets: ")
  for index, item in enumerate(all_categories.keys()):
    if int(category_choice) == index:
      return all_categories[item]

def check_for_available_tickets(driver):
  tickets_found = False
  while not tickets_found:
    no_of_tickets_available = driver.find_elements_by_css_selector('h2.css-1wu73kq.e149jiyc1')[0].text
    if int(no_of_tickets_available) > 0:
      print(no_of_tickets_available, "ticket(s) found for the selected category.")
      tickets_found = True
    else:
      print("No tickets available currently. Refreshing the page in 60 seconds.")
      time.sleep(60)
      driver.refresh()
      time.sleep(5)
      WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.css-1wu73kq.e149jiyc1')))
  return

def get_ticket_links(page_source, minimum_tickets):
  soup = bs(page_source, 'lxml')
  all_ticket_links = []
  available_tickets = soup.find('div', class_='css-uirvwh e1lsc6vo3').find_all('div', class_='css-jub5o6 e15p5mol0')
  for ticket in available_tickets:
    ticket_name = ticket.find('header').text.strip()
    ticket_number = int(ticket_name[: ticket_name.find('×')].strip())
    if ticket_number >= minimum_tickets:
      ticket_link = 'https://www.ticketswap.nl' + ticket.find('a', href=True)['href']
      ticket_price = ticket.find('div', {'class':'css-riobvl e15p5mol8'}).text.strip()
      all_ticket_links.append('{} - {} - {}'.format(ticket_name, ticket_price, ticket_link))
  return all_ticket_links

def run_scraper(event_name, event_location, category_name, minimum_tickets, email_id):
  query_term = event_name + ' ' + event_location
  query_url = 'https://www.ticketswap.nl/search?query={}'.format(query_term)

  options = Options()
  options.add_argument('--no-sandbox')
#   options.add_argument('headless')
  options.add_argument('--disable-dev-shm-usage')
  options.add_argument('log-level=3') 
  options.add_argument("--start-maximized")
  options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
  with webdriver.Chrome(options=options) as driver:
    driver.get(query_url)
    try:
      WebDriverWait(driver, 45).until(EC.presence_of_element_located((By.CLASS_NAME, 'auto-complete-result')))
    except TimeoutException:
      print("No event available for the entered event name and event location. Please check the input info again. Program is exiting.")
      sys.exit()

    # Get the link of the result.
    query_results = driver.find_elements_by_class_name('auto-complete-result')
    print(len(query_results), 'result(s) found.')
    event_link = query_results[0].get_attribute('href')
    print(event_link)
    driver.get(event_link)
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.css-1wu73kq.e149jiyc1')))

    try:
      all_categories = get_categories(driver.page_source)
    except:
      # Check for no of available tickets currently. If '0', we can't see any categories.
      # Keep refreshing until it's more than '0'.
      while True:
        no_of_tickets = driver.find_elements_by_css_selector('h2.css-1wu73kq.e149jiyc1')[0].text
        if int(no_of_tickets) > 0:
          print("Tickets available for the event.")
          break
        else:
          print("No tickets available currently. Refreshing the page in 60 seconds.")
          time.sleep(60)
          driver.refresh()
          time.sleep(5)
          WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h2.css-1wu73kq.e149jiyc1')))
      all_categories = get_categories(driver.page_source)

    # all_categories = get_categories(driver.page_source)
    category_link = choose_category(all_categories, category_name)
    # print(category_link)
    driver.get(category_link)
    time.sleep(10)

    check_for_available_tickets(driver)

    ticket_links = get_ticket_links(driver.page_source, minimum_tickets)
    for each_link in ticket_links:
      print(each_link)
    send_email(email_id, ticket_links)
    


if __name__ == '__main__':
  event_name = input("Enter the Event Name: ")
  event_location = input("Enter the Event Location: ")
  category_name = input("Enter the Category: ")
  minimum_tickets = int(input("Enter the Minimum Number of Tickets: "))
  email_id = input("Enter the Email ID: ")
  run_scraper(event_name, event_location, category_name, minimum_tickets, email_id)