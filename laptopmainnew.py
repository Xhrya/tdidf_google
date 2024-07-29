from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from collections import Counter
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from sklearn.ensemble import RandomForestClassifier
import numpy as np
from gensim import corpora, models
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import pandas as pd
import os
import io
# import tensorflow_decision_forests as tfdf
# print(tfdf.__version__)

# from sklearn.feature_extraction import TfidfVectorizer

app = Flask(__name__)

# Download NLTK data (if not already downloaded)
nltk.download('punkt')
nltk.download('stopwords')

# Define URLs for scraping (original company pages and news articles)
urls = {
    'jpmorgan': [
        # Original company pages
        'https://www.jpmorganchase.com/impact',
        'https://www.jpmorganchase.com/sustainability',
        'https://www.jpmorganchase.com/responsibility',
        'https://www.jpmorganchase.com/our-approach',
        'https://www.jpmorganchase.com/corporate-responsibility',
        'https://www.jpmorganchase.com/about-us/sustainability',
        'https://www.jpmorganchase.com/our-impact',
        'https://www.jpmorganchase.com/what-we-do/sustainability',
        'https://www.jpmorganchase.com/social-impact',
        'https://www.jpmorganchase.com/environmental-initiatives',
        # News articles
        'https://www.ft.com/content/5f26b79a-3d0d-11eb-9f7d-df6b67b9a0b1',
        'https://www.bloomberg.com/news/articles/2022-10-03/jpmorgan-chase-commitments-sustainability',
        'https://www.reuters.com/business/sustainable-business/jpmorgan-chase-corporate-responsibility-2022-08-15/',
        'https://www.wsj.com/articles/jpmorgan-chase-esg-strategies-2022-07-20',
        'https://www.forbes.com/sites/forbessustainability/2022-06-29/jpmorgan-chase-social-impact/?sh=1b8a9e6a2c2b',
        'https://www.cnbc.com/2022/05/25/jpmorgan-chase-and-climate-change.html',
        'https://www.businessinsider.com/jpmorgan-chase-environmental-policies-2022-04-10',
        'https://www.theguardian.com/business/2022/sep/12/jpmorgan-chase-esg-performance',
        'https://www.investopedia.com/jpmorgan-chase-esg-efforts-2022-08-24',
        'https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/jpmorgan-chase-corporate-governance'
    ],
    'goldman': [
        # Original company pages
        'https://www.goldmansachs.com/sustainability',
        'https://www.goldmansachs.com/corporate-sustainability',
        'https://www.goldmansachs.com/impact',
        'https://www.goldmansachs.com/about-us/our-approach',
        'https://www.goldmansachs.com/what-we-do/sustainability',
        'https://www.goldmansachs.com/social-impact',
        'https://www.goldmansachs.com/environmental-sustainability',
        'https://www.goldmansachs.com/responsibility',
        'https://www.goldmansachs.com/corporate-responsibility',
        'https://www.goldmansachs.com/our-commitments',
        # News articles
        'https://www.ft.com/content/6f2760b6-3e8b-11eb-9f84-ff1e5a3a1a2b',
        'https://www.bloomberg.com/news/articles/2022-11-04/goldman-sachs-esg-strategy',
        'https://www.reuters.com/business/sustainable-business/goldman-sachs-esg-commitments-2022-09-22/',
        'https://www.wsj.com/articles/goldman-sachs-sustainability-initiatives-2022-08-30',
        'https://www.forbes.com/sites/forbessustainability/2022-07-21/goldman-sachs-environmental-initiatives/?sh=4b8c6f5e1234',
        'https://www.cnbc.com/2022/06/15/goldman-sachs-and-climate-action.html',
        'https://www.businessinsider.com/goldman-sachs-corporate-responsibility-2022-05-17',
        'https://www.theguardian.com/business/2022/aug/03/goldman-sachs-esg-report',
        'https://www.investopedia.com/goldman-sachs-esg-strategies-2022-07-11',
        'https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/goldman-sachs-esg-performance'
    ],
    'barclays': [
        # Original company pages
        'https://www.home.barclays/sustainability',
        'https://www.home.barclays/corporate-responsibility',
        'https://www.home.barclays/impact',
        'https://www.home.barclays/what-we-do/sustainability',
        'https://www.home.barclays/responsibility',
        'https://www.home.barclays/our-approach',
        'https://www.home.barclays/social-impact',
        'https://www.home.barclays/environmental-initiatives',
        'https://www.home.barclays/corporate-sustainability',
        'https://www.home.barclays/our-impact',
        # News articles
        'https://www.ft.com/content/4d95e8c6-3e8b-11eb-bb84-21b8a55e4e0b',
        'https://www.bloomberg.com/news/articles/2022-09-29/barclays-corporate-sustainability',
        'https://www.reuters.com/business/sustainable-business/barclays-esg-efforts-2022-08-18/',
        'https://www.wsj.com/articles/barclays-environmental-initiatives-2022-07-27',
        'https://www.forbes.com/sites/forbessustainability/2022-06-28/barclays-social-impact/?sh=5a2d6b5e1e3f',
        'https://www.cnbc.com/2022/05/20/barclays-and-climate-commitments.html',
        'https://www.businessinsider.com/barclays-corporate-responsibility-2022-04-15',
        'https://www.theguardian.com/business/2022/sep/07/barclays-esg-strategy',
        'https://www.investopedia.com/barclays-esg-initiatives-2022-08-05',
        'https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/barclays-corporate-governance'
    ],
    'hsbc': [
        # Original company pages
        'https://www.hsbc.com/sustainability',
        'https://www.hsbc.com/responsible-business',
        'https://www.hsbc.com/impact',
        'https://www.hsbc.com/corporate-responsibility',
        'https://www.hsbc.com/what-we-do/sustainability',
        'https://www.hsbc.com/environmental-initiatives',
        'https://www.hsbc.com/social-impact',
        'https://www.hsbc.com/our-approach',
        'https://www.hsbc.com/responsibility',
        'https://www.hsbc.com/our-impact',
        # News articles
        'https://www.ft.com/content/4f9b4a6e-3e8b-11eb-b5f3-5f4a4a6a2a8b',
        'https://www.bloomberg.com/news/articles/2022-10-25/hsbc-sustainability-report',
        'https://www.reuters.com/business/sustainable-business/hsbc-esg-strategies-2022-09-09/',
        'https://www.wsj.com/articles/hsbc-environmental-commitments-2022-08-18',
        'https://www.forbes.com/sites/forbessustainability/2022-07-05/hsbc-corporate-responsibility/?sh=5d6e8a9e3f6b',
        'https://www.cnbc.com/2022/06/23/hsbc-and-climate-strategy.html',
        'https://www.businessinsider.com/hsbc-social-impact-2022-05-11',
        'https://www.theguardian.com/business/2022/sep/01/hsbc-esg-performance',
        'https://www.investopedia.com/hsbc-esg-initiatives-2022-08-12',
        'https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/hsbc-corporate-governance'
    ],
    'morgan_stanley': [
        # Original company pages
        'https://www.morganstanley.com/sustainability',
        'https://www.morganstanley.com/impact',
        'https://www.morganstanley.com/corporate-responsibility',
        'https://www.morganstanley.com/about-us/our-approach',
        'https://www.morganstanley.com/what-we-do/sustainability',
        'https://www.morganstanley.com/environmental-initiatives',
        'https://www.morganstanley.com/social-impact',
        'https://www.morganstanley.com/responsibility',
        'https://www.morganstanley.com/corporate-sustainability',
        'https://www.morganstanley.com/our-commitments',
        # News articles
        'https://www.ft.com/content/5bfb4f62-3e8b-11eb-a3c4-0b1f9d3b4e8b',
        'https://www.bloomberg.com/news/articles/2022-10-10/morgan-stanley-esg-initiatives',
        'https://www.reuters.com/business/sustainable-business/morgan-stanley-esg-strategies-2022-09-12/',
        'https://www.wsj.com/articles/morgan-stanley-sustainability-reports-2022-08-22',
        'https://www.forbes.com/sites/forbessustainability/2022-06-30/morgan-stanley-environmental-commitments/?sh=4c8b7f9e2e3e',
        'https://www.cnbc.com/2022/05/15/morgan-stanley-and-climate-action.html',
        'https://www.businessinsider.com/morgan-stanley-corporate-responsibility-2022-04-20',
        'https://www.theguardian.com/business/2022/sep/13/morgan-stanley-esg-performance',
        'https://www.investopedia.com/morgan-stanley-esg-strategies-2022-08-08',
        'https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/morgan-stanley-corporate-governance'
    ],
    'db': [
        # Original company pages
        'https://www.db.com/sustainability',
        'https://www.db.com/corporate-responsibility',
        'https://www.db.com/impact',
        'https://www.db.com/what-we-do/sustainability',
        'https://www.db.com/responsibility',
        'https://www.db.com/our-approach',
        'https://www.db.com/social-impact',
        'https://www.db.com/environmental-initiatives',
        'https://www.db.com/corporate-sustainability',
        'https://www.db.com/our-impact',
        # News articles
        'https://www.ft.com/content/6b77a4e6-3e8b-11eb-90d6-9e2a7e3f9e6a',
        'https://www.bloomberg.com/news/articles/2022-09-17/db-corporate-sustainability',
        'https://www.reuters.com/business/sustainable-business/db-esg-strategies-2022-08-12/',
        'https://www.wsj.com/articles/db-environmental-initiatives-2022-07-19',
        'https://www.forbes.com/sites/forbessustainability/2022-06-26/db-social-impact/?sh=1d4e7c9e3b3e',
        'https://www.cnbc.com/2022/05/22/db-and-climate-commitments.html',
        'https://www.businessinsider.com/db-corporate-responsibility-2022-04-18',
        'https://www.theguardian.com/business/2022/sep/09/db-esg-strategies',
        'https://www.investopedia.com/db-esg-performance-2022-08-04',
        'https://www.spglobal.com/marketintelligence/en/news-insights/latest-news-headlines/db-corporate-governance'
    ]
}


