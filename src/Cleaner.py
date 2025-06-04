import pandas as pd

# TODO: create unit test for class cleaner

class Cleaner:
    __output_folder = ".\\Data\\Clean\\"

    @staticmethod
    def __Asylum_data_cleaner(data_path: str) -> pd.DataFrame:
        asylum_raw = pd.read_excel(data_path, sheet_name="DATA")

        # Drop columns not in use
        asylum_dropped_rows = asylum_raw.drop(columns=['origin', 'asylum'])

        # Make data more readable with change of abbreviation
        replacement = {
            'REF' : 'Refugee',
            'ASY' : 'Asylum-seekers',
            'ROC' : 'People in refugee-like situation',
            'OIP' : 'Other people in need of international protection'
        }
        asylum_name_changed = asylum_dropped_rows.replace({"PT": replacement})

        # Make column names more readable
        new_column_names = {
            "OriginISO" : "country_of_origin_abbr",
            "OriginName" : "country_of_origin_name",
            "AsylumISO" : "country_of_asylum_abbr",
            "AsylumName" : "country_of_asylum_name",
            "AsylumRegion" : "region_of_asylum",
            "PT" : "category",
            "Year" : "year",
            "Count" : "count"
        }
        asylum_clean = asylum_name_changed.rename(columns=new_column_names)

        rows_to_delete = asylum_clean[asylum_clean['country_of_origin_abbr'].isin(['TIB'])].index
        asylum_clean = asylum_clean.drop(rows_to_delete)
        # Delete 'Not classified' is empty
        # fix West Bank and Gaza problem

        return asylum_clean
    
    @staticmethod
    def __Clean_Population_Data(data_path: str) -> pd.DataFrame:
        data = pd.read_csv(data_path, skiprows=4)

        columns_to_drop = ["Indicator Name", "Indicator Code", 'Unnamed: 68']
        data_new = data.drop(columns=columns_to_drop)

        # Not classified has no data, west bank and gaza has to be analyzed by itself
        rows_to_delete = data_new[data_new['Country Name'].isin(['West Bank and Gaza', 'Not classified'])].index
        data_nn = data_new.drop(rows_to_delete)

        return data_nn
    
    @staticmethod
    def Output_asylum_seekers_clean_data(self, source_path: str) -> None:
        clean_data_asylum = self.__Asylum_data_cleaner(source_path)
        clean_data_asylum.to_csv(f"{self.__output_folder}Asylum_data.csv", index=False)

    @staticmethod
    def Output_population_clean_data(self, source_path: str) -> None:
        clean_data_population = self.__Clean_Population_Data(source_path)
        clean_data_population.to_csv(f"{self.__output_folder}Population_data.csv", index=False)