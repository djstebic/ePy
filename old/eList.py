'''
Created on May 19, 2017

@author: Blu3spirits & JuggernautAlpha
@version: 1.2
'''
import requests
from bs4 import BeautifulSoup

def getFile(filename):
    userList = []
    with open(filename, 'r+') as f:
        [userList.append(x) for x in f]
    return userList

def getPage(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, "html.parser")
    return soup

def getTitle(soup):
    titleGen = (e.get_text() for e in soup.select('h1'))
    test = [x[16:] for x in titleGen]
    return test[0]
    
def getBid(soup):
    priceGen = (e.get_text() for e in soup.find_all(attrs={'id':'prcIsum'}))
    test = [x for x in priceGen]
    if test == []:
        priceGen = (e.get_text() for e in soup.find_all(attrs={'id':'prcIsum_bidPrice'}))
        test = [x for x in priceGen]
    return test[0]