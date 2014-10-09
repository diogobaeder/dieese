import json
import re

from flask import Flask, render_template
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
            current_year = int(column.find('a').text)
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

    data = []
    i = 0
    moving_average = 12
    relations = []

    for year in main_data:
        months = main_data[year]
        for month in months:
            salaries = months[month]
            date = '{}-{:0>2}'.format(year, month + 1)
            nominal = salaries['nominal']
            necessary = salaries['necessary']
            data.append({
                'Data': date,
                'Salário': nominal,
                'Tipo': 'Nominal',
            })
            data.append({
                'Data': date,
                'Salário': necessary,
                'Tipo': 'Necessário',
            })
            data.append({
                'Data': date,
                'Relação': nominal / necessary,
                'Nome': 'Relação',
            })
            relations.append(nominal / necessary)
            first = i - moving_average
            if first >= 0:
                last = i + 1
                values = relations[first:last]
                median = sum(values) / moving_average
                data.append({
                    'Data': date,
                    'Relação': median,
                    'Nome': 'Média ponderada',
                })
            i += 1

    return render_template('index.html', data=json.dumps(data))


if __name__ == '__main__':
    app.run(debug=True)
