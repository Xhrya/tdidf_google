import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import requests
import pandas as pd
import base64
import io

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
        id="loading-esg",
        type="circle",
        children=[
            html.Div(id='esg-data'),
            html.Div(id='topic-modeling'),
            html.Div(id='topic-sentiments')
        ]
    )
])

# Layout for Web Scraping
scraping_layout = html.Div([
    html.H1("ESG Data Analysis"),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select Files')]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=True
    ),

    dcc.Loading(
        id="loading-upload",
        type="circle",
        children=html.Div(id='output-data-upload')
    ),

    html.Div([
        dcc.Input(id="input-url", type="text", placeholder="Enter URL to scrape"),
        html.Button('Scrape URL', id='scrape-url-button', n_clicks=0),
        dcc.Loading(
            id="loading-url",
            type="circle",
            children=html.Div(id='url-scrape-output')
        )
    ])
])

# Navbar for navigation
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("ESG Data and Topic Modeling", href="/", id="nav-link-esg")),
        dbc.NavItem(dbc.NavLink("Web Scraping", href="/scraping", id="nav-link-scraping")),
                dbc.NavItem(dbc.NavLink("Web Scraping", href="/scraping", id="nav-link-scraping")),

    ],
    brand="Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
)

# Main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# Callbacks for page navigation
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if (pathname == '/scraping'):
        return scraping_layout
    if (pathname == '/topic_modeling_scraping'):
        return scraping_layout
    else:
        return esg_layout

# Callback for handling PDF uploads
@app.callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'))
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)
        ]
        return children
    return None

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith('.pdf'):
            # Process the PDF file
            response = requests.post("http://localhost:5050/upload", files={"file": (filename, io.BytesIO(decoded))})
            data = response.json()
            if 'error' in data:
                return html.Div(['There was an error processing this file.'])

            # Create bar graphs for top keywords and buzzwords
            keywords_df = pd.DataFrame(data.get('top_keywords', []), columns=['Keyword', 'Count'])
            buzzwords_df = pd.DataFrame(data.get('top_buzzwords', []), columns=['Buzzword', 'Count'])

            keywords_fig = px.bar(keywords_df, x='Keyword', y='Count', title='Top 10 Keywords')
            buzzwords_fig = px.bar(buzzwords_df, x='Buzzword', y='Count', title='Top 10 Buzzwords')

            return html.Div([
                html.H5(filename),
                html.H6('Top Keywords'),
                dcc.Graph(figure=keywords_fig),
                html.H6('Top Buzzwords'),
                dcc.Graph(figure=buzzwords_fig),
            ])
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])

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

# Callback for scraping data from a provided URL
@app.callback(
    Output('url-scrape-output', 'children'),
    Input('scrape-url-button', 'n_clicks'),
    State('input-url', 'value')
)
def scrape_url(n_clicks, url):
    if n_clicks > 0 and url:
        response = requests.post("http://localhost:5050/scrape", data={"url": url})
        data = response.json()
        if 'error' in data:
            return html.Div([f"Error: {data['error']}"])

        top_keywords = data.get('top_keywords', [])
        top_buzzwords = data.get('top_buzzwords', [])

        keywords_df = pd.DataFrame(top_keywords, columns=['Keyword', 'Count'])
        buzzwords_df = pd.DataFrame(top_buzzwords, columns=['Buzzword', 'Count'])

        keywords_fig = px.bar(keywords_df, x='Keyword', y='Count', title='Top 10 Keywords')
        buzzwords_fig = px.bar(buzzwords_df, x='Buzzword', y='Count', title='Top 10 Buzzwords')

        return html.Div([
            html.H5(f"Results for {url}"),
            html.H6('Top Keywords'),
            dcc.Graph(figure=keywords_fig),
            html.H6('Top Buzzwords'),
            dcc.Graph(figure=buzzwords_fig),
        ])
    return None

if __name__ == '__main__':
    app.run_server(debug=True)
