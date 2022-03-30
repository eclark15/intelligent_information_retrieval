# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 12:47:56 2020

@author: emilyclark
"""


from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import pandas as pd
import random 
import math



def gatherPageText(url, soup, webPageID):      #gathers all of the page text, processes it through re, removes stop words 
    global indexCount                          #stems each word and places the stemmed and regular words into the postingsDict
#####getting all text on a page##########      #also is updating the postingsDict to include stemmed word, webpageID, TF values 
    text = soup.find_all(text=True)

    output = ''              #tags we do not want 
    notagsinclude = ['svg', 'script', 'o-social-wall-dynamic', 'o-website-finder-dynamic', 'video', 'm-search-field-dynamic', 'html', '[document]', 'div', 'section', 'span', 'head']
    for items in text:
        if items.parent.name not in notagsinclude:      #certain website tags are not useful for extracting content so we do not want that text
            output += '{} '.format(items)
    
    outputReg= re.split(r'\W+', output)                 #using regular expressions to clean up our terms 
    
    stop_words = nltk.corpus.stopwords.words('english') #removing stop words from our page terms list
    stop_words.extend(['llc', 'privacy', 'svg', 'endinject', 'cookies', 'settings', 'glassdoor', 'get', 'rights', 'notice','could','917', '421', '7209'])

    fullWords = []                             #list of ALL of the lower case words on the page 
    for word in outputReg:        
        wordLowerCase = word.lower()       
        if (wordLowerCase not in stop_words and len(wordLowerCase)>2):  #do not want any words than are shorter than 2 or are in our stop words 
            fullWords.append(wordLowerCase)                             #append each word to our list 
            
    porter = PorterStemmer()
    for word in fullWords:                     #go through all words on the page 
        stemmedWord = porter.stem(word)        #get the stemmed term
        if word not in termTokenDict.keys(): 
            termTokenDict.update({word : stemmedWord})                     #updating our dictionary with full word + token word
        
        if stemmedWord not in postingsDict.keys():                         #brand new word in our postings dict
            postingsDict.update({stemmedWord : {webPageID : [1, 'idf']}})  #stemmed word: webpageID :[TF, IDF], DocFreq : DF
        
        elif webPageID not in postingsDict[stemmedWord].keys():            #if the term is in dictionary but has not appeared in current document
            postingsDict[stemmedWord][webPageID] = [1, 'idf']
            
        else:
            TF = postingsDict[stemmedWord][webPageID][0]                   #updating the term frequency value if the term has appeared on the current page already 
            TF = TF + 1 
            postingsDict[stemmedWord][webPageID][0] = TF
            
            
    

def gatherPageLinks(url):
    
####initalizing an instance of our URL within beauitful soup###
    r  = requests.get(url)                        #retrieve the URL
    data = r.text                                 #get all data on the page 
    soup = BeautifulSoup(data, 'html.parser')     #initalize BS
    
#######getting all links on a page########
    for link in soup.find_all('a'):
        linkURL = link.get('href')                #gather all links on the page   
        try:
            if linkURL not in links:              #make sure we havent already added this URL to our list   
                if linkURL.startswith('/'):       #updated relative URLs to absolute
                    if len(linkURL) <= 2:         #do not want links less than 2 characters long 
                        continue
                    else:
                        linkURL = 'https://www.bosch.us' + linkURL    #append our relative URLS into absolute    
                        
                        if ('https://www.bosch.us' in linkURL and linkURL not in links and '#' not in linkURL and '?' not in linkURL and 'html' not in linkURL and 'pdf' not in linkURL):              
                                                                      #only want URLs from our specified domain  
                            links.append(linkURL)                     #add all new URLs we find to our links list 
        except:
            continue 
    return soup, url
    


def urlIndex(url):                                #creates instance in webPageDict with random ID for webpage 
    webPageID = random.randint(1,10000)
    webPageDict[webPageID] = url       
    return webPageID
 
    
def crawl(url):                            #crawls all web pages to discover all page links and content 
    webPageID = urlIndex(url)  
    print(webPageID, url)                  #for testing to know which pages you are on 
    soup, url = gatherPageLinks(url)       #gets us all of the URLs on the page and places them into links list              
    gatherPageText(url, soup, webPageID)   #gathers all page text and adds to index, the URL then is added to the visited list   
    visited.append(url)                    #make sure we do not visit same page twice 
    
    for link in links:            #make sure all pages are crawled and stored in index 
        if link not in visited:   #do not crawl previously crawled pages 
            try:
                crawl(link)       #recursively go through the crawl function to make sure all pages are crawled, links are obtained and text gathered 
            except:
                pass

def getDFValues():               #how many documents does each word appear? 
#Initialized once all pages have been parsed. We can now go back and get the DF and IDF values by finding the length of the postingsDict 
    for key in postingsDict.keys():            
        DF = len(postingsDict[key])
        postingsDict[key]['DocFreq'] = DF

def getIDFValues():                               #getting IDF values
#    print(len(webPageDict))
    numofPages = len(webPageDict)                 #for all of the keys in our postings (all the terms)
    for key in postingsDict.keys():               #update the IDF value by taking the log((NumofPages/DF), 2)
        DF = postingsDict[key]['DocFreq']
        IDF = math.log((numofPages/DF), 2)
        postingsDict[key]['IDF'] = IDF            #update the IDF value to the placeholder in our dict 
        for DOCID in postingsDict.get(key):
            try:
                postingsDict[key][DOCID][1] = (postingsDict[key][DOCID][0])*IDF    #get the IDF weight for each doc/term 
                del postingsDict[key][DOCID][0]                                    #optional if we need to remove the TF value
                num = postingsDict[key][DOCID][0] 
                postingsDict[key][DOCID] = num                                     #making item a number not a list 
            except:
                continue
    return postingsDict
    
    

def main():                                  #main function to run program 
    #url = input("Enter a website to extract the URL's from: ") change this so it works for all other websites
    global webPageDict, links, webPageID, termTokenDict, postingsDict, visited
    links = []              #this will be a list of all web pages 
    webPageDict = {}
    visited = []            #once the page has been crawled for text, place the link into visited 
    
    termTokenDict = {}
    postingsDict = {}
    
    url = 'https://www.bosch.us/'
    links.append(url)       #first URL will be the primary domain name and after that, links will be added from the gatherPageLinks function 
    crawl(url)
    getDFValues()
    getIDFValues()

    return postingsDict, termTokenDict, webPageDict

main()












