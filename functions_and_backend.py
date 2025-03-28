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
    """
        This function finds peak in the data and then returns the starting and the finishing years of the peak

        Function type: Generator

        Args: data (pandas.DataFrame): dataframe that contains a year series and a numerical value to check for peaks

        Yields: dictionary with two values 'start' (int), 'end'(int) representing the start and end year for each peak
    """
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

def yearly_data_asylum(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(['country_of_origin_name', 'year']).agg({'count': 'sum'}).reset_index()

def only_the_top_for_year(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    """
        Compares the all the countries and change the name of the country to 'Other' if its less than the constant minimum value 

        Args:
            df (pandas.DataFrame): the DataFrame to work on

        Returns:
            pandas.DataFrame with the values changed.
    """
    MINIMUN_PARTICIPATION = 0.05
    df = df[(start_year <= df['year']) & (df['year'] <= end_year)]
    

    
    years = df['year'].unique().tolist()

    for year in years:
        yearly_df = df[df['year'] == year]
        total_asylums = yearly_df['count'].sum()
        countries = yearly_df['country_of_origin_name'].unique().tolist()

        for country in countries:
            asylum_per_country = yearly_df[yearly_df['country_of_origin_name'] == country]['count'].sum()
            if (asylum_per_country / total_asylums) < MINIMUN_PARTICIPATION:
                df.loc[(df['country_of_origin_name'] == country) & (df['year'] == year), 'country_of_origin_name'] = 'Other'
    
    return df.groupby(['country_of_origin_name', 'year']).agg({'count': 'sum'}).reset_index()

def Top_four_countries(df: pd.DataFrame) -> pd.DataFrame:
    years = df['year'].unique().tolist()

    for year in years:
        yearly_df = df[df['year'] == year]
        countries = yearly_df['country_of_origin_name'].unique().tolist()
        yearly_df = yearly_df.groupby('country_of_origin_name').agg({'count': 'sum'})
        top_4 = yearly_df.sort_values('count', ascending=False).head(4).reset_index()

        for country in countries:
            if not top_4['country_of_origin_name'].isin([country]).any():
                df.loc[(df['country_of_origin_name'] == country) & (df['year'] == year), 'country_of_origin_name'] = 'Other'
        df.loc[~df['country_of_origin_name'].isin(top_4['country_of_origin_name']), 'country_of_origin_name'] = 'Other'
    return df
            
def wrap(df: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    return only_the_top_for_year(df, start_year, end_year)

# Graph functions:

def Country_of_origin():
    as_by_country = asylum.groupby('country_of_origin_name').agg({'count' : 'sum'})
    as_by_country = as_by_country.sort_values('count', ascending=True).reset_index()
    as_by_country = as_by_country[as_by_country['count'] > 100_000]
    fig = px.bar(as_by_country, y='country_of_origin_name', x='count', orientation='h')
    # TODO: Log scale
    fig.update_layout(height=2000)
    fig.show()

def New_asylum_seekers_graph():
    """
        Displays a graph showing the new Asylum seekers by year with highlights of the migration crisis

        Return: no return value, only display
    """
    asylum_by_countries = asylum.groupby(['country_of_origin_name', 'year']).agg({'count': 'sum'}).reset_index().sort_values('count', ascending=False)
    custom_for_template = asylum_by_countries.groupby('year')

    # "By default the group keys are sorted during the groupby operation." Pandas docs https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html
    # This extra hover text can be separated into a function a check for countries with less than 3 rows
    extra_hover_text = [
            f"<b>Year: {year}<br>" +
            f"Total: {countries["count"].sum():,}<br><br>" +
            f"Top three origin countries:</b><br>" +
            f"{countries.iloc[0]['country_of_origin_name']}: {countries.iloc[0]['count']:,}<br>" +
            f"{countries.iloc[1]['country_of_origin_name']}: {countries.iloc[1]['count']:,}<br>" +
            f"{countries.iloc[2]['country_of_origin_name']}: {countries.iloc[2]['count']:,}<br>" +
            f"Other: {countries[3:]['count'].sum():,}"
        for year, countries in custom_for_template
        ]
    
    # Plot the timelime
    ## Data
    timeline = asylum.groupby('year').agg({'count': 'sum'}).reset_index()

    ## Setting trace
    trace = go.Scatter(x=timeline['year'], y=timeline['count'])
    fig = go.Figure(trace)



    for peak in Peak_finder(timeline):
        fig.add_shape(type="rect",
                    x0=peak['start'], y0=0, x1=peak['end'], y1=10300000,
                    fillcolor="tomato", opacity=0.5,
                    layer="below", line_width=0)


    fig.update_traces(
        customdata=extra_hover_text,
        hovertemplate="%{customdata}"

    )

    fig.update_layout(
        title='Total asylumn seeker population over the years (highlighted migration crisis)',
        xaxis={'title': {'text': "Years"}, 'showgrid':False},
        yaxis={'title': {'text': 'Asylum Seekers'}, 'rangemode': 'tozero', 'showgrid':False}
    )
    fig.show()




def Dasher():
    app = Dash(__name__)

    migration_crisis = list(Peak_finder(asylum.groupby('year').agg({'count': 'sum'}).reset_index()))
    options = [f"{years['start']}-{years['end']}" for years in migration_crisis]
    app.layout = html.Div([
        html.H2('Migration crisis'),
        html.P('Select period:'),
        dcc.Dropdown(
            id="dropdown",
            options=options,
            value=options[0],
            clearable=False,
        ),
        dcc.Graph(id="graph"),
        
    ], style={'backgroundColor':'white'})

    @app.callback(
        Output("graph", "figure"),
        Input("dropdown", "value"))

    def update_bar_chart(years):
        years = years.split('-')
        fig = go.Figure()
        period_data = only_the_top_for_year(asylum, int(years[0]), int(years[1])).sort_values('count')
        g = period_data.groupby('country_of_origin_name')
        for country, data in g:
            custom = [
            f"<b>{line['country_of_origin_name']}</b><br>"
            f"Total: {line['count']:,}<br>" +
            f"<b>{(line['count'] / (period_data[period_data['year'] == line['year']]['count'].sum())):%}</b> of the year asylum seeker population"
            for index, line in data.iterrows()
            ]
            fig.add_trace(
                go.Bar(name=country, x=data['year'], y=data['count'], customdata=custom, hovertemplate="%{customdata}"))
            
        fig.update_layout(barmode='stack')
        fig.update_layout(
        title='Total asylum seekers by country of origin (countries that represent less than 5% are group in "Other")',
        xaxis={'title': {'text': "Years"}, 'showgrid':False},
        yaxis={'title': {'text': 'Asylum Seekers'}}
        )
        return fig


    # TODO: Agregado en el mapa

    app.run()