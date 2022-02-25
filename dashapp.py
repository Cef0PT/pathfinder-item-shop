"""
The app is deployed on Heroku and reachable with https://pathfinder-item-shop.herokuapp.com/.
"""

import dash
from dash import html
from dash import dcc
from dash.dependencies import Output, Input, State
import pandas as pd
import plotly.graph_objects as go
import item_generator
import xlrd

# Read xls file
file_path = "./magic_items.xls"
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
                html.Img(src='assets/pathfinder_logo.png', className='header-picture'),
                html.H1(
                    children='Item Shop', className='header-title'
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
                            clearable=True,
                            searchable=True,
                            multi=True,
                            persistence=True,
                            persistence_type='local',
                            style={'padding-bottom': 5},
                            className='dropdown-long',
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
                        html.Div(id='prints1', className='print-line'),
                        html.Div(id='placeholder'),
                        html.Div(id='prints2', className='print-line')
                    ],
                    className='wrapper-txt',
                ),
            ],
            className='wrapper-output',
        ),
        html.Div(
            children=[
                html.P(
                    children='Available Items',
                    id='header-table',
                    className='header-card'
                ),
            ],
            className='wrapper-headers-cards'
        ),
        html.Div(
            children=[
                html.Div(
                    id='style-table',
                    children=dcc.Graph(
                        id='table-items',
                        config={'displayModeBar': False},
                    ),
                    className='table',
                ),
            ],
            className='wrapper-cards',
        ),

        # Footer
        html.Div(
            className='footer'
        )
    ]
)


@app.callback(
    [
        Output('prints1', 'children'),
        Output('placeholder', 'style'),
        Output('prints2', 'children'),
        Output('table-items', 'figure'),
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
    :param n_clicks:
    :param town_size:
    :param allowed_sources:
    :return:
    """
    if n_clicks is not None:
        # Run item generator
        items_dic, print_strings = item_generator.run(magic_item_list, town_size, allowed_sources)

        # Save table and output string in csv/txt files
        if items_dic is not None:
            items_df = pd.DataFrame(data=items_dic)
            items_df.to_csv('current_table.csv')
            with open('output_strings.txt', 'w') as f:
                for string in print_strings:
                    f.write(string + '\n')
        else:
            items_df = pd.DataFrame(columns=['Name', 'Quantity', 'Slot', 'Price', 'Source', 'Description'])
    else:
        # Read csv/txt files on page load
        items_df = pd.read_csv('current_table.csv')
        with open('output_strings.txt', 'r') as f:
            print_strings = f.readlines()

    # Placeholder is only needed if there are more than 3 lines
    if len(print_strings) > 3:
        placeholder_style = {'height': '18px'}
    else:
        placeholder_style = {'height': '0px'}
    # Create output strings
    outp_str1 = []
    outp_str2 = []
    for idx, string in enumerate(print_strings):
        if 'ERROR' in string:
            str_style = {'color': 'red'}
        else:
            str_style = {'color': 'black'}

        if idx <= 2:
            outp_str1.append(html.P(children=string, style=str_style, className='print-p'))
        else:
            outp_str2.append(html.P(children=string, style=str_style, className='print-p'))

    # Sort table
    price_int = []
    for price in items_df['Price']:
        numeric_filter = filter(str.isdigit, price)
        price_int.append(int(''.join(numeric_filter)))
    price_int = pd.DataFrame(data={'Price INT': price_int})
    items_df = items_df.join(price_int)
    items_df.sort_values(['Price INT', 'Name'], inplace=True)

    # Create table
    fig_table = go.Figure(
        data=[
            go.Table(
                columnwidth=[2, 1, 2, 2, 2, 12],
                header=dict(
                    values=['Item', 'Quantity', 'Slot', 'Price', 'Source', 'Description'],
                    fill_color='#222222',
                    font=dict(color='#FFFFFF'),
                    align='left',
                    height=40),
                cells=dict(
                    values=[
                        items_df['Name'],
                        items_df['Quantity'],
                        items_df['Slot'],
                        items_df['Price'],
                        items_df['Source'],
                        items_df['Description']
                    ],
                    fill_color='#dde4eb',
                    align='left',
                    height=40,
                )
            )
        ]
    )
    height = 80 * (len(items_df['Name']) + 1)
    height = 800
    fig_table.update_layout(margin=dict(l=3, r=18, t=0, b=0),
                            height=height)
    h = {'height': height}  # it is necessary to return a table height for some reason, this cant be done in css (wtf)

    return outp_str1, placeholder_style, outp_str2, fig_table, h


if __name__ == '__main__':
    app.run_server()
