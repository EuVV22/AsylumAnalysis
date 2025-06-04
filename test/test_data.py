
from src.Data import Data


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
    d = Data()
    result = list(d.Peak_finder(mock))
    assert result == expected_results