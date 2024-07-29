from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the mapping data
esg_topics_df = pd.read_csv('/path/to/esg_top_topic_mappings.csv')
buzzword_topic_df = pd.read_csv('/path/to/buzzword_to_topic_mapping.csv')
with open('/path/to/esg_keywords.txt') as f:
    esg_keywords = f.read().splitlines()

# Create mappings
buzzword_to_topic = dict(zip(buzzword_topic_df['Buzzword'], buzzword_topic_df['Topic']))
topic_to_esg = dict(zip(esg_topics_df['Topic'], esg_topics_df['ESG']))

# Function to scrape ESG data from website (dummy function for illustration)
def scrape_esg_from_website(urls):
    # Replace with actual scraping logic
    return {
        'environment': 'Sample environment data',
        'social': 'Sample social data',
        'governance': 'Sample governance data'
    }

# Dummy topic modeling function (replace with actual implementation)
def topic_modeling(text):
    # Replace with actual topic modeling logic
    return [('Topic 1', 'Sample text for topic 1'), ('Topic 2', 'Sample text for topic 2')]

# Dummy sentiment analysis function (replace with actual implementation)
def sentiment_analysis(text):
    # Replace with actual sentiment analysis logic
    return 'Positive'

@app.route('/scrape_esg_data/<bank>', methods=['GET'])
def scrape_esg_data(bank):
    urls_list = urls.get(bank)
    if not urls_list:
        return jsonify({'error': 'Bank not found'}), 404

    try:
        data = scrape_esg_from_website(urls_list)
        
        # Combine all text for topic modeling
        all_text = ' '.join(data.values())
        topics = topic_modeling(all_text)
        
        # Map buzzwords to topics and topics to ESG categories
        topic_counts = {}
        for buzzword in buzzword_to_topic.keys():
            if buzzword in all_text:
                topic = buzzword_to_topic[buzzword]
                esg_category = topic_to_esg.get(topic, 'Other')
                if esg_category not in topic_counts:
                    topic_counts[esg_category] = 0
                topic_counts[esg_category] += 1
        
        # Sentiment analysis for topics
        topic_sentiments = {f"{topic[0]}": sentiment_analysis(topic[1]) for topic in topics}

        return jsonify({
            'esg_data': data,
            'topic_modeling': list(topic_counts.keys()),
            'topic_sentiments': topic_sentiments
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5050, debug=True)


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import requests

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# ESG Data and Topic Modeling Layout
esg_layout = html.Div([
    html.H1("ESG Data and Topic Modeling"),
    html.Div([
        html.H2("Select Bank:"),
        dcc.Dropdown(
            id='bank-dropdown',
            options=[
                {'label': 'JPMorgan', 'value': 'jpmorgan'},
                {'label': 'Goldman Sachs', 'value': 'goldman'},
                {'label': 'Barclays', 'value': 'barclays'},
                {'label': 'HSBC', 'value': 'hsbc'},
                {'label': 'Morgan Stanley', 'value': 'morgan_stanley'},
                {'label': 'Deutsche Bank', 'value': 'db'}
            ],
            value='jpmorgan'
        ),
    ]),
    html.Button('Scrape Data', id='scrape-button', n_clicks=0),
    dcc.Loading(
        id="loading-esg",
        type="circle",
        children=[
            html.Div(id='esg-data'),
            html.Div(id='topic-modeling'),
            html.Div(id='topic-sentiments')
        ]
    )
])

# Main Layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dcc.Loading(
        id="loading",
        children=[html.Div(id='page-content')],
        type="circle"
    )
])

# Read data files
esg_topics_df = pd.read_csv('/mnt/data/esg_top_topic_mappings.csv')
buzzword_topic_df = pd.read_csv('/mnt/data/buzzword_to_topic_mapping.csv')
with open('/mnt/data/esg_keywords.txt') as f:
    esg_keywords = f.read().splitlines()

# Create mappings
buzzword_to_topic = dict(zip(buzzword_topic_df['Buzzword'], buzzword_topic_df['Topic']))
topic_to_esg = dict(zip(esg_topics_df['Topic'], esg_topics_df['ESG']))

# Callback for scraping data based on bank selection
@app.callback(
    [Output('esg-data', 'children'),
     Output('topic-modeling', 'children'),
     Output('topic-sentiments', 'children')],
    [Input('scrape-button', 'n_clicks')],
    [State('bank-dropdown', 'value')]
)
def scrape_data(n_clicks, bank):
    if n_clicks > 0:
        response = requests.get(f'http://localhost:5050/scrape_esg_data/{bank}')
        data = response.json()

        if 'error' in data:
            return html.Div(['Error scraping data']), None, None

        esg_data = data.get('esg_data', {})
        topics = data.get('topic_modeling', [])
        sentiments = data.get('topic_sents', {})

        esg_div = html.Div([
            html.H3("ESG Data"),
            html.P(f"Environment: {esg_data.get('environment')}"),
            html.P(f"Social: {esg_data.get('social')}"),
            html.P(f"Governance: {esg_data.get('governance')}")
        ])

        topic_div = html.Div([
            html.H3("Topic Modeling"),
            html.Ul([html.Li(f"{topic}") for topic in topics])
        ])

        sentiment_div = html.Div([
            html.H3("Topic Sentiments"),
            html.Ul([html.Li(f"{topic}: {sentiment}") for topic, sentiment in sentiments.items()])
        ])

        return esg_div, topic_div, sentiment_div
    return None, None, None

if __name__ == '__main__':
    app.run_server(debug=True)
