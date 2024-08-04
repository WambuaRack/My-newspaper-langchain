from flask import Flask, render_template, request
import requests
from transformers import pipeline

app = Flask(__name__)

NEWS_API_KEY = '1496bf594f084f4bb63f6ffd348a37c8'  # Your NewsAPI key

def fetch_news():
    url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    news_data = response.json()
    articles = []
    if news_data.get('articles'):
        for item in news_data['articles']:
            if item['content']:
                articles.append({
                    'title': item['title'],
                    'url': item['url'],
                    'content': item['content']
                })
    return articles

def summarize_article(content):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary = summarizer(content, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
    return summary

def filter_articles(articles, keywords):
    filtered_articles = [article for article in articles if any(keyword.lower() in article['title'].lower() for keyword in keywords)]
    return filtered_articles

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keywords = request.form.get('keywords').split(',')
        articles = fetch_news()
        if not articles:
            return render_template('index.html', articles=None, error="No articles found. Please try again.")
        
        filtered_articles = filter_articles(articles, keywords)
        for article in filtered_articles:
            article['summary'] = summarize_article(article['content'])
        return render_template('index.html', articles=filtered_articles, error=None)
    return render_template('index.html', articles=None, error=None)

if __name__ == "__main__":
    app.run(debug=True)
