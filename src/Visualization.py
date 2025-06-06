import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output
from .Data import Data as data_class

class Visualization:
    __data = data_class()

    def print_total_asylum_seekers(self):
        """
            Prints the total sum of all asylum seekers
        """
        print(format(self.__data.asylum_data['count'].sum(), ",d"))

    def Country_of_origin(self) -> go.Figure:
        """
            Displays a horizontal bar graphs showing the total number of asylum seekers by country of origin

            Return: Plotly figure
        """
        MINIMUM_ASYLUM_SEEKERS = 100_000
        as_by_country = self.__data.Get_origin_country_total()
        as_by_country = as_by_country[as_by_country['count'] > MINIMUM_ASYLUM_SEEKERS]
        
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
        return fig

    def Asylum_seekers_timeline(self) -> go.Figure:
        # Create timeline plot
        timeline_data = self.__data.Get_year_timeline()
        trace = go.Scatter(
            x=timeline_data['year'], 
            y=timeline_data['count'],
            mode='lines+markers',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6, color='#ff7f0e'),
            name='Total Asylum Seekers'
        )
        fig = go.Figure(trace)

        DATA_CLASS = self.__data

        # Highlight migration crisis peaks
        for peak in DATA_CLASS.Peak_finder(timeline_data):
            fig.add_shape(
                type="rect",
                x0=peak['start'], y0=0, x1=peak['end'], y1=timeline_data['count'].max(),
                fillcolor="rgba(255, 99, 71, 0.3)",  # Semi-transparent red
                layer="below", line_width=0
            )

        # This extra hover text can be separated into a function a check for countries with less than 3 rows
        
        # Add hover text
        extra_hover_text = [
                f"<b>Year: {year}<br>" +
                f"Total: {countries['count'].sum():,}<br><br>" +
                f"Top three origin countries:</b><br>" +
                f"{countries.iloc[0]['country_of_origin_name']}: {countries.iloc[0]['count']:,}<br>" +
                f"{countries.iloc[1]['country_of_origin_name']}: {countries.iloc[1]['count']:,}<br>" +
                f"{countries.iloc[2]['country_of_origin_name']}: {countries.iloc[2]['count']:,}<br>" +
                f"Other: {countries[3:]['count'].sum():,}"
            for year, countries in self.__data.Get_grouped_by_year_countries_total_origin()
            ]
        
        fig.update_traces(
            customdata=extra_hover_text,
            hovertemplate="%{customdata}"
        )

        fig.update_layout(
            title='<b>Asylum Seeker Population Over the Years (Migration Crises Highlighted)</b>',
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
        # fig.update_layout(width=1500, height=600,)
        fig.update_xaxes(range=[1960, 2025])
        return fig

    def Destination_countries_graph(self) -> go.Figure:
        # TODO: add better hover text with the principal countries that migrate to that country
        destination_countries = self.__data.Get_destination_countries()

        fig = px.choropleth(destination_countries, locations="country_of_asylum_abbr", locationmode='ISO-3',
                            color="count",
                            color_continuous_scale="Reds",
                            hover_name="country_of_asylum_name",
                            projection="natural earth")
        return fig 


    def Biggest_displacement_percentage_graph(self) -> go.Figure:
        destination_countries = self.__data.Get_biggest_population_displacement_df() 
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=destination_countries['country_of_origin_abbr'],
                y=destination_countries['percentage_of_population_migration'],
                hovertemplate="<b>%{x}</b><br>Year: %{customdata}<br>Percentage: %{y:.2f}%<extra></extra>",
                marker=dict(color='#ad0b0b'),
                customdata=destination_countries['year'], 
                text=destination_countries['year'], 
                textposition='outside' 
            )
        )

        fig.update_layout(
            title="<b>Top Countries by Percentage of Population Displaced</b>",
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

        return fig

    def Migration_crisis_by_period_Dash(self) -> Dash:
        """
            Creates and displays a Dash dashboard of bar graphs showing the years and countries participating in that year migration,
            dashboard has a selector for each one of the migration crisis.
            Uses port 8052

            Return: Dash app.
        """

        app = Dash(__name__)

        migration_crisis = list(self.__data.Peak_finder(self.__data.asylum_data.groupby('year').agg({'count': 'sum'}).reset_index()))
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
            period_data = self.__data.top_origin_countries_yearly(int(years[0]), int(years[1])).sort_values('count')
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

        return app

    def Specific_country_information_dash(self) -> Dash:
        """
            This function creates a Dash app that displays a choropleth map and a line chart of asylum seekers by country.

            Returns: Dash app
        """
        app2 = Dash(__name__)

        countries = self.__data.Get_origin_country_total().sort_values('count', ascending=False)
        options = countries['country_of_origin_name'].unique()
        country_names = self.__data.asylum_data[['country_of_origin_abbr', 'country_of_origin_name']]

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
            name = country
            country = country_names[country_names['country_of_origin_name'] == country]['country_of_origin_abbr'].values[0]
            final = self.__data.Get_ready_for_plot_df(country)
            final_heat = final[final['cumulative_sum'] != 0]

            fig = px.choropleth(final_heat, locations="country", locationmode='ISO-3',
                                color="cumulative_sum",
                                color_continuous_scale="Blues",
                                hover_name="country",
                                animation_frame="year",
                                projection="natural earth")
            country_to_highlight = "USA"

            fig.add_trace(
                go.Choropleth(
                    locations=[country],
                    z=[1],
                    colorscale=[[0, "red"], [1, "red"]],  
                    showscale=False,
                    hovertemplate="%{location}"
                )
            )
            fig.update_layout(
                title=f'<b>Destination Countries of Asylum Seekers Originating from {name}<b>',
                title_x=0.5,
                title_font=dict(size=18, color='black'),
                
                coloraxis_colorbar=dict(
                    title="Asylum seekers"
                )
            )
            fig.update_layout(
                geo={'landcolor' : "#FFFFFF"}
            )

            return fig

        @app2.callback(
            Output("line", "figure"),
            Input("dropdown", "value"))
        ## TODO: test leaving the max and min consistent
        def update_line(country):
            country_iso = country_names[country_names['country_of_origin_name'] == country]['country_of_origin_abbr'].values[0]
            timeline = self.__data.Get_total_country_migration_df(country_iso)
            trace = go.Scatter(x=timeline['year'], y=timeline['count'], mode='lines+markers',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=6, color='#ff7f0e'),
            name='Total Asylum Seekers')

            fig = go.Figure(trace)

            for peak in self.__data.Peak_finder(timeline):
                fig.add_shape(type="rect",
                            x0=peak['start'], y0=0, x1=peak['end'], y1=timeline['count'].max(),
                            fillcolor="tomato", opacity=0.5,
                            layer="below", line_width=0)

            fig.update_layout(
                title=f'<b>Total Asylum Seekers from {country} by Year (Highlighted Migration crisis)<b>',
                xaxis={'title': {'text': "Years"}, 'showgrid':False},
                yaxis={'title': {'text': 'Asylum Seekers'}, 'rangemode': 'tozero', 'showgrid':False}
            )
            fig.update_layout(
                title_x=0.5,
                title_font=dict(size=18, color='black'),
                xaxis=dict(
                    title="<b>Year</b>",
                    showgrid=True,
                    gridcolor='lightgrey',
                    zeroline=False,
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
            )

            return fig


        return app2
    
    # Dual choroplet map
    @staticmethod
    def create_slider(dates):
        return {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 17},
                'prefix': 'Date: ',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 100, 'easing': 'cubic-in-out'}, # 300
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': -0.1,
            'steps': [{
                'args': [[date], {'frame': {'duration': 300, 'redraw': True}, 'mode': 'immediate'}],
                'label': date,
                'method': 'animate'
            } for date in dates]
        }

    @staticmethod
    def create_play_pause_buttons():
        return {
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 500, 'redraw': True}, 'fromcurrent': True}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': True,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }
    
    def Create_plots(self, data: pd.DataFrame, color_scale: str, showscale: bool = True) -> go.Figure:
        if color_scale == 'Reds': # blue is the color used for the origin plot
            ca = 'coloraxis1'
            type = 'origin'
        else:
            type = 'asylum'
            ca = 'coloraxis2'

        fig = go.Choropleth(
            locations=data['country'],
            locationmode='ISO-3',
            z=data['cumulative_sum'],
            customdata=data['hover_text'],
            hovertemplate="%{customdata}",
            colorscale=color_scale,
            colorbar=dict(title='Population') if showscale else None,
            marker_line_width=0,
            showscale=showscale,
            coloraxis=ca
        )
        return fig

    def Create_Frames(self, origin_data: pd.DataFrame, destination_data: pd.DataFrame) -> list:
        frames = []
        dates = sorted(set(origin_data['year'].unique()))
        for date in dates:
            origin = origin_data[origin_data['year'] == date]
            destination = destination_data[destination_data['year'] == date]

            frames.append(go.Frame(
                data=[
                    self.Create_plots(origin, "Reds", showscale=False),
                    self.Create_plots(destination, "Blues", showscale=False)
                ],
                name=str(date)
            ))
        return frames


    def Get_origin_and_destination_graphs(self):
        origin_df = self.__data.Destination_or_origin_by_year('origin')
        destination_df = self.__data.Destination_or_origin_by_year('asylum')

        fig = make_subplots(rows=1, cols=2, subplot_titles=('<b>Countries of origin</b>', '<b>Countries of destination</b>'),
                            specs=[[{'type': 'choropleth'}, {'type': 'choropleth'}]], horizontal_spacing=0.01)

        # Initial traces
        initial_year = origin_df['year'].min()
        fig.add_trace(self.Create_plots(origin_df[origin_df['year'] == initial_year], "Reds", showscale=True), row=1, col=1)
        fig.add_trace(self.Create_plots(destination_df[destination_df['year'] == initial_year], "Blues", showscale=True), row=1, col=2)

        frames = self.Create_Frames(origin_df, destination_df)
        fig.frames = frames

        slider = self.create_slider(sorted(set(origin_df['year'].unique().astype(str))))
        buttons = self.create_play_pause_buttons()
        
        fig.update_layout(
            sliders=[slider],
            updatemenus=[buttons],
            geo=dict(
                showframe=True,
                showcoastlines=False,
                projection_type='natural earth',
                showcountries=True
            ),
            margin=dict(l=0, r=0, b=0, t=50),
            width=1900,
            height=1000,
        )
        fig.update_geos(
            showframe=True,
            showcoastlines=False,
            projection_type='natural earth',
            showcountries=True
        )

        # Hide the colorbar for the second choropleth trace
        fig.data[1].update(showscale=False)
        fig.data[0].update(showscale=True)

        # Fixing title positions
        fig['layout']['annotations'][0]['y'] = 1.05
        fig['layout']['annotations'][1]['y'] = 1.05

        # Make the figure take up the whole window
        fig.layout.width = None
        fig.layout.height = None
        fig.update_layout(
            coloraxis1=dict(colorscale='Reds', colorbar_x=-0.017),
            coloraxis2=dict(colorscale='Blues', colorbar_x=0.95) #1.0075
        )
        return fig