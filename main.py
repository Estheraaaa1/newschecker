import snscrape.modules.twitter as sntwitter
import pandas as pd

query = 'Russia disinformation since:2024-06-01 until:2024-06-04 lang:en'
tweets = []

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    if len(tweets) >= 100:  # 可改成1000或更多
        break
    tweets.append([tweet.date, tweet.user.username, tweet.content])

df = pd.DataFrame(tweets, columns=['Date', 'Username', 'Content'])
print(df.head())
