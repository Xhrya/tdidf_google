import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import requests

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
    elif pathname == '/sentiment':
        return html.Div([
            html.H1("Sentiment Analysis using TF-IDF and GCP NLP"),
            dcc.Graph(id='tfidf-bar-chart'),
            dcc.Graph(id='sentiment-pie-chart')
        ])
    # Add similar conditions for other pages
    return html.Div([html.H1("404: Page not found")])

@app.callback(
    [Output('tfidf-bar-chart', 'figure'),
     Output('sentiment-pie-chart', 'figure')],
    [Input('url', 'pathname')]
)
def update_sentiment(pathname):
    if pathname == '/sentiment':
        try:
            response = requests.get('http://127.0.0.1:5000/api/tfidf')
            data = response.json()

            top_terms = data['top_terms']
            sentiment_results = data['sentiment_results']

            terms = [term for term, _ in top_terms]
            scores = [score for _, score in top_terms]
            sentiment_scores = [result[0] for result in sentiment_results.values()]
            sentiment_magnitudes = [result[1] for result in sentiment_results.values()]

            # Create TF-IDF bar chart
            tfidf_figure = go.Figure(data=[
                go.Bar(x=terms, y=scores, name='TF-IDF Scores')
            ])
            tfidf_figure.update_layout(title='Top TF-IDF Terms')

            # Create Sentiment Pie chart
            sentiment_figure = go.Figure(data=[
                go.Pie(labels=['Positive', 'Neutral', 'Negative'], values=sentiment_scores, name='Sentiment')
            ])
            sentiment_figure.update_layout(title='Sentiment Analysis')

            return tfidf_figure, sentiment_figure

        except Exception as e:
            print(f"An error occurred in update_sentiment: {e}")
            return go.Figure(), go.Figure()
    return go.Figure(), go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