# Load buzzword-to-topic mapping and ESG keywords
mapping_df = pd.read_csv('../resources/buzzword_to_topic_mapping.csv')
keywords = pd.read_csv('../resources/esg_keywords.txt', header=None).squeeze().tolist()
buzzwords = mapping_df['Buzzword'].tolist()
esg_topic_mappings = pd.read_csv('../resources/esg_top_topic_mappings.csv')
buzzword_topic_mapping = pd.read_csv('../resources/buzzword_to_topic_mapping.csv').set_index('Buzzword')['Topic'].to_dict()
topic_esg_mapping = pd.read_csv('../resources/esg_top_topic_mappings.csv').set_index('Topic')['ESG'].to_dict()


def preprocess_text(text):
    stop_words = set(nltk.corpus.stopwords.words('englist'))
    tokens = nltk.tokenize.word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return ''.join(tokens)


def extract_text_from_pdf(file):
    pdf_reader = PdfReader(io.BytesIO(file.read()))
    text=''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_web(urls):
    all_text=[]
    for url in urls:
        try:
            response =requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            all_text.append(text)
        except Exception as e:
            print(f'Error scraping {url}: {str(e)}')
    return ''.join(all_text)

# @app.route('/tfdf_scraping', methods=['POST'])
# def tfdf_scraping():
#     if 'file' not in request.files and 'url' not in requst.form:
#         return jsonify({"error": "No file or URL provided"}), 400

