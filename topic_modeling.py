import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
from util import TopicModelling

# Define the layout for the /topic_modeling page
topic_modeling_layout = html.Div([
    html.Div(children="Enter a valid Topic ID"),
    
    dcc.Dropdown(
        id='topic-dropdown',
        options=[{'label': 'Topic 1', 'value': '1'}, {'label': 'Topic 2', 'value': '2'}],  # Example options
        value='1'
    ),
    
    dcc.Upload(
        html.Button('Upload File'),
        id='upload-doc',
        multiple=False
    ),
    
    html.P(id='uploaded_file_name', children="Uploaded File: "),
    
    html.P(id='n_topics', children="Number of topics: 0"),
    
    html.Button('Query Model Data', id='query-data', n_clicks=0),
    
    dcc.Graph(id="topic-bar", figure={}),
    
    html.Div(id='output-state'),
    
    html.Hr()
])

# Define callbacks for the /topic_modeling page
def register_callbacks(app):
    @app.callback(
        Output('topic-bar', 'figure'),
        [Input('topic-dropdown', 'value')],
        [State('upload-doc', 'contents')]
    )
    def update_topic_graph(value, contents):
        return TopicModelling.update_topic_graph(value, contents)

    @app.callback(
        [Output('uploaded_file_name', 'children'),
         Output('n_topics', 'children'),
         Output('topic-dropdown', 'options')],
        [Input('upload-doc', 'filename')],
        [State('upload-doc', 'contents')]
    )
    def update_uploaded_file_name(filename, contents):
        return TopicModelling.update_uploaded_file_name(filename, contents)
