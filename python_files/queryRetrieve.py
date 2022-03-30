# -*- coding: utf-8 -*-
"""

@author: emilyclark
"""
import pandas as pd
from final_index import postingsDict, termTokenDict, webPageDict



def processQuery(query):
    queryList = query.split()
    relevantWords = []

    for word in queryList:                  #checking to see if any of our query words are in our dict  
        try:                                #if they are, then we add the tokenized version of that word into and get a list of our relevantWords
            relevantWords.append(termTokenDict[word]) 
        except:
            continue

    queryDict = {}
    print("these are our token relevant words: ", relevantWords) #check for term frequency in our query (TF)
    
    for word in relevantWords:
        if word in queryDict.keys():
            count = queryDict[word][0]
            count += 1
            queryDict[word][0] = count         #updating our term count for query if we've already seen it 
        else:
            queryDict[word] = [1, 'TFIDF']     #update queryDict if it is the 1st time we are seeing this term 
    
    for word in queryDict.keys():              #calculate the TFIDF weighted value for each one of our query terms   
        IDFValue = postingsDict[word]['IDF']   #get IDF value for that particular term 
        TF = queryDict[word][0]
        TFIDF = IDFValue*TF
        queryDict[word][1] = TFIDF             #update our dict with the correct TFIDF value 
    
    for word in queryDict.keys():   
        del queryDict[word][0]                 #remove the TF value
        num = queryDict[word][0]
        queryDict[word] = num                  #making item a number not a list 
        
    queryList = []
    for value in queryDict:                    #making a list of our TFIDF so we can easily compute the cosine
        queryList.append(queryDict[value])
    
    print("\n this is our query list:", queryList)
    return queryList, queryDict

def processPostings(queryDict):
    postingsDictQuery = {}
    for word in queryDict.keys():                         #only want the keywords within our query and all of the postings for those terms  
        postingsDictQuery[word] = postingsDict[word]      #pulling out only keywords from our query from the postings
    
    ####clean up postings list for query######
    postingsDictQueryDF = pd.DataFrame(postingsDictQuery)
    postingsDictQueryDFClean = postingsDictQueryDF.drop('IDF', axis=0)
    postingsDictQueryDFClean = postingsDictQueryDFClean.drop('DocFreq', axis=0)
    postingsDictQueryDFClean.fillna(0, inplace=True)      #gives us our dataframe with rows of docs and columns for keywords 
    
    return postingsDictQueryDFClean

def getCosineSimiliarty(postingsDictQueryDFClean, queryList):   #computing cosine similarity between our query and all of the docs
    import numpy as np
    from numpy.linalg import norm
    
    def cosine_similarity(QueryVect, DocVect):                  #returns cosine similarity when 2 lists are entered 
        cosine = np.dot(QueryVect,DocVect)/(norm(QueryVect) * norm(DocVect))
        return cosine
    
    rowLists = postingsDictQueryDFClean.values.tolist()         #create a list from our cleaned DataFrame
    cosineList = []
    for row in rowLists:                                        #for loop going through each doc, computing cosine and appending result to cosineList
        COS = cosine_similarity(queryList, row)
        cosineList.append(COS)
               
    postingsDictQueryDFClean["Cosine Similiarity"] = cosineList #make new column for our cosine 
    cosineScores = postingsDictQueryDFClean.sort_values(by="Cosine Similiarity", ascending=False) #sort DF by cosine score 
    print(cosineScores)
    
    return cosineScores


def returnWebPages(cosineScores):            
    topPages = cosineScores.head(7)          #looking to find the top 7 most relevant pages 
    topPagesIDNum = []                       #based on the highest cosine score 
    topURLs = []
    for row in topPages.index: 
        topPagesIDNum.append(row)            #get all of the row ID #'s for top pages 
    for ID in topPagesIDNum:
        topURLs.append(webPageDict.get(ID))  #use the row ID numbers to find the actual URL from our webPageDict
    
    return topURLs


def returnTextFromPage(topURLs, query):               #return some text from each relevant page 
    from bs4 import BeautifulSoup
    import requests
    import re
    ####initalizing an instance of our URL within beauitful soup###
    count = 0
    print('\n Your query was: ', query)
    for URL in topURLs:
        r  = requests.get(URL)                        #retrieve the URL
        data = r.text                                 #get all data on the page 
        soup = BeautifulSoup(data, 'html.parser')     #initalize BS
        text = soup.find_all(text=True)
        output = ''
        notagsinclude = ['svg', 'script', 'o-social-wall-dynamic', 'button', 'ul','o-website-finder-dynamic', 'main', 'a', 'ol', 'meta', 'video', 'header', 'form', 'li', 'body', 'nav', 'm-search-field-dynamic', 'link', 'picture', 'html', 'figure', '[document]', 'div','img', 'section', 'footer', 'span', 'title', 'head']
        for items in text:
            if items.parent.name not in notagsinclude:
                output += '{} '.format(items)

        count = count + 1        
        print("{} most relevant page: {}. \n Text Introduction: {} \n \n".format(count, URL, output[236:400]))




def mainQuery():                                           #primary function that calls on each one of the functions above 
    query = 'internships in marketing or design'
#    query = 'environmental sustainability responsibility'
    
    #query = input("please enter your search query: ")
    queryList, queryDict = processQuery(query)
    postingsDictQueryDFClean = processPostings(queryDict)
    cosineScores = getCosineSimiliarty(postingsDictQueryDFClean, queryList)
    topURLs = returnWebPages(cosineScores)
    returnTextFromPage(topURLs, query)
    
mainQuery()

