# Import packages
from dash import Dash, html, dcc, callback, Output, Input
from dash.html import Link
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
from nltk.corpus import stopwords
from config import DB_PASS, LOCALHOST
import cv2
import re
from wordcloud import WordCloud
import pandas as pd
import numpy as np
import psycopg2


# Incorporate data
conn = psycopg2.connect(
        host = LOCALHOST,
        port = 5432,
        database = 'youtube_comments',
        user = 'postgres',
        password = DB_PASS,
    )

def recent_comment():
    cursor = conn.cursor()

    cursor.execute("SELECT content, username FROM comments_raw WHERE published = (SELECT MAX(published) FROM comments_raw)")

    content, username = cursor.fetchall()[0]

    cursor.close()

    return content, username

def valid_dates():
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT (EXTRACT(YEAR FROM published)) AS years FROM comments_cleaned;")

    years = np.squeeze(cursor.fetchall())

    months_map = {}

    for year in years:
        cursor.execute("SELECT DISTINCT EXTRACT(MONTH FROM published) FROM comments_raw WHERE EXTRACT(YEAR FROM published) = %s", (str(year), ))
        months = np.squeeze(cursor.fetchall())

        months_map[year] = months

    return years, months_map

def monthly_wordcloud(month, year):

    def get_frequencies(column):
        content = column.apply(lambda x: [token for token in x.split()])
        stop_words = set(stopwords.words("english"))
        pattern = r'[a-zA-Z0-9]'
        all_tokens = []
        for comment in content:
            all_tokens.extend([token for token in comment if (bool(re.search(pattern, token)) and token not in stop_words)])

        return Counter(all_tokens)
    
    cursor = conn.cursor()

    cursor.execute(f"SELECT content FROM comments_cleaned WHERE EXTRACT(YEAR FROM published) = {year} AND EXTRACT(MONTH FROM published) = {month}")

    data = cursor.fetchall()

    cursor.close()

    df = pd.DataFrame(data, columns = ['content'])

    frequencies = get_frequencies(df['content'])

    trojan = cv2.imread('./images/trojan.png')

    return WordCloud(width=800, height=800, background_color=(240, 240, 240), colormap='Accent', mask = trojan, contour_color='black', contour_width=1).generate_from_frequencies(frequencies=Counter({word:count for word,count in frequencies.most_common(100)}))

# Get recent comment info
content, username = recent_comment()

# Establish valid dates for wordcloud
years, months_map = valid_dates()

# Make seaborn time-series plots
def comments_weekly():
    cursor = conn.cursor()
    cursor.execute('SELECT published FROM comments_raw')
    data = cursor.fetchall()
    data = pd.DataFrame(data, columns = ['timestamp'])
    counts = data['timestamp'].apply(lambda x: np.array(datetime(x.year, x.month, x.day))).value_counts()
    counts = counts.reset_index().resample('W', on='timestamp').sum()
    fig = px.scatter(
        x = counts.index,
        y = counts['count'],
        trendline='rolling',
        trendline_options={'window':3}
    )
    fig.update_layout(title='Total Comments Posted by Week')
    fig.update_xaxes(title='Date')
    fig.update_yaxes(title='')

    cursor.close()

    return fig

def comments_hourly():
    cursor = conn.cursor()
    cursor.execute('SELECT EXTRACT(HOUR FROM published) FROM comments_raw')
    data = cursor.fetchall()
    data = pd.DataFrame(data, columns = ['hour'])
    counts = data['hour'].value_counts()
    fig = px.scatter(
        x = counts.index,
        y = counts.values / sum(counts.values)
    )
    fig.update_layout(title='Proportion of Comments Posted by Hour')
    fig.update_xaxes(title='Time', tickvals=[0,4,8,12,16,20,23], ticktext=['12am', '4am', '8am', '12pm', '4pm', '8pm', '11pm'])
    fig.update_yaxes(title='', tickvals=[0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14], ticktext=['2%', '4%', '6%', '8%', '10%', '12%', '14%'])

    cursor.close()

    return fig

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div(className = 'body', children = [
    html.Div(className = 'first-block', children = 'Gonna put some text on the side here eventually!'), 
    html.Div(className = 'second-block', children = [
            html.P(className = 'recent-comment-title', children = 'Most recent 949 comment!'),
            html.Blockquote(className = 'recent-comment-content-block', children = [
                html.P(className = 'recent-comment-content', children = content),
                html.Footer(className = 'recent-comment-signature', children = f"- {username}")
            ]),
        html.Div(className = 'wordcloud-panel', children=[
            html.P(className = 'wordcloud-panel-title', children = 'The 949 over time'),
            dcc.Dropdown(className = 'wordcloud-year-selector', options = years, value=2022, id='wordcloud-year-selector', clearable=False),
            dcc.Slider(id='month-slider', included=False, min=1, max=12, step=1, value=8, marks={i:month for i,month in zip(range(1,13), ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'])}),
            dcc.Graph(figure={}, id='cloud_object')])
    ]),
    html.Div(className = 'third-block', children=[
        dcc.Graph(figure=comments_weekly(), id='comments_weekly'),
        dcc.Graph(figure=comments_hourly(), id='comments-hourly')
    ])   
])

@callback(
    Output(component_id='cloud_object', component_property='figure'),
    Input(component_id='month-slider', component_property='value'),
    Input(component_id='wordcloud-year-selector', component_property='value')
)
def update_cloud(month, year):
    cloud = go.Figure(data=[go.Image(z=monthly_wordcloud(month=month, year=year))])
    return cloud

# dcc.Slider(id='month-slider', included=False, min=1, max=12, step=1, value=8, marks={i:month for i,month in zip(range(1,13), ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'])}),
@callback(
    Output(component_id='month-slider', component_property='min'),
    Output(component_id='month-slider', component_property='max'),
    Output(component_id='month-slider', component_property='value'),
    Output(component_id='month-slider', component_property='marks'),
    Input(component_id='wordcloud-year-selector', component_property='value')
)
def update_slider(year):
    months = [int(val) for val in months_map[year]]

    min_month = min(months)
    max_month = max(months)

    initial_month = (min_month + max_month) // 2

    all_months = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

    marks = {i:month for i, month in zip(range(min_month, max_month + 1), all_months[min_month-1: max_month])}

    return min_month, max_month, initial_month, marks

# Run the app
if __name__ == '__main__':
    app.run(debug=True)