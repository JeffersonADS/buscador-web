import re
from bs4 import BeautifulSoup
import requests
import requests_cache
import sqlite3
from time import sleep


requests_cache.install_cache('web-scrapping')

connection = sqlite3.connect('buscador.sqlite')
cursor = connection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS data
              (url text not null,
               keyword text not null,
               occurrences int)''')


global informations
informations = []


def search(keyword, url, depth):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html5lib')
    links = [link.get('href') for link in soup.find_all('a', href=re.compile('^(http|https)://'))]
    text = soup.get_text()


    cursor.execute("select * from data where keyword = '{}' and url = '{}'".format(keyword, url))
    query = cursor.fetchall()
    
    
    if len(query) == 0:
        amount_of_occurrences = len(re.findall(keyword, text, re.IGNORECASE))
        if amount_of_occurrences > 0:
            information = [url, keyword, amount_of_occurrences]
            print(f'URL: {information[0]}\tKeyword: {information[1]}\tAmount of occurrences: {information[2]}\n')
            sleep(0.5)
            informations.append(information)

        if depth > 0:
            depth -= 1
            amount_of_links = len(links)
            for i in range(amount_of_links):
                try:
                    search(keyword=keyword, url=links[i], depth=depth)
                except:
                    continue


search('comunidade', 'https://fedorabr.org', 1)

informations.sort(key=lambda information: information[2], reverse=True)

cursor.executemany('INSERT INTO data VALUES (?,?,?)', informations)
connection.commit()
connection.close()


