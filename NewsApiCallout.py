"""
CREATEDBY: Calvin O'Keefe
DATE:03/2/2021
DESCRIPTION: 
    Queries for all news articles related to a keyword (the variable query) 
    and stores the first 100 results in a SQL Database
SETUP:
    Install all required libraries below 
    Create a NewsAPI dev account and generate a key and upate the api variable with your key
    Create a SQL database (I used mySQLWorkbench to create mine)
    Update credentials for accessing your SQL Database on line 73
    Create a SQL table called Articles with the following columns:
        Title, Description, URL, Date, Source
    Create a SQL table called Sources with the following columns
        Source
"""
from ArticleConstruct import Article
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
#pip3 install newsapi-python
from newsapi import NewsApiClient
import pymysql
import json

# Init Variables
query = 'Politics'
language = 'en'
fromDate = (datetime.today() - timedelta(days=1)).strftime("20%y-%m-%d")
toDate = datetime.today().strftime("20%y-%m-%d")
api = NewsApiClient(api_key="YOURAPIKEYHERE")

#Calls the NewsAPI 5 times (dev can only query the first 100 articles) and create a list of results
def getArticles(query, sources, language, fromDate, toDate):
    result = []
    for i in range(1,6):
        result.append(api.get_everything(q=query, sources=sources, language=language, from_param=fromDate, to=toDate, page=i))
    return result

#Optional for if you want to choose the sources the API picks from (this picks all of them)
def createSourceQuery():
    result = api.get_sources()
    sourceSet = []
    for source in result.get('sources'):
        sourceSet.append(source.get('id'))
    sourceQ = "INSERT IGNORE INTO sys.Sources (Source) VALUES "
    for source in sourceSet:
        sourceQ += ('(\'' + str(source) + '\'),')
    sourceQuery = sourceQ[:-1] + ';'
    return sourceQuery, sourceSet

def createArticleQuery(query, language, fromDate, toDate):
    articleQ = "INSERT IGNORE INTO sys.Articles (Title, Description, URL, Date, Source) VALUES "
    source_string = ','.join(sourceSet)
    result = getArticles(query, source_string, language, fromDate, toDate)
    article_list = []
    #Breaks apart articles to add to query
    for article_list in result:
        for article in article_list.get('articles'):
            titleVal = article["title"].replace('\"', '')
            titleVal = titleVal.replace('\'', '')
            descriptionVal = article["description"].replace('\"', '')
            descriptionVal = descriptionVal.replace('\'', '')
            tempArticle = Article(title = titleVal, description = descriptionVal,  url = article["url"], source = article["source"]["id"], date=toDate)
            articleQ += ('(\'' + tempArticle.title + '\',\'' + tempArticle.description + '\',\'' + tempArticle.url + '\',\'' + tempArticle.date + '\',\'' + tempArticle.source + '\'),')
    articleQuery = articleQ[:-1] + ';'
    return articleQuery

sourceQuery, sourceSet = createSourceQuery()
articleQuery = createArticleQuery(query, language, fromDate, toDate)

#UPDATE THE PASSWORD AND ANY OTHER PARAM THATS DIFFERENT IN THIS CALLOUT TO CONNECT TO YOUR SQL SERVER
conn = pymysql.connect(host='localhost', port=3306, user='MYUSERNAME', passwd='YOURPASSWORDHERE', db='mysql')
cur = conn.cursor()
cur.execute(sourceQuery)
cur.execute(articleQuery)
conn.commit()

allSources = pd.read_sql('SELECT Source FROM sys.Sources;', con=conn)
allArticles = pd.read_sql('SELECT Title, Description, URL, Source FROM sys.Articles;', con=conn)
print(allSources)
print(allArticles)

cur.close()
conn.close()
