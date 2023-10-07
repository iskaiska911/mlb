
import datetime
from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse
import pandas as pd
import re
import math

price_selector = 'div[class="layout-row pdp-price"]>div.price-card>div>div>span>span>span.money-value>span.sr-only'
title_selector = 'h1[data-talos="labelPdpProductTitle"]'
size_selector = 'a.size-selector-button.available'
image_selector = 'div[class="carousel-container large-pdp-image"]>div>img'
filter_selector= 'a.side-nav-facet-item.hide-radio-button'
amount_selector='[data-talos="itemCount"]'



scrapfly = ScrapflyClient(key='scp-live-7a4d5b5f2beb4fa68321410101c7f9d6')

base_url = "https://www.mlbshop.com/"
result = scrapfly.scrape(ScrapeConfig(url=base_url))


hrefs = [result.soup.select('li.entity-item>a')[i].attrs['href'] for i in range(0,len(result.soup.select('li.entity-item>a')))]


team_products = []


for i in hrefs[0:2]:
    team_products.append(scrapfly.scrape(ScrapeConfig(url=base_url+i)))


filters=[team_products[i].soup.select(filter_selector)[j].attrs['href'] for i in range(len(team_products)) for j in range(len(team_products[i].soup.select(filter_selector)))]

team_products=[]
pattern = r'\d+'
for j in filters:
    try:
        amount=scrapfly.scrape(ScrapeConfig(url=base_url + j)).soup.select(amount_selector)[0].text
        amount=int(re.findall(pattern, amount)[-1])
        pages=math.ceil(amount/72)
    except:
        continue
    for page in range(1,pages):
        team_products.append(scrapfly.scrape(ScrapeConfig(url=base_url + j+"?pageSize=72&pageNumber={}&sortOption=TopSellers".format(page))))






team_products=[team_products[i].soup.select('div.product-image-container>a')[j].attrs['href'] for i in range(0,len(team_products)) for j in range(0,len(team_products[i].soup.select('div.product-image-container>a'))) ]



item_card=[]

logname='mlb_log'+str(datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.txt')

for i in team_products:
    try:
        item_card.append(scrapfly.scrape(ScrapeConfig(url=base_url+i)))
    except Exception as e:
        with open(logname, "w") as log:
            log.write(str(e))
        continue


messy='mlb_messy'+str(datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.txt')
with open(messy, 'w',encoding='utf-8') as f:
    f.write('\n'.join(team_products))

df_list=[]
for i in range(0,len(item_card)):
    row_list=[]
    try:
        row_list.append(item_card[i].soup.select(title_selector)[0].text)
    except:
        row_list.append('Fail')
        continue
    try:
        row_list.append(item_card[i].soup.select(price_selector)[0].text)
    except:
        row_list.append('Fail')
        continue
    try:
        row_list.append(item_card[i].soup.select(image_selector)[0].attrs['src'])
    except:
        row_list.append('Fail')
        continue
    try:
        row_list.append([j.text for j in item_card[i].soup.select(size_selector)])
    except:
        row_list.append('Fail')
        continue
    df_list.append(row_list)



# Create a DataFrame
df = pd.DataFrame(df_list,columns=['title', 'price', 'image','sizes'])

filename='mlb'+str(datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.csv')

df.to_csv(filename, index=False)