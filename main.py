# TODO module documentation

import argparse
import matplotlib.pyplot as plt
import pandas as pd

ECDC_DATA_URL = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'


def import_ecdc_data():
    """Read data for ECDC

    Loads the data and formats the dates

    :return: pandas.DataFrame
        Containing the data from ECDC
    """

    ecdc_data = pd.read_csv(ECDC_DATA_URL, encoding='utf_8')
    ecdc_data['dateRep'] = pd.to_datetime(ecdc_data['dateRep'], format='%d/%m/%Y')

    return ecdc_data


class Country:
    # TODO class documentation

    def __init__(self, covid_data, country_name):

        # Prepare data
        country_data = covid_data[covid_data['countriesAndTerritories'] == country_name]
        country_data.set_index('dateRep', inplace=True)

        self.cases = country_data['cases'].sort_index()
        self.deaths = country_data['deaths'].sort_index()
        self.population = country_data['popData2019'][0]

    def r_number(self, lag=1, n_days=1):
        """Calculates a simple version of the R-number - the number of additional people infected by each infected
        individual.

        It is calculated as the ratio of the total number of infected people over a specified period, divided by the
        number of people infected over a period of the same length of time in an earlier period.

        :param lag: integer, default 1
            The number of days between the two periods in which the infection rate is being measured.
        :param n_days: integer, default 1
            The length of the period over which the number of infections is being counted for the two periods.
        :return: pandas.Series
            Containing the resulting R-number
        """

        x = self.cases.rolling(n_days).sum()
        x_lag = x.shift(lag)

        return x / x_lag

    def active_cases(self, recovery_days=14):
        """Calculates the number of active cases at any given point in time.

        For simplicity, it is assumed that people all recover after the same fixed number of days. Two weeks, by
        default.

        :param recovery_days: integer, default 14
            The number of days a newly infected person is assumed to be sick.
        :return: pandas.Series
            Containing the resulting number of active cases each day
        """

        return self.cases.rolling(recovery_days).sum()

    def cases_by_population(self):
        """The number of cases over the last 7 days per 100k people.

        :return: pandas.Series
            Resulting number of cases
        """

        return self.cases.rolling(7).sum() / (self.population / 100000)


def main():
    """Generates graphs showing different aspects of the COVID-19 data.

    :return: None
    """

    parser = argparse.ArgumentParser(description="Generate graphs based on COVID-19 data from ECDC")
    parser.add_argument('countries', type=str, help="Countries for which graph's should be created", nargs='+')

    args = parser.parse_args()

    countries = tuple(args.countries)

    data = import_ecdc_data()

    # Cases in previous week per 100k people
    for country in countries:
        my_country = Country(data, country)
        my_country.cases_by_population().plot(label=country)

    plt.title('Cases in previous week per 100k people')
    plt.legend()
    plt.show()

    # Active cases
    for country in countries:
        my_country = Country(data, country)
        my_country.active_cases().plot(label=country)

    plt.title('Active cases')
    plt.legend()
    plt.show()

    # R-Number
    for country in countries:
        my_country = Country(data, country)
        my_country.r_number(4, 7)[-100:].plot(label=country)

    plt.title('R-Number')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
