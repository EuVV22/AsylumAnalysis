from operator import index
from unittest import result
from webbrowser import get
from src.Data import Data
import pandas as pd



def test_Peak_finder():
    expected_results = []
    cases_df = []

    # Peak expected result {'start': 1990, 'end': 1992}
    peak_df = pd.DataFrame( {
            'year': [1990, 1991, 1992],
            'count': [5_000, 150_000, 60_000]
        })
    expected_results.append({'start': 1990, 'end': 1992})
    cases_df.append(peak_df)
    
    # No peak expected results: nothing

    no_peak_df = pd.DataFrame( {
            'year': [1993, 1994, 1995],
            'count': [60_000, 65_000, 70_000]
        })
    cases_df.append(no_peak_df)
    
    # Elongated peak expected result {'start': 1996, 'end': 1999}
    elongated_peak_df = pd.DataFrame( {
        'year': [1996, 1997, 1998, 1999],
        'count': [70_000, 110_000, 110_000, 90_000]
    })
    expected_results.append({'start': 1996, 'end': 1999})
    cases_df.append(elongated_peak_df)

    mock = pd.concat(cases_df, ignore_index=True)
    data = Data()
    result = list(data.Peak_finder(mock))
    assert result == expected_results

def test_top_origin_countries_yearly():
    mock = pd.read_csv('test\\utils\\mock_data_for_top_countries.csv')
    data_class = Data()
    data_class.asylum_data = mock
    result = data_class.top_origin_countries_yearly(1975, 1980)
    expected_result = pd.read_csv('test\\utils\\results_for_top_origin_countries_yearly.csv')
    pd.testing.assert_frame_equal(result, expected_result)

# TODO: make test\\utils\\mock_data_population.csv smaller and change the desire outputs
def test_Country_population_data():
    mock = pd.read_csv('test\\utils\\mock_data_population.csv', index_col=0)
    data_class = Data()
    data_class.population_data = mock
    result = data_class.Country_population_data('AFG')
    expected_result = pd.read_csv('test\\utils\\result_Country_population_data.csv', index_col=0)
    pd.testing.assert_frame_equal(result, expected_result)

# TODO: same 
def test_get_country_population_df():
    mock = pd.read_csv('test\\utils\\mock_data_population.csv', index_col=0)
    data_class = Data()
    data_class.population_data = mock

    result = data_class.Get_country_population_df()
    
    expected_result = pd.read_csv('test\\utils\\result_Get_country_population_df.csv', index_col=0)
    pd.testing.assert_frame_equal(result, expected_result)

def Get_mock_data() -> pd.DataFrame:
    return pd.DataFrame([
        {'country_of_origin_abbr' : 'TGO', 'country_of_origin_name' : 'Togo', 'country_of_asylum_abbr' : 'CHE', 
        'country_of_asylum_name' : 'Switzerland', 'region_of_asylum' : 'Europe', 'category': 'Asylum-seekers', 'year': '1989', 'count': '7'},

        {'country_of_origin_abbr' : 'MUS', 'country_of_origin_name' : 'Mauritius', 'country_of_asylum_abbr' : 'GBR', 
        'country_of_asylum_name' : 'United Kingdom', 'region_of_asylum' : 'Europe', 'category': 'Asylum-seekers', 'year': '2017', 'count': '10'},

        {'country_of_origin_abbr' : 'KEN', 'country_of_origin_name' : 'Kenya', 'country_of_asylum_abbr' : 'GBR', 
        'country_of_asylum_name' : 'United Kingdom', 'region_of_asylum' : 'Europe', 'category': 'Asylum-seekers', 'year': '1996', 'count': '1170'}
    ])

def test_Get_destination_by_year():
    mock_data = Get_mock_data()

    data_class = Data()
    data_class.asylum_data = pd.DataFrame(mock_data)

    result = data_class.Get_destination_by_year('KEN')

    expected_result = pd.DataFrame({'year': ['1996'], 'country_of_asylum_abbr': ['GBR'], 'count': ['1170'], 'merge_column': ['GBR1996']})
    
    pd.testing.assert_frame_equal(result, expected_result)

def test_Get_countries_and_years_df():
    mock_data = Get_mock_data()

    result = Data.Get_countries_and_years_df(mock_data)

    expected_result = pd.DataFrame([{'country': 'CHE', 'year': '1989', 'merge_column': 'CHE1989'},
                                    {'country': 'CHE', 'year': '2017', 'merge_column': 'CHE2017'},
                                    {'country': 'CHE', 'year': '1996', 'merge_column': 'CHE1996'},
                                    {'country': 'GBR', 'year': '1989', 'merge_column': 'GBR1989'},
                                    {'country': 'GBR', 'year': '2017', 'merge_column': 'GBR2017'},
                                    {'country': 'GBR', 'year': '1996', 'merge_column': 'GBR1996'}])

    pd.testing.assert_frame_equal(result, expected_result)

def test_Merge_and_clean_df():
    data_class = Data()
    data_class.asylum_data = Get_mock_data()

    destination = data_class.Get_destination_by_year('KEN')
    years = data_class.Get_countries_and_years_df(destination)
    result = data_class.Merge_and_clean_df(destination, years)

    expected_result = pd.DataFrame([{'country': 'GBR', 'year': '1996', 'count': 1170, 'cumulative_sum': 1170}])

    pd.testing.assert_frame_equal(result, expected_result)


def test_Get_ready_for_plot_df():
    data_class = Data()
    data_class.asylum_data = Get_mock_data()
    result = data_class.Get_ready_for_plot_df('KEN')

    expected_result = pd.DataFrame([{'country': 'GBR', 'year': '1996', 'count': 1170, 'cumulative_sum': 1170, 'country_name': 'United Kingdom', 'hover_text': 'United Kingdom: 1170'}])

    pd.testing.assert_frame_equal(result, expected_result)

