
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
    mock = pd.read_csv('test\\utils\\mock_data_population.csv')
    data_class = Data()
    data_class.population_data = mock
    result = data_class.Country_population_data('AFG')
    expected_result = pd.read_csv('test\\utils\\result_Country_population_data.csv')
    pd.testing.assert_frame_equal(result, expected_result)

# TODO: same 
def test_get_country_population_df():
    mock = pd.read_csv('test\\utils\\mock_data_population.csv')
    data_class = Data()
    data_class.population_data = mock

    result = data_class.Get_country_population_df()
    
    expected_result = pd.read_csv('test\\utils\\result_Get_country_population_df.csv', index_col=0)
    pd.testing.assert_frame_equal(result, expected_result)