#     if 'file' in reqest.files:
#         file = request.files['file']
#         if file.filename.endswith('.pdf'):
#             text = extract_text_from_pdf(file)
#         else:
#             return jsonify({"error": "Invalid file type"}), 400
        
#     elif 'url' in request.form:
#         urls_list = request.form.getlist('url')
#         text = extract_text_from_web(urls_list)
#     else:
#         return jsonify({"error": "Invalid request"}), 400
#     processing_text = preprocess_text(text)

#     vectorizer = TfidfVectorizer()
#     X= vectorizer.fit_transform([processed_text])
#     df = pd.DataFrame.sparse.from_spmartrix(C)

#     try:
#         model = tfdf.keras.RandomForestModel(task =tfdf.keras.tasks.Classification(num_classes=2))
#         tfdf_dataset = tfdf.keras.pd_dataframe_to_tf_dataset(df, task=tfdf.keras.tasks.Classification(num_classes=2))
        
#         # Predict using the TFDF model
#         predictions = model.predict(tfdf_dataset)
        
#         # Process predictions (example: convert to list)
#         predictions_list = [prediction.numpy().tolist() for prediction in predictions]

#         return jsonify({'predictions': predictions_list})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        # Read PDF file
        text = extract_text_from_pdf(file)
        
        # Preprocess text
        processed_text = preprocess_text(text)

        # Count keywords and buzzwords
        keywords_counts = Counter()
        buzzwords_counts = Counter()

        for keyword in keywords:
            keywords_counts[keyword] = processed_text.lower().count(keyword.lower())

        for buzzword in buzzwords:
            buzzwords_counts[buzzword] = processed_text.lower().count(buzzword.lower())

        # Get top 10 buzzwords
        top_buzzwords = sorted(buzzwords_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Map buzzwords to topics
        buzzword_to_topic = mapping_df.set_index('Buzzword')['Topic'].to_dict()
        topic_counts = Counter()
        for buzzword, count in buzzwords_counts.items():
            topic = buzzword_to_topic.get(buzzword)
            if topic:
                topic_counts[topic] += count

        # Get top 10 topics
        top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Get sentiment for each topic
        topic_sentiments = {}
        for topic, _ in top_topics:
            topic_text = ' '.join([buzzword for buzzword, buzzword_topic in buzzword_to_topic.items() if buzzword_topic == topic])
            topic_sentiments[topic] = sentiment_analysis(topic_text)

        # Map topics to ESG categories
        topic_esg_mapping = esg_topic_mappings.set_index('Topic')['ESG Category'].to_dict()
        esg_counts = {'E': 0, 'S': 0, 'G': 0}

        for topic, _ in top_topics:
            esg_category = topic_esg_mapping.get(topic)
            if esg_category:
                esg_counts[esg_category] += 1

        return jsonify({
            'top_buzzwords': top_buzzwords,
            'top_topics': top_topics,
            'topic_sentiments': topic_sentiments,
            'esg_counts': esg_counts
        })

    return jsonify({"error": "Invalid file type"}), 400



# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file provided"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     if file and file.filename.endswith('.pdf'):
#         # Read PDF file
#         pdf_reader = PdfReader(io.BytesIO(file.read()))
#         text = ''
#         for page in pdf_reader.pages:
#             text += page.extract_text()

#         # Count keywords and buzzwords
#         keywords_counts = Counter()
#         buzzwords_counts = Counter()

#         for keyword in keywords:
#             keywords_counts[keyword] = text.lower().count(keyword.lower())

#         for buzzword in buzzwords:
#             buzzwords_counts[buzzword] = text.lower().count(buzzword.lower())

#         # Convert counts to sorted lists
#         top_keywords = sorted(keywords_counts.items(), key=lambda x: x[1], reverse=True)[:10]
#         top_buzzwords = sorted(buzzwords_counts.items(), key=lambda x: x[1], reverse=True)[:10]

#         return jsonify({
#             'top_keywords': top_keywords,
#             'top_buzzwords': top_buzzwords
#         })
#     return jsonify({"error": "Invalid file type"}), 400

def scrape_esg_from_website(urls):
    all_data = {
        'environment': [],
        'social': [],
        'governance': []
    }
    
    for url in urls:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            esg_data = {
                'environment': extract_text(soup, 'environment'),
                'social': extract_text(soup, 'social'),
                'governance': extract_text(soup, 'governance')
            }
            
            for category in all_data:
                if esg_data[category] != 'N/A':
                    all_data[category].append(esg_data[category])
                    
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # Aggregate data (example: joining all texts)
    aggregated_data = {
        'environment': ' '.join(all_data['environment']),
        'social': ' '.join(all_data['social']),
        'governance': ' '.join(all_data['governance'])
    }
    
    return aggregated_data

def extract_text(soup, category):
    # Try different methods based on the website's structure
    element = soup.find(lambda tag: tag.name == 'p' and category in tag.get_text().lower())
    return element.get_text(strip=True) if element else 'N/A'

def topic_modeling(text):
    # Tokenization and stop word removal
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    
    # Create dictionary and corpus
    dictionary = corpora.Dictionary([tokens])
    corpus = [dictionary.doc2bow(tokens)]
    
    # Perform LDA
    lda_model = models.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=15)
    
    topics = lda_model.print_topics(num_words=5)
    return topics

