import pandas as pd

class Data:
    def __init__(self):
        self.asylum_data = pd.read_csv('.\\Data\\Clean\\Asylum_data.csv')
        self.population_data = pd.read_csv(".\\Data\\Clean\\Population_data.csv")

        self.abbr_dict = {
                            row["country_of_origin_abbr"]: row["country_of_origin_name"]
                            for index, row in self.asylum_data[['country_of_origin_abbr', 'country_of_origin_name']].drop_duplicates(subset=['country_of_origin_abbr'], keep='first').iterrows()
        }
        # adding two names only appeared in destinations
        self.abbr_dict['SXM'] = 'Sint Maarten (Dutch part)'
        self.abbr_dict['ABW'] = 'Aruba'
        # making names more appealing for display
        self.abbr_dict['VEN'] = 'Venezuela'
        self.abbr_dict['UKN'] = 'Unknown'
        self.abbr_dict['SRB'] = 'Serbia and Kosovo'
        self.abbr_dict['TZA'] = 'Tanzania'
        self.abbr_dict['BOL'] = 'Bolivia'
        self.abbr_dict['NLD'] = 'Netherlands'
        self.abbr_dict['FSM'] = 'Micronesia'




    @staticmethod
    def Peak_finder(data: pd.DataFrame):
        MINIMUN_CONSIDERATION_VALUE = 1_000
        CRISIS_INCREMENT_ALERT = 0.5 # Increments higher than this % are consider crisis
        previous_value = data['count'][0]
        previous_year = data['year'][0]

        inside_peak = False
        current_highlight = {}
        # Start of the highlight:
        for index, row in data.iterrows():
            if not inside_peak:
                if previous_value > MINIMUN_CONSIDERATION_VALUE: 
                    if (row['count'] - previous_value) > (previous_value * CRISIS_INCREMENT_ALERT):
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


    def only_the_top_for_year(self, start_year: int, end_year: int) -> pd.DataFrame:
        """
            Compares the all the countries and change the name of the country to 'Other' if its less than the constant minimum value 

            Args:
                df (pandas.DataFrame): the DataFrame to work on

            Returns:
                pandas.DataFrame with the values changed.
        """
        MINIMUN_PARTICIPATION = 0.05
        df = self.asylum_data[(start_year <= self.asylum_data['year']) & (self.asylum_data['year'] <= end_year)]

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

    def Country_population_data(self, country_code: str) -> pd.DataFrame:
        country_population = self.population_data[self.population_data["Country Code"] == country_code].drop(columns=["Country Name", "Country Code"]).transpose().reset_index()
        country_population.columns = ['year', 'population']
        country_population['year'] = country_population['year'].astype(int)

        country = self.asylum_data[self.asylum_data["country_of_origin_abbr"] == country_code].groupby("year", as_index=False)["count"].sum()
        
        country = country.merge(right= country_population, how='left', on='year')
        country.drop(country[country['population'].isna()].index, inplace=True)
        country["percentage_of_population_migration"] = (country["count"] / country["population"]) * 100

        country.rename(columns={'count': "displaced"}, inplace=True)
        country["country_of_origin_abbr"] = country_code
        return country

    def Get_country_population_df(self) -> pd.DataFrame:
        countries = self.asylum_data["country_of_origin_abbr"].unique()
        countries_not_in_the_analysis = []
        full_data = pd.DataFrame()
        for country in countries:
            if country in self.population_data['Country Code'].values:
                full_data = pd.concat([full_data, self.Country_population_data(country)])
            else:
                # countries not in the asylum DF
                countries_not_in_the_analysis.append(self.asylum_data[self.asylum_data['country_of_origin_abbr'] == country]['country_of_origin_name'].iloc[0])
        return full_data

    def Get_Destination_by_year_df(self, country_abbr: str) -> pd.DataFrame:
        result = self.asylum_data[self.asylum_data['country_of_origin_abbr'] == country_abbr]
        result = result.groupby(['year', 'country_of_asylum_abbr']).agg({'count' : 'sum'}).reset_index()
        result['merge_column'] = result['country_of_asylum_abbr'] + result['year'].astype(str)
        return result

    @staticmethod
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
    @staticmethod
    def Merge_and_clean_df(destination_df: pd.DataFrame, years_df: pd.DataFrame) -> pd.DataFrame:
        final = years_df.merge(destination_df, on='merge_column', how='left')
        final[final['year_x'] != final['year_y']]
        final = final.drop(columns=['year_y', 'merge_column', 'country_of_asylum_abbr'])
        final = final.rename(columns={'year_x': 'year'})
        final['count'] = final['count'].fillna(0)
        final['cumulative_sum'] = final.groupby('country')['count'].cumsum()
        return final

    def Get_ready_for_plot_df(self, country_of_origin_abbr: str) -> pd.DataFrame:
        destination = self.Get_Destination_by_year_df(country_of_origin_abbr)
        yearly = self.Get_countries_and_years_df(destination)
        return self.Merge_and_clean_df(destination, yearly)    
    
    # Same but different
    @staticmethod
    def Get_df_with_a_year_per_country(df: pd.DataFrame) -> pd.DataFrame:
        countries = df['country'].unique()
        years = df['year'].unique()
        result = pd.DataFrame(columns=["country", "year"])
        for country in countries:
            c_list = [country] * len(years)
            country_list_df = pd.DataFrame({"country" : c_list, "year" : years})
            result = pd.concat([result, country_list_df], ignore_index=True)
        return result
    
    def Add_hover_text(self, df: pd.DataFrame, type: str) -> pd.DataFrame:
        if type == 'origin':
            COLUMN_NAME = 'country_of_asylum_name'
            result_countries = 'destination'
            TOTAL_DESCRIPTION = 'Displaced population:'
        else:
            COLUMN_NAME = 'country_of_origin_name'
            result_countries = 'origin'
            TOTAL_DESCRIPTION = 'Asylum seekers received:'
        r = df
        result = pd.DataFrame({'hover_text': []})
        for row in r.itertuples(): # TODO: try writing this in vectorization to be more efficient
            country = row.country # country of destionation or origin
            # gets all the times that country has been use as origin or destination
            specific_type_df = self.asylum_data[self.asylum_data['country_of_' + type + '_abbr'] == country]
            specific_type_df = specific_type_df[specific_type_df['year'] <= row.year] # selects the year as the maximun year
            specific_type_df = specific_type_df.groupby([COLUMN_NAME]).agg({'count': 'sum'}).reset_index() # sums all the users
            specific_type_df = specific_type_df.sort_values('count', ascending=False)# this first part can be precomputed before the loop starts

            hover_text = f'''<b>{self.abbr_dict[country]}<br>{TOTAL_DESCRIPTION} {int(row.cumulative_sum):,}<br><br>Top {result_countries} countries:</b><br>'''
            MAX_DISPLAY_COUNTRIES = 5
            number_of_countries_to_display =  MAX_DISPLAY_COUNTRIES if len(specific_type_df) >= MAX_DISPLAY_COUNTRIES else len(specific_type_df)
            i = 0
            while i < number_of_countries_to_display:
                hover_text += f'{specific_type_df.iloc[i][COLUMN_NAME]}: {specific_type_df.iloc[i]['count']:,}<br>'
                i += 1
            result.loc[row[0]] = [hover_text]    
        return result    

    def Destionation_or_origin_by_year(self, type: str) -> pd.DataFrame:
        # prepares data
        TARGET_TYPE_COLUNM = 'country_of_' + type +'_abbr'
        df_with_total_by_year = self.asylum_data.groupby(['year', TARGET_TYPE_COLUNM]).agg({'count' : 'sum'}).reset_index()
        df_with_total_by_year.rename(columns={TARGET_TYPE_COLUNM: 'country'}, inplace=True)
        # Generate dataframe with every year for every country
        one_year_for_each_country_df = self.Get_df_with_a_year_per_country(df_with_total_by_year)
        # Merge the two dataframes
        cumutalive_data = one_year_for_each_country_df.merge(df_with_total_by_year, on=['country', 'year'], how='left')
        cumutalive_data['count'] = cumutalive_data['count'].fillna(0)
        cumutalive_data['cumulative_sum'] = cumutalive_data.groupby('country')['count'].cumsum()
        cumutalive_data = cumutalive_data[cumutalive_data['cumulative_sum'] != 0]
        cumutalive_data = cumutalive_data.join(self.Add_hover_text(cumutalive_data, type))

        return cumutalive_data
    ## /

    def Get_total_country_migration_df(self, country_of_origin_abbr: str) -> pd.DataFrame:
        return self.asylum_data[self.asylum_data['country_of_origin_abbr'] == country_of_origin_abbr].groupby('year').agg({'count' : 'sum'}).reset_index()

    def Get_origin_country_total(self) -> pd.DataFrame:
        return  self.asylum_data.groupby('country_of_origin_name').agg({'count': 'sum'}).sort_values('count', ascending=True).reset_index()
    
    def Get_year_timeline(self) -> pd.DataFrame:
        return self.asylum_data.groupby('year').agg({'count': 'sum'}).reset_index()

    def Get_grouped_by_year_countries_total_origin(self):
        # "By default the group keys are sorted during the groupby operation." Pandas docs https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html
        origin_country_total_by_year = self.asylum_data.groupby(['country_of_origin_name', 'year']).agg({'count': 'sum'})
        origin_country_total_by_year = origin_country_total_by_year.reset_index().sort_values('count', ascending=False)
        grouped_by_year = origin_country_total_by_year.groupby('year')
        return grouped_by_year
    
    def Get_destination_countries(self) -> pd.DataFrame:
        destination_countries = self.asylum_data.groupby("country_of_asylum_abbr").agg({"count":'sum'}).reset_index().sort_values('count', ascending=False)
        country_names = self.asylum_data[['country_of_asylum_abbr', 'country_of_asylum_name']]
        country_names = country_names.drop_duplicates(subset=['country_of_asylum_abbr'], keep='first')
        destination_countries = destination_countries.merge(country_names, how='inner', on='country_of_asylum_abbr')
        return destination_countries
    
    def Get_biggest_population_displacement_df(self) -> pd.DataFrame:
        AMOUNT_OF_COUNTRIES = 20
        data = self.Get_country_population_df().sort_values('percentage_of_population_migration', ascending=False)
        country_names = self.asylum_data[['country_of_origin_abbr', 'country_of_origin_name']].drop_duplicates(subset=['country_of_origin_abbr'], keep='first')
        destination_countries = data.merge(country_names, how='left', on='country_of_origin_abbr')
        destination_countries = destination_countries[:AMOUNT_OF_COUNTRIES]
        # Filter to show only the year with the highest percentage of population migration for each country
        filtered_data = destination_countries.loc[
            destination_countries.groupby('country_of_origin_name')['percentage_of_population_migration'].idxmax()
        ].sort_values(by='percentage_of_population_migration', ascending=False)
        return filtered_data