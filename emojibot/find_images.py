# Thanks http://stackoverflow.com/questions/20716842/python-download-images-from-google-image-search

from bs4 import BeautifulSoup
import requests
import re
import urllib2
import os

def find(keyword, num):

    def get_soup(url,header):
      return BeautifulSoup(urllib2.urlopen(urllib2.Request(url,headers=header)))

    image_type = "Action"
    query = keyword
    query= query.split()
    query='+'.join(query)
    url="https://www.google.co.in/search?q="+query+"&source=lnms&tbm=isch"
    url+="&tbs=isz:i" #icon size only
    header = {'User-Agent': 'Mozilla/5.0'} 
    soup = get_soup(url,header)

    images = [a['src'] for a in soup.find_all("img", {"src": re.compile("gstatic.com")})]

    return images[:num]
