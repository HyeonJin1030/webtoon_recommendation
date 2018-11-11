import requests
from bs4 import BeautifulSoup

import re
import pandas as pd
import numpy as np

import os

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

#장르별 웹툰 크롤링(title_id, 제목, 별점, 장르)

r = requests.get("https://comic.naver.com/webtoon/genre.nhn")
soup = BeautifulSoup(r.content, "lxml")
genres = soup.findAll("ul",{"class":"spot"})[0].findAll("a")

df = pd.DataFrame(data = {'main_title':[],'main_rating':[],'title_id':[], 'genre':[]})

for genre in genres:
    g_option = re.search('genre=(.*?)"',str(genre)).group(1)

    link = "https://comic.naver.com/webtoon/genre.nhn?genre=" + g_option

    r = requests.get(link)
    soup = BeautifulSoup(r.content, "lxml")
    
    main_titles = soup.findAll("dt")
    main_ranks = soup.findAll("div",{"class":"rating_type"})
    
    for main_title,main_rank in zip(main_titles,main_ranks):
    
        #제목, title_id가져오기
        title = re.search('title="(.*?)"',str(main_title.find("a"))).group(1)
        title_id = re.search('titleId=(.*?)"',str(main_title.find("a"))).group(1)
        
        #별점 가져오기
        rating = main_rank.find("strong").get_text()
        
        df = df.append({'main_title':title, 'main_rating':rating, 'title_id':title_id, 'genre':g_option},ignore_index=True)


a = df.groupby(['title_id']).agg({'genre' : lambda x: [x.tolist()]})# title_id 기준으로 장르(genre) 합치기
a['genre'] = a['genre'].apply(lambda x: np.reshape(x,-1))# genre col: 2차원list 1차원list로 변경

b = df.groupby(['title_id']).max()[['main_rating','main_title']]

final = a.join(b)

final.to_csv(path + "/data/meta/webtoon_genre.csv")
