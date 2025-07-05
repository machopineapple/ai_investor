
# AI Investing Assistant

This project is an AI-powered investing assistant that builds and rebalances a portfolio
based on financial data, market prices, and sentiment analysis of news articles.

## Setup

1. Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

2. Add your NewsAPI key to `.streamlit/secrets.toml`:

```toml
NEWS_API_KEY = "your_newsapi_key_here"
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

## Deployment

This project is ready to deploy on [Streamlit Cloud](https://streamlit.io/cloud).

- Push this repository to GitHub.
- Connect your GitHub repo on Streamlit Cloud.
- Streamlit Cloud will read dependencies from `requirements.txt` and secrets from `.streamlit/secrets.toml`.