def sentiment_analysis(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity

@app.route('/scrape_esg_data/<bank>', methods=['GET'])
def scrape_esg_data(bank):
    urls_list = urls.get(bank)
    if not urls_list:
        return jsonify({'error': 'Bank not found'}), 404

    try:
        data = scrape_esg_from_website(urls_list)
        
        # Topic modeling
        all_text = ' '.join(data.values())
        topics = topic_modeling(all_text)
        
        # Sentiment analysis for topics
        topic_sentiments = {f"Topic {i}": sentiment_analysis(topic[1]) for i, topic in enumerate(topics)}

        return jsonify({
            'esg_data': data,
            'topic_modeling': topics,
            'topic_sentiments': topic_sentiments
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scrape', methods=['POST'])
def scrape_website():
    try:
        if 'url' not in request.form:
            return jsonify({"error": "No URL provided"}), 400

        url = request.form['url']
        if not url:
            return jsonify({"error": "URL cannot be empty"}), 400

        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to retrieve URL"}), 400

        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        keywords_counts = Counter()
        buzzwords_counts = Counter()

        for keyword in keywords:
            keywords_counts[keyword] = text.lower().count(keyword.lower())

        for buzzword in buzzwords:
            buzzwords_counts[buzzword] = text.lower().count(buzzword.lower())

        top_keywords = sorted(keywords_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_buzzwords = sorted(buzzwords_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return jsonify({
            'top_keywords': top_keywords,
            'top_buzzwords': top_buzzwords
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)