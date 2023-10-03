
import datetime
from scrapfly import ScrapeConfig, ScrapflyClient, ScrapeApiResponse
import pandas as pd

price_selector='div[class="layout-row pdp-price"]>div.price-card>div>div>span>span>span.money-value>span.sr-only'
title_selector='h1[data-talos="labelPdpProductTitle"]'
size_selector='a.size-selector-button.available'
image_selector='div[class="carousel-container large-pdp-image"]>div>img'

scrapfly = ScrapflyClient(key='scp-live-7a4d5b5f2beb4fa68321410101c7f9d6')

base_url="https://www.mlbshop.com/"
result=scrapfly.scrape(ScrapeConfig(url=base_url))


hrefs=[result.soup.select('li.entity-item>a')[i].attrs['href'] for i in range(0,len(result.soup.select('li.entity-item>a')))]


team_products=[]
for i in hrefs:
    team_products.append(scrapfly.scrape(ScrapeConfig(url=base_url+i)))

team_products=[team_products[i].soup.select('div.product-image-container>a')[j].attrs['href'] for i in range(0,len(team_products)) for j in range(0,len(team_products[i].soup.select('div.product-image-container>a'))) ]


item_card=[]

for i in team_products:
    item_card.append(scrapfly.scrape(ScrapeConfig(url=base_url+i)))


titles=[item_card[i].soup.select(title_selector)[0].text for i in range(0,len(item_card))]
prices=[item_card[i].soup.select(price_selector)[0].text for i in range(0,len(item_card))]
images=[item_card[i].soup.select(image_selector)[0].attrs['src'] for i in range(0,len(item_card))]
sizes=[[element.get_text() for element in item_card[i].soup.select(size_selector)] for i in range(len(item_card))]

data = {
    'Title': titles,
    'Price': prices,
    'images': images,
    'sizes': sizes
}

# Create a DataFrame
df = pd.DataFrame(data)

filename='mlb'+str(datetime.datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")+'.csv')

df.to_csv(filename, index=False)