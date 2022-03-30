
README FILE

For this IR project, I created a search engine retrieval system that crawls the entire  
https://www.bosch.us and returns the top 7 most relevant web pages based on the user’s search query. 

The search retrieval system consists of two python files, one that contains the index of the website 
(called final_index.py) and the other file that retrieves the users search query and returns the relevant 
web pages (called queryRetrieve.py). 

The index would work for any website however minor edits to the code would be needed within the 
gatherPageLinks() function since I needed to append the relative URLs into absolute URLs. However, this 
could be done very easily. 

To run, simply call the main() function in the final_index.py file which will activate the website crawler. 
3 dictionaries will be returned postingsDict, termTokenDict, webPageDict.

1. postingsDict - contains the primary index with our stemmed words, doc IDF weighted value, DOCFREQ, IDF 
EXAMPLE: stemmed term: {webpageID : IDF weighted value, WebpageID2 : 'scale': {8123: 8.98370619265935, 3692: 4.491853096329675, 'DocFreq': 2, 'IDF': 4.491853096329675}

2. termTokenDict - full term : token value 
3. webPageDict - website ID : full URL


queryRetrieve.py -
takes in a users search query (this can also be adjusted). 
Returns the 10 7 most relevant web pages based on the search query by using cosine similarity. 