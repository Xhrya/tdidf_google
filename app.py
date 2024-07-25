import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import requests
import datetime

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout for ESG Data and Topic Modeling
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
        id="loading",
        type="circle",
        children=[
            html.Div(id='esg-data'),
            html.Div(id='topic-modeling'),
            html.Div(id='topic-sentiments')
        ]
    )
])

# Main app layout with Navbar
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

# Callback for updating page content based on URL
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return html.Div([html.H1("Home Page")])
    elif pathname == '/topic':
        return esg_layout
    elif pathname == '/sentiment':
        return html.Div([
            html.H1("Sentiment Analysis using TF-IDF and GCP NLP"),
            dcc.Graph(id='tfidf-bar-chart'),
            dcc.Graph(id='sentiment-pie-chart')
        ])
    # Add similar conditions for other pages
    return html.Div([html.H1("404: Page not found")])

# Callback for scraping ESG data and displaying results
@app.callback(
    [Output('esg-data', 'children'),
     Output('topic-modeling', 'children'),
     Output('topic-sentiments', 'children')],
    [Input('scrape-button', 'n_clicks')],
    [State('bank-dropdown', 'value')]
)
def update_output(n_clicks, selected_bank):
    if n_clicks > 0:
        url = f'http://127.0.0.1:5050/scrape_esg_data/{selected_bank}'
        response = requests.get(url)
        data = response.json()

        esg_data = data.get('esg_data', {})
        topic_modeling = data.get('topic_modeling', [])
        topic_sentiments = data.get('topic_sentiments', {})
        
        esg_content = html.Div([
            html.H3("ESG Data:"),
            html.Pre(f"Environment: {esg_data.get('environment', '')}"),
            html.Pre(f"Social: {esg_data.get('social', '')}"),
            html.Pre(f"Governance: {esg_data.get('governance', '')}")
        ])
        
        topics_content = html.Div([
            html.H3("Topics:"),
            html.Ul([html.Li(f"Topic {i+1}: {topic[1]}") for i, topic in enumerate(topic_modeling)])
        ])
        
        sentiments_content = html.Div([
            html.H3("Topic Sentiments:"),
            html.Ul([html.Li(f"Topic {i+1}: {sentiment}") for i, sentiment in enumerate(topic_sentiments.values())])
        ])
        
        return esg_content, topics_content, sentiments_content
    else:
        return html.Div(), html.Div(), html.Div()

if __name__ == '__main__':
    app.run_server(debug=True)
