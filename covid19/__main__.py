import argparse
from datetime import date
from covid19 import graph as gr


def main():

    parser = argparse.ArgumentParser(description="Generate graphs based on COVID-19 data from OWID")
    parser.add_argument('output_dir', type=str, help="The location where the output should be stored")
    parser.add_argument('countries', type=str, help="Countries for which graph's should be created", nargs='+')

    args = parser.parse_args()

    countries = tuple(x.replace('_', ' ') for x in args.countries)
    file_name = f'{args.output_dir}/covid-graph_{date.today()}.html'

    data = gr.import_owid_data()

    gr.make_graphs(data, countries, file_name)


if __name__ == '__main__':
    main()
