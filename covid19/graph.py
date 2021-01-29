# TODO module documentation

from bokeh.layouts import layout
from bokeh.models import HoverTool
from bokeh.models.annotations import Span
from bokeh.palettes import Category10
from bokeh.plotting import figure, output_file, show
import pandas as pd

OWID_DATA_URL = 'https://covid.ourworldindata.org/data/owid-covid-data.csv'


def import_owid_data():
    """Reads coronavirus data for Our World In Data

    Loads the data and formats the dates

    :return: pandas.DataFrame
        Containing the data from Our World In Data
    """

    owid_data = pd.read_csv(OWID_DATA_URL, encoding='utf_8')
    owid_data['date'] = pd.to_datetime(owid_data['date'], format='%Y-%m-%d')

    return owid_data


class Country:
    # TODO class documentation

    def __init__(self, covid_data, country_name):

        # Prepare data
        country_data = covid_data[covid_data['location'] == country_name]
        country_data.set_index('date', drop=False, inplace=True)

        self.date = country_data['date'].sort_index()
        self.cases = country_data['new_cases'].sort_index()
        self.deaths = country_data['new_deaths'].sort_index()
        self.vaccinations = country_data['total_vaccinations_per_hundred'].interpolate(method='linear').sort_index()
        self.population = country_data['population'][0]

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

    @property
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

    @property
    def cases_by_population(self):
        """The number of cases over the last 7 days per 100k people.

        :return: pandas.Series
            Resulting number of cases
        """

        return self.cases.rolling(7).sum() / (self.population / 100000)

    @property
    def deaths_by_population(self):
        """The number of cases over the last 7 days per 100k people.

        :return: pandas.Series
            Resulting number of deaths
        """

        return self.deaths.rolling(7).sum() / (self.population / 100000)


def make_graphs(data, countries, file_name):
    """
    # TODO write documentation
    :param data:
    :param countries:
    :param file_name:
    :return:
    """

    # BOKEH ----------------------------

    # output to static HTML file
    output_file(file_name)

    colours = Category10[max(len(countries), 3)]  # Category10 does not work with an input of <3
    if len(countries) > len(colours):
        raise ValueError(f"The maximum number of countries which can be plotted is {len(colours)}")

    # 1. Create the figures

    # Graph 1 - Active cases
    hover1 = HoverTool(tooltips=[('country', '$name'), ('date', '$x{%F}'), ('cases', '$y{0,0}k')],
                       formatters={'$x': 'datetime'})
    p1 = figure(width=1200, height=300, title="Active cases", tools=[hover1], x_axis_type="datetime",
                x_axis_label='date', y_axis_label="thousands of cases")
    p1.xaxis.formatter.months = '%b-%y'
    p1.y_range.start = 0

    # Graph 2 - Cases in previous week per 100k people
    hover2 = HoverTool(tooltips=[('country', '$name'), ('date', '$x{%F}'), ('cases', '$y{0,0}')],
                       formatters={'$x': 'datetime'})
    p2 = figure(width=600, height=300, title="Cases in previous week per 100k people", tools=[hover2],
                x_axis_type="datetime", x_axis_label='date', y_axis_label='cases')
    p2.xaxis.formatter.days = '%d-%b'
    p2.y_range.start = 0

    # Graph 3 - R-Number
    hover3 = HoverTool(tooltips=[('country', '$name'), ('date', '$x{%F}'), ('r-number', '$y')],
                       formatters={'$x': 'datetime'})
    p3 = figure(width=600, height=300, title="R-Number", tools=[hover3], x_axis_type="datetime", x_axis_label='date',
                y_axis_label='r-number')
    p3.xaxis.formatter.days = '%d-%b'

    # Graph 4 - Deaths in previous week per 100k people
    hover4 = HoverTool(tooltips=[('country', '$name'), ('date', '$x{%F}'), ('deaths', '$y{0.0}')],
                       formatters={'$x': 'datetime'})
    p4 = figure(width=600, height=300, title="Deaths in previous week per 100k people", tools=[hover4],
                x_axis_type="datetime", x_axis_label='date', y_axis_label='deaths')
    p4.xaxis.formatter.days = '%d-%b'
    p4.y_range.start = 0

    # Graph 5 - Total vaccinations per 100 people
    hover5 = HoverTool(tooltips=[('country', '$name'), ('date', '$x{%F}'), ('vaccinations', '$y{0,0}')],
                       formatters={'$x': 'datetime'})
    p5 = figure(width=600, height=300, title="Total vaccinations per 100 people", tools=[hover5],
                x_axis_type="datetime", x_axis_label='date', y_axis_label='vaccinations')
    p5.xaxis.formatter.days = '%d-%b'
    p5.y_range.start = 0

    # Create lists to contain country specific graphs for number of cases per day and number of deaths per day
    cases = []
    deaths = []

    # 2. Create glyphs

    for i, country in enumerate(countries):
        my_country = Country(data, country)

        # Plot graphs 1 - 4
        s1 = my_country.active_cases / 1000
        p1.line(s1.index, s1.values, name=country, legend_label=country, line_width=2, line_color=colours[i])

        s2 = my_country.cases_by_population[-60:]
        p2.line(s2.index, s2.values, name=country, legend_label=country, line_width=2, line_color=colours[i])
        
        s3 = my_country.r_number(4, 7)[-60:]
        p3.line(s3.index, s3.values, name=country, legend_label=country, line_width=2, line_color=colours[i])

        s4 = my_country.deaths_by_population[-60:]
        p4.line(s4.index, s4.values, name=country, legend_label=country, line_width=2, line_color=colours[i])

        # s5 = my_country.total_vaccinations_per_hundred()[-60:]
        s5 = my_country.vaccinations[-60:]
        p5.line(s5.index, s5.values, name=country, legend_label=country, line_width=2, line_color=colours[i])

        # Graph 6 - Cases
        p6 = figure(width=600, height=200, title=f'{country} - Cases per Day', x_axis_type="datetime",
                    x_axis_label='date', y_axis_label='cases')
        p6.vbar(my_country.date, top=my_country.cases, color=colours[i])
        p6.xaxis.formatter.months = '%b-%y'

        # Graph 7 - Deaths
        p7 = figure(width=600, height=200, title=f'{country} - Deaths per Day', x_axis_type="datetime",
                    x_axis_label='date', y_axis_label='deaths')
        p7.vbar(my_country.date, top=my_country.deaths, color=colours[i])
        p7.xaxis.formatter.months = '%b-%y'

        cases.append(p6)
        deaths.append(p7)

    for p in [p1, p2, p3, p4, p5]:
        p.legend.location = 'top_left'

    r_one = Span(location=1, dimension='width', line_color='maroon', line_width=2)
    p3.add_layout(r_one)

    # 3. Show the results
    show(layout([
        [p1],
        [p2, p3],
        [p4, p5],
        [cases, deaths]
    ]))

    # TODO add text with data source
