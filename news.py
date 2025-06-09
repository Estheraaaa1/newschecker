import streamlit as st
import requests
import feedparser
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
from collections import Counter
import re

st.title("📰 Google News 爬蟲＋情緒分析")
keyword = st.text_input("請輸入要搜尋的關鍵字", "Czech election")

if st.button("開始搜尋"):
    with st.spinner("抓取新聞中..."):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        url = f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}"
        response = requests.get(url, headers=headers)
        feed = feedparser.parse(response.content)

        st.write(f"找到 {len(feed.entries)} 筆 RSS 項目")

        articles = []

        for entry in feed.entries:
            link = entry.link
            title = entry.title

            try:
                article_html = requests.get(link, headers=headers, timeout=5)
                soup = BeautifulSoup(article_html.content, "html.parser")

                # ✅ 嘗試抓前 10 段落
                paragraphs = soup.find_all("p")
                text = ' '.join(p.get_text() for p in paragraphs[:10]).strip()

                # ✅ 若太短，用 <article> 備援
                if len(text) < 100:
                    article_tag = soup.find("article")
                    if article_tag:
                        text = article_tag.get_text().strip()

                # ✅ 若還是太短，用 <div> 備援
                if len(text) < 100:
                    div_tag = soup.find("div")
                    if div_tag:
                        text = div_tag.get_text().strip()

                # ✅ 最後備援：用標題情緒分析
                if not text or len(text) < 50:
                    text = title
                    st.info(f"🟡 僅用標題做情緒分析：{link}")

                sentiment = TextBlob(text).sentiment.polarity

                articles.append({
                    "Title": title,
                    "Link": link,
                    "Sentiment": sentiment,
                    "Text": text
                })

            except Exception as e:
                st.warning(f"⚠️ 抓取錯誤：{link}\n{e}")
                continue

        if not articles:
            st.error("🚫 沒有成功抓到有效新聞")
        else:
            df = pd.DataFrame(articles)
            st.success(f"🎉 成功擷取 {len(df)} 筆新聞")

            st.dataframe(df[["Title", "Sentiment"]])

            st.subheader("🎯 情緒最正面新聞")
            best = df.sort_values("Sentiment", ascending=False).iloc[0]
            st.write(best["Title"])
            st.write(best["Link"])

            st.subheader("🚨 情緒最負面新聞")
            worst = df.sort_values("Sentiment", ascending=True).iloc[0]
            st.write(worst["Title"])
            st.write(worst["Link"])

            all_words = []
            for text in df["Text"]:
                words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
                all_words.extend(words)

            common_words = Counter(all_words).most_common(20)
            st.subheader("🧠 詞頻分析（Top 20）")
            for word, count in common_words:
                st.write(f"{word}: {count}")

