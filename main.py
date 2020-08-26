import schedule
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import twint
import pandas as pd
from sqlalchemy import create_engine
def twitterScrapper():
    # get hashtags
    driver = webdriver.Firefox()
    response = driver.get('https://twitter.com/I/trends')
    driver.implicitly_wait(500)
    time.sleep(5)
    text = driver.find_elements_by_xpath("//div[@aria-label =  'Timeline: Trends']")
    html = text[0].get_attribute('innerHTML')
    html = BeautifulSoup(html, 'html5lib')
    string_ex = html.prettify()
    # remove HTML tags
    trending_dict = {}
    soup = BeautifulSoup(string_ex, 'html.parser')
    trendig_divs = soup.select('div.css-1dbjc4n.r-1loqt21.r-6koalj.r-1ny4l3l.r-1j3t67a.r-1w50u8q.r-o7ynqc.r-6416eg')
    for div in trendig_divs:
        inner_div = div.find_all("span", {"class": ["css-901oao",
                                                    "css-16my406",
                                                    "r-1qd0xha",
                                                    "r-ad9z0x",
                                                    "r-bcqeeo",
                                                    "r-qvutc0"]})
        if len(inner_div) > 2:
            trending_dict[inner_div[1].text.lstrip().rstrip()] = inner_div[2].text.lstrip().rstrip()
        else:
            trending_dict[inner_div[1].text.lstrip().rstrip()] = 'No of Tweets Unknown'
    # list of trends
    trends = []
    print(trending_dict)
    df = pd.DataFrame()
    for key in trending_dict.keys():
        trends.append(key)
    for i, trend in enumerate(trends):
        print("Fetching Tweets")
        c = twint.Config()
        c.Search = trend
        c.Limit = 10
        c.Store_json = True
        c.Output = "custom_out.json"
        c.Pandas = True
        twint.run.Search(c)
        Tweets_df = twint.storage.panda.Tweets_df
        Tweets_df["Tag"] = trend
        Tweets_df["Rank #"] = i+1
        df = pd.concat([df, Tweets_df])
        print(df.columns)
        driver.quit()
    print(df)
    df = df.astype("unicode")
    df["datetime"] = pd.to_datetime(df["date"])
    print(df.info())
    df = df.sort_values("Rank #", ascending=True)
    engine = create_engine('sqlite:///db_tweets.db', echo=False)
    df.to_sql('users', if_exists='replace', con=engine)
    print(engine.execute("SELECT * FROM users").fetchall())
twitterScrapper()
schedule.every().hour.do(twitterScrapper)
while True:
    schedule.run_pending()
    time.sleep(1)
