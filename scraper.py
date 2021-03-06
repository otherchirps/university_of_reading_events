from lxml import html
import requests
import scraperwiki
import time
import string
from dateutil.parser import parse

def do_the_scraping():
    page = requests.get('http://www.reading.ac.uk/news-and-events/about-eventlist.aspx')
    tree = html.fromstring(page.text)
    links = tree.xpath('//a[contains(@href,"/about/newsandevents/Events/")]/@href')
    for link in links:
        url = 'http://www.reading.ac.uk' + link
        try:
            scrape_event(url)
        except:
            "Error scraping event: " + url
        time.sleep(0.5)
        
def flatten(nodes, join_char="\n"):
    return join_char.join(
        [
            node.strip() 
            for node in nodes
            if node and node.strip != ""
        ]
    )

def scrape_event(url):
    page = requests.get(url)
    tree = html.fromstring(page.text)
    title = tree.xpath('//h1[@class="page-header"]/text()')[0]
    description = flatten(tree.xpath('//p[@class="event-summary"]/text()'))
    raw_date = tree.xpath('//p[@class="event-date"]/text()')[0]
    event_number = url.rsplit('/',1)[1]
    id = int(filter(str.isdigit, event_number))
    try:
        date = parse(raw_date)
        date = date.strftime('%Y-%m-%d')
    except:
        date = raw_date
    event_time = tree.xpath('//p[@class="event-time"]/text()')[0]
    location = tree.xpath('//p[@class="event-location"]/text()')[0]
    try:
        venue = location.split(',')[0]
    except:
        venue = location
    contact = flatten(tree.xpath('//p[@class="event-contact"]/text()'))
    
    data = {
        'id': 'uor' + str(id),
        'title': title,
        'description': description,
        'date': date,
        'time': event_time,
        'location': location,
        'venue': venue,
        'source': url,
        'contact': contact,        
    }
    
    print data
    scraperwiki.sqlite.save(unique_keys = ['id'], data = data)
        
if scraperwiki.sql.show_tables():
    scraperwiki.sqlite.execute("DELETE FROM data") #use 'swdata' on Mac, use 'data' on morph.io
    
do_the_scraping()
