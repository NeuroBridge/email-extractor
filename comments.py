import csv
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import datetime

"""
this program takes a tsv file consisting of pubmed article ids and uses them
to find and extract their full-text links and put them into a csv file
"""


with open("neuroquery-metadata.tsv") as file:
    next(file) # skip the header row

    # will be the columns of the new file with the full text links
    ids = []
    freelinks = []
    accesslinks = []
    counter = 0
    starttime = datetime.datetime.now()

    for line in file:
        counter = counter + 1
        # extract the pubmed id from each line
        ids.append(line.split('\t')[0])

        # define the URL for an article to scrape using the pubmed id
        URL = "https://pubmed.ncbi.nlm.nih.gov/" + line.split('\t')[0]

        # make a request and process the response
        RESPONSE = requests.get(URL)
        DOC = BeautifulSoup(RESPONSE.text, "html.parser")

        """
        if the pubmed article provides links to access the full-text version,
        the links will be located in the full-text-elements-list div in the page
        """
        
        FULL_TEXT_ELEMENT = DOC.find("div", "full-text-links-list")

        """
        some articles do not provide a free link or an access link, so we
        predefine empty links and only update them if we do end up finding
        corresponding links for the article

        since free full-text links will state that they're free on the page itself,
        the algorithm currently locates the "Free" HTML text to find the free links,
        but there might be a better way of achieving the same goal
        """
        
        thisfreelink = ""
        thisaccesslink = ""
        
        if(FULL_TEXT_ELEMENT):
            for link_element in FULL_TEXT_ELEMENT.findChildren('a', href=True, recursive=False):
                if("Free" in link_element.get_text()):
                    thisfreelink = link_element['href']
                else:
                    thisaccesslink = link_element['href']
        freelinks.append(thisfreelink)
        accesslinks.append(thisaccesslink)

        if (counter % 100 == 0):
            print(counter)
            endtime = datetime.datetime.now()
            print(starttime)
            print(endtime)
            starttime = datetime.datetime.now()
            

        time.sleep(2)

    # combine ids and links into a csv file        
    df = pd.DataFrame(list(zip(ids, freelinks, accesslinks)), columns =['id', 'free links', 'access links'])
    df.to_csv("neuroquery-links.csv", encoding='utf-8', index=False)
