# -*- coding: utf-8 -*-

from nltk.tokenize import word_tokenize, sent_tokenize, RegexpTokenizer
from nltk.corpus import stopwords 
from nltk.stem import PorterStemmer, WordNetLemmatizer
from newsapi import NewsApiClient
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import string
from datetime import datetime, timedelta


    
# this functions returns the top 10 words for each article  
def tokenize(article):
    '''
    This function tokenizes an article, removes stopwords, lemmatizes the tokens
    and computes the TFIDF for each article. It then extracts and returns the 
    top 10 words in the article based on the TFIDF computation
    '''
    
    tokens = word_tokenize(article)    

    # Removing Stopwords
    stop_words = set(stopwords.words('english')) 
    token_no_stop = [w for w in tokens if not w in stop_words] 
    
    # Removing punctuations during tokenization
    token_no_punct = [t for t in token_no_stop if t not in string.punctuation 
                      and t != '“' and t != '--' and t != '’' and t != '…']
    
    # Lemmatizing
    lemmatizer = WordNetLemmatizer()
    article_lem = [lemmatizer.lemmatize(w) for w in token_no_punct] 
    
    return article_lem



def getNewsInfo():
    '''
    Function that will be called from the Main Application. 
    It reads news from the internet related to a particle stock using a WebAPI. It
    then extracts the top 10 words of the 3 latest news articles using NLP features.
    This function returns a dictionary that embodies all information related to the news
    articles and consists of the following keys and elements.
    
    'NumArticles' : Contain the number of articles [Integer]
    'StartDate' : Date from which articles are considered [String]
    'EndDate' : Date till which articles are considered [String]
    'Source' :  Website from which the news articles are extracted [String]
    'Topwords_Corpus' : The top 10 words of the entire corpus  [List]
    'TopWords_Article' : The top 10 words in each of latest 3 articles together with their timestamp
                    [Dictionary with timestamp as key and list of top 10 words as values]
    '''
    
    # Creating the corpus
    newsapi = NewsApiClient(api_key='70a6e58d4f8f4350a6d01b1b0c28abe5')
        
    # Calculating Today's date
    today = str(datetime.now())
    # Calculating the date for 30 days before
    month_before = str(datetime.now() - timedelta(days=30))
    source = 'bloomberg'
     
    # Extracting articles between this day and a month before       
    all_articles = newsapi.get_everything(q='Microsoft',
                                          #sources='bbc-news',                                     
                                          sources=source,
                                          from_param=month_before,
                                          to=today,                                     
                                          language='en',
                                          sort_by='relevancy'
                                          )                                
    
    
    # List that will hold all the articles
    corpus_list = []
    
    
    # Dictionary that will hold the timestamp as key and the article as corresponsong values
    corpus_dict = {}
    
    # Dictionary that will hold the latest 3 news articles, the article number and their timestamps
    top_3_dict = {}
    
    # The format in Datetime to which the string timestamps are going to be converted to
    fmt = "%Y-%m-%dT%H:%M:%S"
    
    numArticles= len(all_articles['articles'])
    for i in range(numArticles):
        news = all_articles['articles'][i]['content']
        time = all_articles['articles'][i]['publishedAt']
        
        # Extract the timestamp and convert it into datetime format
        time_mod = time.split('Z')[0]
        dt = datetime.strptime(time_mod, fmt)

        # Case Normalization
        news_lower = news.lower()
        
        # Append the news article to the corpus list for TDIDF computation
        corpus_list.append(news_lower)
        
        article_list = [i, news_lower]
        
        #Append the news article to the dictionary with timestamp as key
        corpus_dict[dt] = article_list        
        
    # Sorting the dictionary by timestamp in descending order
    sorted_time = (sorted(corpus_dict.keys(), reverse=True))    
    
    # Creating a dictionary with the latest 3 articles and their timestamps
    count = 0
    
    for time in sorted_time:
        #Eliminating the articles that are warnings
        if corpus_dict[time][1] != "to continue, please click the box below to let us know you're not a robot.":
            top_3_dict[time] = corpus_dict[time]
            count += 1
        if count > 2:
            break       
 
    # Dictionary to be returned by function containing all information
    all_info_dict = {}
    
        
    # Compute TFIDF
    tfidf = TfidfVectorizer(sublinear_tf=True, tokenizer=tokenize)
    tfs = tfidf.fit_transform(corpus_list) 
    
    features = np.array(tfidf.get_feature_names())
    
    #Top 10 words of the corpus list...all the articles
    tfidf_sorting = np.argsort(tfs.toarray()).flatten()[::-1]
    n = 10
    top_n_corpus = features[tfidf_sorting][:n]
    
    top_n_articles = []
    topwords_article = {}
    
    # Top 10 words of each of the latest 3 articles
    for key in top_3_dict.keys():
        top_n_articles = []
        article_index = top_3_dict[key][0]
        tfidf_sorting = np.argsort(tfs[article_index].toarray()).flatten()[::-1]
        top_10_words = features[tfidf_sorting][:n]
        top_n_articles.append(list(top_10_words))
        top_articles = [j for i in top_n_articles for j in i]
        topwords_article[key] = top_articles
        
           
    # Populating the dictionary to be returned
    all_info_dict['NumArticles'] = numArticles
    all_info_dict['StartDate'] = month_before.split(" ")[0]
    all_info_dict['EndDate'] = today.split(" ")[0]
    all_info_dict['Source'] = source
    all_info_dict['TopWords_Corpus'] = top_n_corpus
    all_info_dict['TopWords_Articles'] =  topwords_article
    
    return all_info_dict



