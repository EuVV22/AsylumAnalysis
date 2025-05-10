# This python file holds all the functions needed to create the data viazualizations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output

asylum = pd.read_csv('.\\Data\\Clean\\Asylum_data.csv')
population = pd.read_csv(".\\Data\\Clean\\Population_data.csv")

# Data class
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

# Data class
def Top_four_countries(df: pd.DataFrame) -> pd.DataFrame:
    """
        dep
    """
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

# Data class
def Country_population_data(country_code: str, population_data: pd.DataFrame, asylum_data: pd.DataFrame) -> pd.DataFrame:
    country_population = population_data[population_data["Country Code"] == country_code].drop(columns=["Country Name", "Country Code"]).transpose().reset_index()
    country_population.columns = ['year', 'population']
    country_population['year'] = country_population['year'].astype(int)

    country = asylum_data[asylum_data["country_of_origin_abbr"] == country_code].groupby("year", as_index=False)["count"].sum()
    
    country = country.merge(right= country_population, how='left', on='year')
    country.drop(country[country['population'].isna()].index, inplace=True)
    country["percentage_of_population_migration"] = (country["count"] / country["population"]) * 100

    country.rename(columns={'count': "displaced"}, inplace=True)
    country["country_of_origin_abbr"] = country_code
    return country

# Data class
def Get_country_population_df(pop, asy) -> pd.DataFrame:
    countries = asy["country_of_origin_abbr"].unique()
    countries_not_in_the_analysis = []
    full_data = pd.DataFrame()
    for country in countries:
        if country in pop['Country Code'].values:
            full_data = pd.concat([full_data, Country_population_data(country, population_data=pop, asylum_data=asy)])
        else:
            countries_not_in_the_analysis.append(asylum[asylum['country_of_origin_abbr'] == country]['country_of_origin_name'].iloc[0])
        
    # print('These countries were remove from the Dataframe due to not existing in the WorldBank population dataset:')
    # print(countries_not_in_the_analysis)
    return full_data

# Data class
def Get_Destination_by_year_df(df: pd.DataFrame, country_abbr: str) -> pd.DataFrame:
    result = df[df['country_of_origin_abbr'] == country_abbr]
    result = result.groupby(['year', 'country_of_asylum_abbr']).agg({'count' : 'sum'}).reset_index()
    result['merge_column'] = result['country_of_asylum_abbr'] + result['year'].astype(str)
    return result

# Data class
def Get_countries_and_years_df(df: pd.DataFrame) -> pd.DataFrame:
    countries = df['country_of_asylum_abbr'].unique()
    years = df['year'].unique()
    result = pd.DataFrame(columns=["country", "year"])
    for country in countries:
        c_list = [country] * len(years)
        country_list_df = pd.DataFrame({"country" : c_list, "year" : years})
        result = pd.concat([result, country_list_df], ignore_index=True)
    result['merge_column'] = result['country'] + result['year'].astype(str)
    return result

## TODO: For loop at group by with if statement

def Merge_and_clean_df(destination_df: pd.DataFrame, years_df: pd.DataFrame) -> pd.DataFrame:
    final = years_df.merge(destination_df, on='merge_column', how='left')
    final[final['year_x'] != final['year_y']]
    final = final.drop(columns=['year_y', 'merge_column', 'country_of_asylum_abbr'])
    final = final.rename(columns={'year_x': 'year'})
    final['count'] = final['count'].fillna(0)
    final['cumulative_sum'] = final.groupby('country')['count'].cumsum()
    return final

def Get_ready_for_plot_df(df: pd.DataFrame, country_of_origin_abbr: str) -> pd.DataFrame:
    destination = Get_Destination_by_year_df(df, country_of_origin_abbr)
    yearly = Get_countries_and_years_df(destination)
    return Merge_and_clean_df(destination, yearly)    

def Get_total_country_migration_df(df: pd.DataFrame, country_of_origin_abbr: str) -> pd.DataFrame:
    return df[df['country_of_origin_abbr'] == country_of_origin_abbr].groupby('year').agg({'count' : 'sum'}).reset_index()


# Graph functions:

def print_total_asylum_seekers():
    """
        Prints the total sum of all asylum seekers
    """
    print(format(asylum['count'].sum(), ",d"))

# Visualization class
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

