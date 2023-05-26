import datetime
from abc import ABC
import psycopg2
from bs4 import BeautifulSoup
import requests
from html.parser import HTMLParser
import random
import praw
import time

top_25 = []
conn = None
cursor = None
r = None


class BestSub:
    def __init__(self):
        global conn, cursor, r
        with open("../RedditCredentials.txt") as red_info:
            red_credentials = red_info.readlines()
            red_client_id = red_credentials[0].strip("\n")
            red_client_secret = red_credentials[1].strip("\n")
            red_client_user = red_credentials[2].strip("\n")
            red_client_pass = red_credentials[3].strip("\n")
            red_user_agent = red_credentials[4].strip("\n")
            r = praw.Reddit(client_id=red_client_id,
                            client_secret=red_client_secret,
                            username=red_client_user,
                            password=red_client_pass,
                            user_agent=red_user_agent)
        with open("../DBCredentials.txt") as db_stuff:
            db_credentials = db_stuff.readlines()
            # needed to strip newline character because format of file was weird
            db_db_name = db_credentials[0].strip("\n")
            db_name = db_credentials[1].strip("\n")
            db_pass = db_credentials[2].strip("\n")
            db_host = db_credentials[3].strip("\n")
            db_port = db_credentials[4].strip("\n")
            conn = psycopg2.connect(database=db_db_name,
                                    user=db_name,
                                    password=db_pass,
                                    host=db_host,
                                    port=db_port)
            cursor = conn.cursor()

    # noinspection PyMethodMayBeStatic
    def get_best(self):
        global top_25
        proxy = requests.get('https://free-proxy-list.net/')
        soup = BeautifulSoup(proxy.content, 'html.parser')
        table_body = soup.find('tbody')
        row = table_body.find('tr')
        proxy_num = row.find('td')
        proxy_num = proxy_num.text

        proxies = {
            "http": proxy_num,
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'
        }
        page = requests.get('https://www.reddit.com/subreddits/leaderboard/', headers=headers, proxies=proxies)
        soup = BeautifulSoup(page.content, features='html.parser')
        popular_subs = soup.find_all('li', attrs={'class': "_267lcOmg8VvXcoj9O0Q1TB"})
        parser = MyHTMLParser()
        parser.feed(str(popular_subs))
        rand_num = random.randint(0, 24)
        random_top = top_25[rand_num]
        command = (
            """
                INSERT INTO POPULAR_SUBREDDITS VALUES (%s, %s, %s);
            """
        )
        sub_name = str(random_top)[3:len(random_top) - 1]
        subreddit = r.subreddit(sub_name)
        num_subs = subreddit.subscribers
        curr_time = time.mktime(datetime.datetime.now().timetuple())
        to_insert = (sub_name, num_subs, curr_time)
        try:
            cursor.execute(command, to_insert)
        except Exception:
            return False
        conn.commit()
        return True

    # noinspection PyMethodMayBeStatic
    def red_inst(self):
        return r

    # noinspection PyMethodMayBeStatic
    def get_conn(self):
        return conn

    # noinspection PyMethodMayBeStatic
    def get_cursor(self):
        return cursor


# just for the sake of getting top 25 trending for the day

class MyHTMLParser(HTMLParser, ABC):
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if "/r/" in attr[1]:
                top_25.append(attr[1])
