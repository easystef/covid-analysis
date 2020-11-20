from bs4 import BeautifulSoup
import requests

RKI_URL = 'https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Risikogebiete_neu.html'


# THIS CODE IS NOT USED YET BY THE APPLICATION!!!
def main():

    rki = requests.get(RKI_URL)
    soup = BeautifulSoup(rki.text, 'html.parser')

    main_div = soup.find('div', {'id': 'main'})

    countries = []

    line_item = main_div.ul.li

    while True:

        if sub_items := line_item.findAll('li'):
            x = line_item.p.string
            for subentry in sub_items:
                x += f' {subentry.string};'
            countries.append(x)
        else:
            countries.append(line_item.string)

        if line_item.nextSibling:
            line_item = line_item.nextSibling
        else:
            break

    for i in countries:
        a, b = unpack_country(i)
        #b = parse_date(b)
        print(i)
        print((a, b))


def unpack_country(line_item):

    x1 = line_item.find('(seit')
    d1 = line_item.find('(seit') + 6  # Corresponds to '(seit '
    d2 = line_item.find(')')

    country = line_item[:x1]

    risk_since = line_item[d1:d2]

    return country, risk_since


def parse_date(date):

    month_dict = {'Januar': '01', 'Februar': '02', 'März': '03', 'April': '04', 'Mai': '05', 'Juni': '06', 'Juli': '07',
                  'August': '08', 'September': '09', 'Oktober': '10', 'November': '11', 'Dezember': '12'}

    x = date.find('.')

    return '2020-' + month_dict[date[x+2:]] + '-' + date[:x]


if __name__ == '__main__':
    main()

# TODO split country name from bit in parenthesis
# TODO translate
