# This python file holds all the functions needed to create the data viazualizations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output

asylum = pd.read_csv('.\\Data\\Clean\\Asylum_data.csv')
population = pd.read_csv(".\\Data\\Clean\\Population_data.csv")


def print_total_asylum_seekers():
    print(format(asylum['count'].sum(), ",d"))


def Peak_finder(data: pd.DataFrame):
    percentaje_to_check = 0.5
    previous_value = data['count'][0]
    previous_year = data['year'][0]

    inside_peak = False
    current_highlight = {}
    # Start of the highlight:
    for index, row in data.iterrows():
        if not inside_peak:
            if previous_value > 1000:
                if (row['count'] - previous_value) > (previous_value * percentaje_to_check):
                    current_highlight = {'start': previous_year, 'end': 0}
                    inside_peak = True
        else:
            if (row['count']) <= (previous_value):
                current_highlight['end'] = row['year']
                yield current_highlight
                inside_peak = False
                current_highlight = {}
        previous_value = row['count']
        previous_year = row['year']
