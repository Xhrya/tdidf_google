import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import requests
from topic_modeling import topic_modeling_layout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout with Navbar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavLink("Home", href="/", id="home-link"),
            dbc.NavLink("Chatbot", href="/chatbot", id="chatbot-link"),
            dbc.NavLink("Sentiment Analysis", href="/sentiment", id="sentiment-link"),
            dbc.NavLink("Topic Modeling", href="/topic", id="topic-link"),
            dbc.NavLink("Web Scraping", href="/scraping", id="scraping-link"),
            dbc.NavLink("About", href="/about", id="about-link"),
        ],
        brand="My Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
    ),
    dcc.Loading(
        id="loading",
        children=[
            html.Div(id='page-content'),
        ],
        type="circle"
    )
])

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return html.Div([html.H1("Home Page")])
    if pathname == '/topic_modeling':
        return topic_modeling_layout
    elif pathname == '/sentiment':
        return html.Div([
            html.H1("Sentiment Analysis using TF-IDF and GCP NLP"),
            dcc.Graph(id='tfidf-bar-chart'),
            dcc.Graph(id='sentiment-pie-chart')
        ])
    # Add similar conditions for other pages
    return html.Div([html.H1("404: Page not found")])

@app.callback(
    [
        Output('sentiment-graph', 'figure'),
        Output('sentiment-graph', 'style'),
        Output('most_recent_text_id', 'children'),
        Output('most_recent_text_content', 'children'),
        Output('most_recent_text_sentiment', 'children'),
    ],
    [Input('submit-button', 'n_clicks')],
    [State('text-input', 'value')]
)
def update_sentiment(n_clicks, text_value):
    sentiment_map = {"positive": 1, "negative": -1, "neutral": 0}
    
    if n_clicks > 0:
        try:
            # Send a GET request to the API with text as a query parameter
            response = requests.get('http://127.0.0.1:8080/api/text', params={'text': text_value})
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Print status code and raw response for debugging
            print(f"Response status code: {response.status_code}")
            print(f"Raw response content: {response.text}")

            # Check if response is empty
            if not response.text:
                raise ValueError("Empty response received")

            # Try to parse JSON response
            data = response.json()
            print(f"Parsed JSON data: {data}")

            most_recent_text_id = ""
            most_recent = None
            most_recent_timestamp = 0
            sentiment_data = []

            for k, v in data.items():
                # Find the most recent entry
                cur_timestamp = datetime.datetime.strptime(v["timestamp"][:-6], "%Y-%m-%d %H:%M:%S.").timestamp()
                if cur_timestamp >= most_recent_timestamp:
                    most_recent_timestamp = cur_timestamp
                    most_recent_text_id = k
                    most_recent = v

                # Extract sentiment data
                sentiment_data.append({'text': v['text'], 'sentiment': sentiment_map[v['sentiment']]})

            # Create a bar chart using Plotly
            fig = px.bar(sentiment_data, x='text', y='sentiment', title='Sentiment Analysis')
            return fig, {}, f"Most Recent Text ID: {most_recent_text_id}", f"Content: {most_recent['text']}", f"Sentiment: {most_recent['sentiment']}"
        
        except requests.RequestException as e:
            print(f"Request error: {e}")
            return {}, {'display': 'none'}, "Error", "Error", "Error"
        except ValueError as e:
            print(f"JSON decode error: {e}")
            return {}, {'display': 'none'}, "Error", "Error", "Error"
    else:
        return {}, {'display': 'none'}, "Most Recent Text ID: Not Loaded", "Content: Not Loaded", "Sentiment: Not Loaded"

if __name__ == '__main__':
    app.run_server(debug=True)
