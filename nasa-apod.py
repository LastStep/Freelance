import requests, argparse, re
from bs4 import BeautifulSoup as bs
from datetime import timedelta, date



parser = argparse.ArgumentParser()
parser.add_argument('--d', help='gets the data for a specific date in format yy/mm/dd')
parser.add_argument('--r', nargs=2, help='gets the data in a range of dates in format yy/mm/dd yy/mm/dd')
parser.add_argument('--limit', type=int, help='maximum number of dates to get in a date range, default is 10')
parser.add_argument('--t', action='store_true', help='gets the data for today')
parser.add_argument('--img', action='store_true', help='to download the image(s)')
parser.add_argument('--info', action='store_true', help='to get the info')
parser.add_argument('--path', help='specify a path to save the image(s) in. it should not end with a slash')

args = parser.parse_args()


def get_apod(req, nasa_site):
    global nasa_apod
    print('\nConnecting to {} ...\n'.format(nasa_site))
    site = req.get(nasa_site)
    site = bs(site.text, 'lxml')

    inf = site.find_all('center')

    try:
        title = inf[1].find('b').text.strip()
    except:
        title = False
        
    try:
        image_link = nasa_apod + inf[0].find('img')['src']
        if args.img:
            regex = re.compile('[^a-zA-Z ]')
            output_name = regex.sub('', title) if title else 'unknown'
            print('Downloading {}.jpg\n'.format(output_name))
            path = args.path if args.path else '.'
            img_data = req.get(image_link).content
            with open('{}\\{}.jpg'.format(path, output_name), 'wb') as handle:
                handle.write(img_data)
    except Exception as e:
        print(e)
        print('Image Not Found \n')
    
    try:
        credit = [i.text.strip() for i in inf[1].find_all('a')]
        credit = [' '.join(i.split()) for i in credit]
        credit = ', '.join(credit)
    except:
        credit = False

    try:
        explanation = [i.text.strip() for i in site.find_all('p')]
        explanation = [i for i in explanation if i.startswith('Explanation')][0]
        explanation = ''.join([i if i != '\n' else '' for i in explanation])
    except:
        explanation = False
    
    if args.info:
        if title:
            print('Title: ' + title)
            print('\n')
        else:
            print('Title Not Found \n')
        if credit:
            print('Image Credits: ' + credit)
            print('\n')
        else:
            print('Image Credit Not Found \n')
        if explanation:
            print(explanation)
            print('\n')
        else:
            print('Explanation Not Found \n')


def daterange(start_date, end_date):
    for _, n in zip(range(args.limit if args.limit else 10), range(int ((end_date - start_date).days))):
        yield start_date + timedelta(n)

def get_date_link(date):
    apod_id = date.split('/')
    apod_id = ''.join(apod_id)
    return nasa_apod + 'ap' + apod_id + '.html'


if __name__ == '__main__':
    nasa_apod = 'https://apod.nasa.gov/apod/'

    with requests.Session() as req:
        
        if args.d:
            if len(args.d) != 8:
                print('\nIncorrect date format')
                exit()
            get_apod(req, get_date_link(args.d))
        
        elif args.t:
            get_apod(req, nasa_apod)
        
        elif args.r:
            start_date, end_date = [int(i) for i in args.r[0].split('/')], [int(i) for i in args.r[1].split('/')]
            start_date[0], end_date[0] = int('20{}'.format(start_date[0])), int('20{}'.format(end_date[0]))
            start_date, end_date = date(*start_date), date(*end_date)

            for single_date in daterange(start_date, end_date):
                date = single_date.strftime("%y/%m/%d")
                get_apod(req, get_date_link(date))



    
         