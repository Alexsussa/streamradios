import os
import sys
import socket
from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup

url = 'https://web.whatsapp.com'
open_url = urlopen(url).read()
soup = BeautifulSoup(open_url, 'html.parser')
page = soup.find('div', attrs={'class': ''})
images = soup.findAll('img')
img = images[0]

print(img.attrs['src'])
download = url + img.attrs['src']
save = urllib.request.urlretrieve(download, 'chrome.png')
