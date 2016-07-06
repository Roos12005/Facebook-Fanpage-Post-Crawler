#!/usr/bin/python
#-*-coding: utf-8 -*-
from __future__ import print_function
import sys
import requests
import json
import mysql.connector

##### EDIT HERE <<<<<
config = {
  'user': 'root',
  'password': '1234',
  'host': '127.0.0.1',
  'database': 'facebookcrawldb'
}
#####################

# FUNCITON parseme
def parseme(content, field, cursor):
    i=0
    if 'paging' in content[field]:
        items = content[field]
        while 'paging' in items:
            for item in items['data']:

                ##### EDIT HERE <<<<<
                # Console Log
                i+=1
                print(str(i)+" "+item['id'])

                # Insertion Query
                query = ("INSERT INTO posts_of_page "
                            "(id, message, permalink_url, likes_count, comments_count, shares_count) "
                            "VALUES (%(id)s, %(message)s, %(permalink_url)s, %(likes_count)s, %(comments_count)s, %(shares_count)s)")
                # Binding Data
                query_data = {
                    'id': item['id'],
                    'message': item.get('message',''),
                    'permalink_url': item.get('permalink_url',''),

                    # 'likes_count': item['likes']['summary']['total_count'],
                    'likes_count': item.get('likes',{}).get('summary',{}).get('total_count',-1),

                    # 'comments_count': item['comments']['summary']['total_count'],
                    'comments_count': item.get('comments',{}).get('summary',{}).get('total_count',-1),

                    # 'shares_count': item['shares']['count'],
                    'shares_count': item.get('shares',{}).get('count',-1),
                }
                # print(query_data)
                #####################
                cursor.execute(query, query_data)

            # if have next page -> goto next page
            if 'next' in items['paging']:
                url2 = items['paging']['next']
                items = requests.get(url2).json()
            else:
                break



# FUNCITON main
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

friend_id_list = []
for line in sys.stdin:
    line = line.strip()
    ACCESS_TOKEN = line

    ##### EDIT HERE <<<<<
    base_url = 'https://graph.facebook.com/v2.6/345056712217661'
    fields = 'posts.limit(100).summary(true){likes.limit(0).summary(true),comments.limit(0).summary(true),message,permalink_url,shares}'
    focused_field = 'posts'
    #####################

    url = '%s?fields=%s&access_token=%s' % (base_url,fields,ACCESS_TOKEN)
    content = requests.get(url).json()
    # print(content)

    parseme(content, focused_field, cursor)

# Make sure data is committed to the database
cnx.commit()

cursor.close()
cnx.close()



##NOTE TO ME: create table
# CREATE TABLE `facebookcrawldb`.`posts_of_page` (
#   `id` INT NOT NULL,
#   `message` TEXT NULL,
#   `permalink_url` VARCHAR(256) NULL,
#   `likes_count` INT NULL,
#   `comments_count` INT NULL,
#   `shares_count` INT NULL,
#   PRIMARY KEY (`id`));

##NOTE TO ME: query
#345056712217661?fields=posts.limit(10).summary(true){likes.limit(0).summary(true)}
#345056712217661?fields=posts.limit(10).summary(true){likes.limit(0).summary(true),comments.limit(0).summary(true)}
#345056712217661?fields=posts.limit(100).summary(true){likes.limit(0).summary(true),comments.limit(0).summary(true),message,permalink_url,shares}
