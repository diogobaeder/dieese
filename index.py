import json
import re

from flask import Flask
from pyquery import PyQuery as pq


app = Flask(__name__)


m = [
    'Janeiro',
    'Fevereiro',
    'Março',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
]
MONTHS = {month: i for i, month in enumerate(m)}
NUMERIC_PATTERN = re.compile(r'([\d,\.]+)')


def money_to_float(money):
    br_number = NUMERIC_PATTERN.findall(money)[0]
    number = br_number.replace('.', '').replace(',', '.')
    return float(number)


@app.route('/')
def index():
    url = 'http://www.dieese.org.br/analisecestabasica/salarioMinimo.html'
    print('requesting...')
    d = pq(url=url)
    print('done.')
    rows = d('#conteudo table tr')
    main_data = {}
    current_year = None

    for row in rows:
        klass = row.attrib.get('class')
        columns = row.findall('td')
        if klass == 'subtitulo':
            column = columns[0]
            current_year = column.find('a').text
            main_data[current_year] = {}
        elif columns and len(columns) == 3:
            month_name = columns[0].text
            nominal = money_to_float(columns[1].text)
            necessary = money_to_float(columns[2].text)
            month = MONTHS[month_name]
            main_data[current_year][month] = {
                'nominal': nominal,
                'necessary': necessary,
            }

    return json.dumps(main_data, indent=4)


if __name__ == '__main__':
    app.run(debug=True)
