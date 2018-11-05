import sys
import os

import pandas as pd
import numpy as np

import requests as rq
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urljoin
import webtoon_config as WC
import json

main_title = sys.argv[1]

path = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

meta = pd.read_csv( path + "/data/meta/meta.csv" )
total = pd.DataFrame()

def make_link(webtoon_url, page_count):
    return webtoon_url + '&page=' + str(page_count)

def data_parse(soup, url):
    rank = soup.select('#topPointTotalNumber')[0].text
    title = soup.title.text.split(':')[0]

    titleId = str(parse_qs(urlparse(url).query)['titleId'][0])
    no = str(parse_qs(urlparse(url).query)['no'][0])

    comment_url = WC.NAVER_URL + '/comment/comment.nhn?titleId=' + titleId + '&no=' + no
    objectId = titleId + '_' + no

    page_count = 1

    u = 'http://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=comic&templateId=webtoon&pool=cbox3&_callback=jQuery1113012327623800394427_1489937311100&lang=ko&country=KR&objectId=' + objectId + '&categoryId=&pageSize=15&indexSize=10&groupId=&listType=OBJECT&sort=NEW&_=1489937311112'
    df = pd.DataFrame()
    #num = 0;
    while True:
        #print(df.shape)
        comment_url = make_link(u, page_count)
        header = {
            "Host": "apis.naver.com",
            "Referer": "http://comic.naver.com/comment/comment.nhn?titleId=" + titleId + "&no=" + no,
            "Content-Type": "application/javascript"
        }

        res = rq.get(comment_url, headers=header)
        soup = BeautifulSoup(res.content, 'lxml')
        #print(num)
        #print('\n')
        #num += 1
    
        try:
            content_text = soup.select('p')[0].text
            one = content_text.find('(') + 1
            two = content_text.find(');')
            content = json.loads(content_text[one:two])
            
            comments = content['result']['commentList']
            
            for comment_info in comments:
                user_title_dict = {'userId': comment_info['userIdNo'], 'title': comment_info['objectId']}
                #print(user_title_dict)
                #print('\n')
                df = df.append(user_title_dict, ignore_index=True)
            
            #print(titleId, no)
            if not len(comments):
                break
            else:
                page_count += 1
                print(page_count)
        except:
            break
            pass
    return df

for title, link in meta[meta['maintitle'] == main_title][['maintitle','link']].values:

    res = rq.get(link)
    webtoon_page_soup = BeautifulSoup(res.content, 'lxml')
    turn = data_parse(webtoon_page_soup, link)
    turn['main_title'] = title
    total = total.append(turn,ignore_index = True)
    
total.to_csv(path + '/data/comment_data/'+ str(main_title)+'.csv')
