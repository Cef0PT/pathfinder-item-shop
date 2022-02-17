"""
The app is deployed on Heroku and reachable with https://pathfinder-item-shop.herokuapp.com/.
"""

import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import pandas as pd
import item_generator
import xlrd

# Read xls file
file_path = ".\\magic_items.xls"
header_rows = 1

magic_item_list = []
with xlrd.open_workbook(file_path) as excel_file:
    sheet = excel_file.sheet_by_index(0)
    for row in range(header_rows, sheet.nrows):
        current_item = {}
        for column in range(sheet.ncols):
            current_item[sheet.cell_value(0, column)] = sheet.cell_value(row, column)
        magic_item_list.append(current_item)

# Get unique available sources
available_sources = sorted(set({k: [dic[k] for dic in magic_item_list] for k in magic_item_list[0]}['Source']))
available_sources.remove('')

# Define app - Includes all assets by default
external_stylesheets = [
    {
        'href': 'https://fonts.googleapis.com/css2?'
                'family=Lato:wght@400;700&display=swap',
        'rel': 'stylesheet',
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server  # Heroku needs a variable named 'server'
app.title = 'Pathfinder Item Shop'

# Create the layout of the dashboard
# HTML components get converted to actual html code
app.layout = html.Div(
    children=[
        # Header
        html.Div(
            children=[
                html.H1(
                    children='Pathfinder Item Shop', className='header-title'
                ),
            ],
            className='header',
        ),

        # Menu
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Button(
                            children='Generate Items',
                            id='update-button',
                            n_clicks=0,
                            className='button',
                        ),
                    ],
                    className='wrapper-button',
                ),

                html.Div(
                    children=[
                        html.Div(children='Stadtgröße', className='menu-title'),
                        dcc.Dropdown(
                            id='town-size',
                            options=[{'label': size, 'value': size} for size in item_generator.town_sizes],
                            value='Großstadt',
                            clearable=False,
                            searchable=True,
                            persistence=True,
                            persistence_type='local',
                            className='dropdown',
                        ),
                    ],

                ),
                html.Div(
                    children=[
                        html.Div(children='Regelwerke', className='menu-title'),
                        dcc.Dropdown(
                            id='sources',
                            options=[{'label': source, 'value': source} for source in available_sources],
                            value=["PFRPG Core", "APG", "RotRL-AE-Appendix", "Advanced Race Guide",
                                   "Advanced Class Guide", "Adventurer's Guide", "Ultimate Equipment",
                                   "Occult Adventures", "Ultimate Intrigue"],
                            clearable=False,
                            searchable=True,
                            multi=True,
                            persistence=True,
                            persistence_type='local',
                            className='dropdown-long'
                        ),
                    ],
                ),
            ],
            className='menu',
        ),

        # Body
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.P(
                            children='Table',
                            id='header-table',
                            className='header-card'
                        ),
                    ],
                    className='wrapper-header-single'
                ),
            ],
            className='wrapper-headers-cards'
        ),
        html.Div(
            children=[
                html.Div(
                    id='style-table',
                    children=dcc.Graph(
                        id='table-counties',
                        config={'displayModeBar': False},
                    ),
                    className='table',
                    style={'height': 500},
                ),
            ],
            className='wrapper-cards',
        ),

        # Footer
        html.Div(
            children=[
                html.P(
                    children='abc',
                    className='footer-description'
                ),
                html.Div(
                    className='placeholder'
                ),
                html.P(
                    children='def',
                    className='footer-description'
                ),
            ],
            className='footer'
        )
    ]
)


@app.callback(
    [
        Output('table-counties', 'figure'),
        Output('style-table', 'style'),
    ],
    [
        Input('update-button', 'n_clicks'),
    ],
    [
        State('town-size', 'value'),
        State('sources', 'value'),
    ],
)
def generate_items(n_clicks: int, town_size: str, allowed_sources: list):
    """
    Trigger if site is reloaded or button is pressed
    todo: prevent trigger if site is loaded (save in "cache"?)
    :param n_clicks:
    :param town_size:
    :param allowed_sources:
    :return:
    """
    # Get data
    items_df = pd.DataFrame(data=item_generator.run(magic_item_list, town_size, allowed_sources))
    test = items_df['Price']
    test2 = items_df['Item']

    fig_table = go.Figure(data=[go.Table(  # columnwidth=[3, 1, 1, 3, 3],
        header=dict(values=['Item', 'Slot', 'Price', 'Source', 'Description'],
                    fill_color='paleturquoise',
                    align='left',
                    height=40),
        cells=dict(
            values=[
                items_df['Item'],
                items_df['Slot'],
                items_df['Price'],
                items_df['Source'],
                items_df['Description']
            ],
            fill_color='lavender',
            align='left',
            height=40,))])
    height = 40 * (len(items_df) + 1)
    fig_table.update_layout(margin=dict(l=0, r=0, t=0, b=0),
                            height=height)
    h = {'height': height}

    return fig_table, h


if __name__ == '__main__':
    app.run_server()
