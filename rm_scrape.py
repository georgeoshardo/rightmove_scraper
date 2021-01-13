import requests
from bs4 import BeautifulSoup
import pprint
pp = pprint.PrettyPrinter(indent=4)
from selenium import webdriver
options = webdriver.ChromeOptions();
options.add_argument('--headless');
browser = webdriver.Chrome(options=options)
import pandas as pd
import re
from joblib import Parallel, delayed

def get_house_URLs(search_URL):
    """
    Returns list of house URLs from a search URL
    """
    URL = search_URL
    pages = 20
    house_URLs = []
    for x in range(pages):
        page = URL + "&index=" + str(int(x * 24))
        page = requests.get(page)
        soup = BeautifulSoup(page.content, 'html.parser')
        house_search_results = soup.findAll(class_="propertyCard-link")
        for house_URL in house_search_results:
            house_URLs.append(house_URL["href"])
    house_URLs = list(set(house_URLs))
    house_URLs = [x for x in house_URLs if len(x)>2]
    house_URLs = ["https://www.rightmove.co.uk" + url for url in house_URLs]
    return house_URLs

def get_house_page(house_URL):
    """
    Returns house object from house_URL
    """

    browser.get(house_URL)
    html = browser.page_source
    house = BeautifulSoup(html, 'lxml')
    return house


class House:
    

    
    def __init__(self, URL):
        self.URL = URL
        self.page = get_house_page(self.URL)
        
    def house_page(self,URL):

        """
        Returns house object from house_URL
        """
        browser.get(URL)
        html = browser.page_source
        house = BeautifulSoup(html, 'lxml')
        return house
    
    def streetAddress(self):
        try:
            streetAddress = list(self.page.findAll("h1", itemprop="streetAddress")[0])[0]
            return streetAddress
        except:
            return "NA"

    def propertyType(self):
        try:
            return list(list(self.page.find(text='PROPERTY TYPE').parent.parent())[-1])[0]
        except:
            return "NA"

    def bedrooms(self):
        try:
            return int(list(list(self.page.find(text='BEDROOMS').parent.parent())[-1])[0][-1])
        except:
            return "NA"

    def bathrooms(self):
        try:
            return int(list(list(self.page.find(text='BATHROOMS').parent.parent())[-1])[0][-1])
        except:
            return "NA"
        
    def sqft(self):
        try:
            sqft = list(list(self.page.find(text='SIZE').parent.parent())[-2])[0]
            sqft = [int(s) for s in sqft.split() if s.isdigit()][0]
            return sqft
        except:
            return "NA"
    def guidePrice(self):
        try:
            guidePrice = self.page.find(text='Guide Price').parent.parent()[1]
            guidePrice = guidePrice.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
            return guidePrice
        except:
            guidePrice = self.page.find(text='Offers in Region of').parent.parent()[1]
            guidePrice = guidePrice.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
            return guidePrice
        finally:
            guidePrice = self.page.find(text=re.compile("£"))
            guidePrice = [int(s) for s in guidePrice.split()[0] if s.isdigit()]
            guidePrice = int("".join(map(str, guidePrice)))
            return guidePrice
        
    def info(self):
        infodict = {
            "URL": self.URL,
            "Street Address": self.streetAddress(),
            "Property Type": self.propertyType(),
            "Bedrooms": self.bedrooms(),
            "Bathrooms": self.bathrooms(),
            "Size (sq ft)": self.sqft(),
            "Guide Price": self.guidePrice()
        }
        return infodict
    
def search_to_df(search_URL):
    URLs = get_house_URLs(search_URL)
    df = pd.DataFrame()
    for URL in URLs:
        house = House(URL)
        df = df.append(pd.DataFrame.from_dict(house.info(),orient='index').T)
    df.reset_index(drop=True, inplace=True)
    return df