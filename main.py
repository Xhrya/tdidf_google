from flask import Flask, jsonify, abort
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from google.cloud import language_v1
import numpy as np
import pandas as pd
from esg_scraper import scrape_data
import re
import json
from google.cloud import language_v1

app = Flask(__name__)

# Initialize GCP NLP client
client = language_v1.LanguageServiceClient()

def analyze_sentiment_gcp(text):
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment
    return sentiment.score, sentiment.magnitude

@app.route('/api/tfidf', methods=['GET'])
def get_tfidf_sentiment():
    try:
        # Scrape data
        barclys_data = scrape_data('barclys')
        hbsc_data = scrape_data('hbsc')
        db_data = scrape_data('db')

        if not barclys_data or not hbsc_data or not db_data:
            raise ValueError("One or more data sources are empty.")

        documents = {
            "barclys": barclys_data,
            "hbsc": hbsc_data,
            "db": db_data
        }

        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(documents.values())
        feature_names = vectorizer.get_feature_names_out()

        # Aggregate scores
        scores = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
        terms_scores = dict(zip(feature_names, scores))

        # Get top terms
        sorted_terms = sorted(terms_scores.items(), key=lambda x: x[1], reverse=True)
        top_terms = sorted_terms[:10]

        # GCP Sentiment Analysis
        sentiment_results = {term: analyze_sentiment_gcp(term) for term, score in top_terms}

        response = {
            "top_terms": top_terms,
            "sentiment_results": sentiment_results
        }

        return jsonify(response)
    except Exception as e:
        print(f"An error occurred in /api/tfidf: {e}")
        abort(500)  # Internal Server Error

if __name__ == '__main__':
    app.run(debug=True)

# pip install google-cloud-language google-cloud-core
# pip show google-cloud-language
