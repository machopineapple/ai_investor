
import logging
import requests
import yfinance as yf
import torch
import numpy as np
import streamlit as st
from transformers import BertTokenizer, BertForSequenceClassification

# Setup logging
logging.basicConfig(filename='portfolio_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

class AIPortfolioManagerV5:
    def __init__(self, budget, risk_profile='moderate'):
        self.budget = budget
        self.cash = budget
        self.risk_profile = risk_profile
        self.holdings = {}
        self.watchlist = self.get_watchlist_by_risk(risk_profile)
        self.model, self.tokenizer = self.load_finbert()
        self.news_cache = {}
        self.price_cache = {}
        logging.info(f"Initialized with ${budget}, risk profile: {risk_profile}")

    def get_watchlist_by_risk(self, profile):
        return {
            'conservative': ['KO', 'JNJ', 'PG', 'MSFT'],
            'moderate': ['MSFT', 'AAPL', 'GOOGL', 'V'],
            'aggressive': ['TSLA', 'NVDA', 'PLTR', 'COIN']
        }.get(profile, ['AAPL', 'MSFT'])

    def load_finbert(self):
        tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
        model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone')
        model.eval()
        return model, tokenizer

    def get_price(self, symbol):
        if symbol in self.price_cache:
            return self.price_cache[symbol]
        try:
            price = yf.Ticker(symbol).history(period='1d')['Close'][-1]
            self.price_cache[symbol] = price
            return price
        except Exception as e:
            logging.error(f"Price fetch failed for {symbol}: {e}")
            return 0

    def get_news_articles(self, symbol):
        if symbol in self.news_cache:
            return self.news_cache[symbol]
        try:
            url = f"https://newsapi.org/v2/everything?q={symbol}&language=en&sortBy=publishedAt&pageSize=5&apiKey={st.secrets["NEWS_API_KEY"]}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = [article['title'] + ". " + (article.get('description') or '') for article in data['articles']]
            self.news_cache[symbol] = articles
            return articles
        except Exception as e:
            logging.error(f"News fetch failed for {symbol}: {e}")
            return []

    def get_sentiment_score(self, texts):
        scores = []
        for text in texts:
            try:
                inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1)
                score = probs[0][2].item() - probs[0][0].item()
                scores.append(score)
            except Exception as e:
                logging.warning(f"Sentiment failed on text: {e}")
                continue
        if scores:
            return np.mean(scores), np.std(scores)
        return 0, 0

    def build_portfolio(self):
        logging.info("Building initial portfolio...")
        allocation = self.budget / len(self.watchlist)
        for symbol in self.watchlist:
            price = self.get_price(symbol)
            shares = int(allocation // price) if price > 0 else 0
            self.holdings[symbol] = {'shares': shares, 'price': price}
            self.cash -= shares * price
        logging.info(f"Initial portfolio: {self.holdings}")

    def rebalance(self):
        logging.info("Rebalancing portfolio based on sentiment...")
        for symbol in self.watchlist:
            price = self.get_price(symbol)
            if price == 0:
                continue

            news = self.get_news_articles(symbol)
            sentiment, std_dev = self.get_sentiment_score(news)
            logging.info(f"{symbol} Sentiment: {sentiment:.2f}, StdDev: {std_dev:.2f}")

            if sentiment < -0.2:
                shares = self.holdings.get(symbol, {}).get('shares', 0)
                self.cash += shares * price
                self.holdings[symbol]['shares'] = 0
                logging.info(f"SELL: {symbol} - {shares} shares")

            elif sentiment > 0.4:
                investable_cash = self.cash * 0.2
                shares = int(investable_cash // price)
                if shares > 0:
                    if symbol not in self.holdings:
                        self.holdings[symbol] = {'shares': 0, 'price': price}
                    self.holdings[symbol]['shares'] += shares
                    self.cash -= shares * price
                    logging.info(f"BUY: {symbol} - {shares} shares")

    def report(self):
        report = {}
        total_value = self.cash
        for symbol, data in self.holdings.items():
            latest_price = self.get_price(symbol)
            value = data['shares'] * latest_price
            report[symbol] = {'shares': data['shares'], 'value': round(value, 2)}
            total_value += value
        report['Cash'] = round(self.cash, 2)
        report['Total Value'] = round(total_value, 2)
        logging.info(f"Report: {report}")
        return report
