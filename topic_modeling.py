import dash_core_components as dcc
import dash_html_components as html

# Define the layout for the /topic_modeling page
topic_modeling_layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Location component to track the URL
    html.Div(id='page-content'),  # Placeholder for the page content
    html.Nav([...]),  # Define your navbar content here

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
