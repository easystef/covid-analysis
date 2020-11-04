# TODO module documentation

import argparse
from bokeh.layouts import layout
from bokeh.models import HoverTool, NumeralTickFormatter
from bokeh.models.annotations import Span
from bokeh.palettes import Category10
from bokeh.plotting import figure, output_file, show
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

    # BOKEH ----------------------------

    # output to static HTML file
    output_file("output/lines.html")

    colours = Category10[max(len(countries), 3)]  # Category10 does not work with an input of <3
    if len(countries) > len(colours):
        raise ValueError(f"The maximum number of countries which can be plotted is {len(colours)}")

    # 1. Create the figures

    # Graph 1
    hover1 = HoverTool(tooltips=[('date', '$x{%F}'), ('cases', '$y{0,0}k')], formatters={'$x': 'datetime'})
    p1 = figure(width=1200, height=400, title="Active cases", tools=[hover1], x_axis_type="datetime",
                x_axis_label='date', y_axis_label="thousands of cases")
    p1.xaxis.formatter.months = '%b-%y'

    # Graph 2
    hover2 = HoverTool(tooltips=[('date', '$x{%F}'), ('cases', '$y{0,0}')], formatters={'$x': 'datetime'})
    p2 = figure(width=600, height=400, title="Cases in previous week per 100k people", tools=[hover2],
                x_axis_type="datetime", x_axis_label='date', y_axis_label='cases')
    p2.xaxis.formatter.days = '%d-%b'

    # Graph 3
    hover3 = HoverTool(tooltips=[('date', '$x{%F}'), ('r-number', '$y')], formatters={'$x': 'datetime'})
    p3 = figure(width=600, height=400, title="R-Number", tools=[hover3], x_axis_type="datetime", x_axis_label='date',
                y_axis_label='r-number')
    p3.xaxis.formatter.days = '%d-%b'

    # 2. Create glyphs

    for i, country in enumerate(countries):
        my_country = Country(data, country)

        s1 = my_country.active_cases() / 1000
        p1.line(s1.index, s1.values, legend_label=country, line_width=2, line_color=colours[i])

        s2 = my_country.cases_by_population()[-60:]
        p2.line(s2.index, s2.values, legend_label=country, line_width=2, line_color=colours[i])
        
        s3 = my_country.r_number(4, 7)[-60:]
        p3.line(s3.index, s3.values, legend_label=country, line_width=2, line_color=colours[i])

    for p in [p1, p2, p3]:
        p.legend.location = 'top_left'

    r_one = Span(location=1, dimension='width', line_color='maroon', line_width=2)
    p3.add_layout(r_one)

    # 3. Show the results
    show(layout([
        [p1],
        [p2, p3]
    ]))


if __name__ == '__main__':
    main()