def Country_of_origin():
    as_by_country = asylum.groupby('country_of_origin_name').agg({'count': 'sum'})
    as_by_country = as_by_country.sort_values('count', ascending=True).reset_index()
    as_by_country = as_by_country[as_by_country['count'] > 100_000]
    
    fig = px.bar(
        as_by_country,
        y='country_of_origin_name',
        x='count',
        orientation='h',
        title="<b>Total Asylum Seekers by Country of Origin</b>",
        labels={'country_of_origin_name': 'Country of Origin', 'count': 'Total Asylum Seekers'}
    )
    
    fig.update_layout(
        height=1500,  
        title_x=0.5, 
        title_font=dict(size=20, color='black'), 
        xaxis=dict(
            title="<b>Total Asylum Seekers</b>",
            showgrid=True,
            gridcolor='lightgrey',
            zeroline=False
        ),
        yaxis=dict(
            title="<b>Country of Origin</b>",
            showgrid=False
        ),
        plot_bgcolor='white',
        margin=dict(l=150, r=50, t=50, b=50)
    )
    fig.update_traces(marker_color='#ad0b0b')
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
            f"Total: {countries['count'].sum():,}<br><br>" +
            f"Top three origin countries:</b><br>" +
            f"{countries.iloc[0]['country_of_origin_name']}: {countries.iloc[0]['count']:,}<br>" +
            f"{countries.iloc[1]['country_of_origin_name']}: {countries.iloc[1]['count']:,}<br>" +
            f"{countries.iloc[2]['country_of_origin_name']}: {countries.iloc[2]['count']:,}<br>" +
            f"Other: {countries[3:]['count'].sum():,}"
        for year, countries in custom_for_template
        ]
    
    # Plot the timeline
    ## Data
    timeline = asylum.groupby('year').agg({'count': 'sum'}).reset_index()

    ## Setting trace
    trace = go.Scatter(
        x=timeline['year'], 
        y=timeline['count'],
        mode='lines+markers',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6, color='#ff7f0e'),
        name='Total Asylum Seekers'
    )
    fig = go.Figure(trace)

    # Highlight migration crisis peaks
    for peak in Peak_finder(timeline):
        fig.add_shape(
            type="rect",
            x0=peak['start'], y0=0, x1=peak['end'], y1=timeline['count'].max(),
            fillcolor="rgba(255, 99, 71, 0.3)",  # Semi-transparent red
            layer="below", line_width=0
        )

    fig.update_traces(
        customdata=extra_hover_text,
        hovertemplate="%{customdata}"
    )

    fig.update_layout(
        title='<b>Total Asylum Seeker Population Over the Years (Highlighted Migration Crisis)</b>',
        title_x=0.5,
        title_font=dict(size=18, color='black'),
        xaxis=dict(
            title="<b>Year</b>",
            showgrid=True,
            gridcolor='lightgrey',
            zeroline=False,
            tickangle=-45
        ),
        yaxis=dict(
            title="<b>Asylum Seekers</b>",
            showgrid=True,
            gridcolor='lightgrey',
            rangemode='tozero'
        ),
        plot_bgcolor='white',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    fig.show()




def Migration_crisis_by_period_Dash():
    app = Dash(__name__)

    migration_crisis = list(Peak_finder(asylum.groupby('year').agg({'count': 'sum'}).reset_index()))
    options = [f"{years['start']}-{years['end']}" for years in migration_crisis]
    app.layout = html.Div([
        html.H2('Migration Crisis Analysis', style={'text-align': 'center', 'color': '#333'}),
        html.H4('Select a migration crisis period:', style={'text-align': 'center', 'font-size': '16px', 'color': '#555'}),
        dcc.Dropdown(
            id="dropdown",
            options=[{'label': option, 'value': option} for option in options],
            value=options[0],
            clearable=False,
            style={'width': '50%', 'margin': '0 auto'}
        ),
        dcc.Graph(id="graph"),
    ], style={'backgroundColor': '#f9f9f9', 'padding': '20px'})

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
                f"Year: {line['year']}<br>"
                f"Total: {line['count']:,}<br>"
                f"Percentage: {(line['count'] / (period_data[period_data['year'] == line['year']]['count'].sum())):.2%}"
                for _, line in data.iterrows()
            ]
            fig.add_trace(
                go.Bar(
                    name=country,
                    x=data['year'],
                    y=data['count'],
                    customdata=custom,
                    hovertemplate="%{customdata}",
                    marker=dict(line=dict(width=0.5, color='black'))
                )
            )

        fig.update_layout(
            barmode='stack',
            title={
                'text': 'Total Asylum Seekers in migration Crisis Period',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333'}
            },
            xaxis={
                'title': {'text': "Years", 'font': {'size': 16, 'color': '#555'}},
                'showgrid': False,
                'tickfont': {'size': 12, 'color': '#555'}
            },
            yaxis={
                'title': {'text': 'Asylum Seekers', 'font': {'size': 16, 'color': '#555'}},
                'showgrid': True,
                'gridcolor': 'lightgrey',
                'tickfont': {'size': 12, 'color': '#555'}
            },
            legend={
                'title': {'text': 'Countries', 'font': {'size': 14, 'color': '#555'}},
                'font': {'size': 12, 'color': '#555'}
            },
            plot_bgcolor='white',
            paper_bgcolor='#f9f9f9',
            margin=dict(l=50, r=50, t=50, b=50)
        )
        return fig

    app.run(port=8052)

