from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
from components import recent_comment, valid_dates, monthly_wordcloud, comments_hourly, comments_weekly

# Get recent comment info
content, username = recent_comment()

# Establish valid dates for wordcloud
years, months_map = valid_dates()

# Initialize the app
app = Dash(__name__)

# App layout
app.layout = html.Div(className = 'body', children = [
    # Header text
    html.Div(className = 'first-block', children = 'Gonna put some text on the side here eventually!'),

    # Most recent comment
    html.Div(className = 'second-block', children = [
            html.P(className = 'recent-comment-title', children = 'Most recent 949 comment!'),
            html.Blockquote(className = 'recent-comment-content-block', children = [
                html.P(className = 'recent-comment-content', children = content),
                html.Footer(className = 'recent-comment-signature', children = f"- {username}")
            ]),
        # Wordcloud object
        html.Div(className = 'wordcloud-panel', children=[
            html.P(className = 'wordcloud-panel-title', children = 'The 949 over time'),
            # dropdown menu to select year
            dcc.Dropdown(className = 'wordcloud-year-selector', options = years, value=2022, id='wordcloud-year-selector', clearable=False),
            # slider with months based on selected year
            dcc.Slider(id='month-slider',
                       included=False,
                       step = 1,
                       min_month = {},
                       max_month = {},
                       value = {},
                       marks = {}),
            # Figure object from callback
            dcc.Graph(figure={}, id='cloud_object')])
    ]),

    # Comment frequency graphs
    html.Div(className = 'third-block', children=[
        # Total comments posted each week
        dcc.Graph(figure=comments_weekly(), id='comments_weekly'),
        # Total comments posted by hour
        dcc.Graph(figure=comments_hourly(), id='comments-hourly')
    ])   
])

# Callbacks
# Output - Word cloud figure
# Inputs - Selected year and month
@callback(
    Output(component_id='cloud_object', component_property='figure'),
    Input(component_id='month-slider', component_property='value'),
    Input(component_id='wordcloud-year-selector', component_property='value')
)
# Returns cloud object
def update_cloud(month, year):
    cloud = go.Figure(data=[go.Image(z=monthly_wordcloud(month=month, year=year))])
    return cloud

# Output - min, max, values, marks of month slider
# Input - year selection from year dropdown
@callback(
    Output(component_id='month-slider', component_property='min'),
    Output(component_id='month-slider', component_property='max'),
    Output(component_id='month-slider', component_property='value'),
    Output(component_id='month-slider', component_property='marks'),
    Input(component_id='wordcloud-year-selector', component_property='value')
)
# returns updated slider parameters
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