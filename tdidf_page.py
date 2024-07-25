import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import requests

# Create a Dash app for this page
app = dash.Dash(__name__, suppress_callback_exceptions=True, use_pages=True)

app.layout = html.Div([
    html.H1("TF-IDF Sentiment Analysis"),
    html.Button('Fetch TF-IDF Sentiment Data', id='fetch-data', n_clicks=0),
    dcc.Graph(id='sentiment-graph'),
    html.Div(id='api-response')
])

@app.callback(
    [
        Output('sentiment-graph', 'figure'),
        Output('api-response', 'children')
    ],
    [Input('fetch-data', 'n_clicks')]
)
def update_sentiment_graph(n_clicks):
    if n_clicks > 0:
        try:
            # Call the Flask API
            response = requests.get('http://127.0.0.1:5000/api/tfidf')
            response.raise_for_status()
            data = response.json()
            
            # Process the data for visualization
            terms = [item[0] for item in data['top_terms']]
            scores = [item[1] for item in data['top_terms']]
            fig = px.bar(x=terms, y=scores, labels={'x': 'Terms', 'y': 'Scores'}, title='Top Terms by TF-IDF Score')

            # Format sentiment results for display
            sentiment_text = '\n'.join([f"Term: {term}, Score: {score}, Sentiment Score: {sentiment[0]}, Sentiment Magnitude: {sentiment[1]}"
                                        for term, (score, sentiment) in data['sentiment_results'].items()])

            return fig, sentiment_text

        except requests.exceptions.RequestException as e:
            return {}, f"Error: {e}"
    return {}, "Click the button to fetch data"

if __name__ == '__main__':
    app.run_server(debug=True)

#                 html.Li(html.A("TF-IDF Analysis", href="/tfidf_page", style={"color": "white", "text-decoration": "none", "display": "flex", "align-items": "center", "height": "100%", "padding": "10px"})),
