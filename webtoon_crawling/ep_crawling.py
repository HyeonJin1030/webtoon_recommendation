import requests
from bs4 import BeautifulSoup

import re
import pandas as pd
import numpy as np

import os

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
df = pd.read_csv(path + "/data/check_list.csv")

def get_wrt(title_id):
    r = requests.get("https://comic.naver.com/webtoon/list.nhn?titleId="+str(title_id))
    soup = BeautifulSoup(r.content, "lxml")
    wrt = soup.find("span",{"class":"wrt_nm"}).get_text()
    wrt = re.sub("\t","",wrt)
    wrt = re.sub("\n","",wrt)
    wrt = re.sub("\r",'',wrt)
    wrt = wrt.split(' / ')
    return wrt

def get_ep(title_id):
    s = "'" + str(title_id) + "','(.*?)'," #웹툰내 no(회차 정보)를 따오기 위한 정규표현식

    page = 1
    r = requests.get("https://comic.naver.com/webtoon/list.nhn?titleId="+str(title_id)+"&page="+ str(page))
    soup = BeautifulSoup(r.content, "lxml")

    is_there_next_page = 2 #2:다음 페이지 있음 / 1:다음 페이지 없음 ( 첫 페이지 제외 )

    ep = []

    while True:

        number = soup.findAll("td",{"class":"title"})

        for num in number:
            no = [re.search(s,str(num)).group(1)]
            ep = ep + no

        if is_there_next_page ==1:
            break
        else:
            page = page+1
            r = requests.get("https://comic.naver.com/webtoon/list.nhn?titleId="+str(title_id)+"&page="+ str(page))
            soup = BeautifulSoup(r.content, "lxml")
            is_there_next_page = len(soup.findAll("span",{"class":"cnt_page"}))
    
    return ep

df['wrt'] = df['title_id'].apply(lambda x: get_wrt(x))
df['episode'] = df['title_id'].apply(lambda x: get_ep(x))

df.to_csv(path + "/data/meta/webtoon_ep.csv")