def Destination_countries_graph():
    # TODO: add better hover text with the principal countries that migrate to that country
    destination_countries = asylum.groupby("country_of_asylum_abbr").agg({"count":'sum'}).reset_index().sort_values('count', ascending=False)
    country_names = asylum[['country_of_asylum_abbr', 'country_of_asylum_name']]
    country_names = country_names.drop_duplicates(subset=['country_of_asylum_abbr'], keep='first')
    destination_countries = destination_countries.merge(country_names, how='inner', on='country_of_asylum_abbr')
    fig = px.choropleth(destination_countries, locations="country_of_asylum_abbr", locationmode='ISO-3',
                        color="count",
                        color_continuous_scale="Reds",
                        hover_name="country_of_asylum_name",
                        projection="natural earth")

    fig.show()


def Biggest_displacement_percentage_graph():
    data = Get_country_population_df(population, asylum).sort_values('percentage_of_population_migration', ascending=False)
    country_names = asylum[['country_of_origin_abbr', 'country_of_origin_name']].drop_duplicates(subset=['country_of_origin_abbr'], keep='first')

    destination_countries = data.merge(country_names, how='left', on='country_of_origin_abbr')
    destination_countries = destination_countries[:20]

    fig = go.Figure()
    # Filter to show only the year with the highest percentage of population migration for each country
    filtered_data = destination_countries.loc[
        destination_countries.groupby('country_of_origin_name')['percentage_of_population_migration'].idxmax()
    ].sort_values(by='percentage_of_population_migration', ascending=False)

    fig.add_trace(
        go.Bar(
            x=filtered_data['country_of_origin_name'],
            y=filtered_data['percentage_of_population_migration'],
            hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Percentage: %{y:.2f}%<extra></extra>",
            marker=dict(color='#ad0b0b'),
            customdata=filtered_data['year'], 
            text=filtered_data['year'], 
            textposition='outside' 
        )
    )

    fig.update_layout(
        title="<b>Top Countries by Percentage of Population Displaced (Highest Year per Country)</b>",
        xaxis=dict(
            title="<b>Country of Origin</b>",
            tickangle=-45,
            showgrid=False
        ),
        yaxis=dict(
            title="<b>Percentage of Population Displaced</b>",
            showgrid=True,
            gridcolor='lightgrey'
        ),
        plot_bgcolor='white',
        height=600,
        margin=dict(t=50, b=150)
    )

    fig.show()

def Specific_country_information_dash():
    """
        This function creates a Dash app that displays a choropleth map and a line chart of asylum seekers by country.

        Returns:
            None
    """
    app2 = Dash(__name__)

    countries = asylum[['country_of_origin_name', 'count']].groupby('country_of_origin_name').agg({'count': "sum"}).reset_index().sort_values('count', ascending=False)
    options = countries['country_of_origin_name'].unique()
    country_names = asylum[['country_of_origin_abbr', 'country_of_origin_name']]

    app2.layout = html.Div([
        html.H2('Countries', style={'text-align': "center"}),
        html.P('Select country:'),
        dcc.Dropdown(
            id="dropdown",
            options=options,
            value=options[0],
            clearable=False,
        ),
        dcc.Graph(id="line"),
        dcc.Graph(id="graph"),
        
    ], style={'backgroundColor':'white'})

    @app2.callback(
        Output("graph", "figure"),
        Input("dropdown", "value"))

    def update_bar_chart(country):
        country = country_names[country_names['country_of_origin_name'] == country]['country_of_origin_abbr'].values[0]
        final = Get_ready_for_plot_df(asylum, country)
        final_heat = final[final['cumulative_sum'] != 0]

        fig = px.choropleth(final_heat, locations="country", locationmode='ISO-3',
                            color="cumulative_sum",
                            color_continuous_scale="Reds",
                            hover_name="country",
                            animation_frame="year",
                            projection="natural earth")
        country_to_highlight = "USA"
        fig.add_trace(
            go.Choropleth(
                locations=[country],
                z=[1],
                colorscale=[[0, "green"], [1, "green"]],  
                showscale=False,
                hovertemplate="%{location}"
            )
        )

        return fig

    @app2.callback(
        Output("line", "figure"),
        Input("dropdown", "value"))

    def update_line(country):
        country_iso = country_names[country_names['country_of_origin_name'] == country]['country_of_origin_abbr'].values[0]
        timeline = Get_total_country_migration_df(asylum, country_iso)
        trace = go.Scatter(x=timeline['year'], y=timeline['count'])
        fig = go.Figure(trace)

        for peak in Peak_finder(timeline):
            fig.add_shape(type="rect",
                        x0=peak['start'], y0=0, x1=peak['end'], y1=timeline['count'].max(),
                        fillcolor="tomato", opacity=0.5,
                        layer="below", line_width=0)

        fig.update_layout(
            title=f'Total {country} asylum seeker population over the years (highlighted migration crisis)',
            xaxis={'title': {'text': "Years"}, 'showgrid':False},
            yaxis={'title': {'text': 'Asylum Seekers'}, 'rangemode': 'tozero', 'showgrid':False}
        )

        return fig



    app2.run(port=8053)