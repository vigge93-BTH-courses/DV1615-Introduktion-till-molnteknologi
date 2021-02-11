from flask import Flask
import requests
from typing import Dict, Any

app = Flask(__name__)
endpoint = 'https://lager.emilfolino.se/v2/products/everything'


@app.route('/unique')
def unique() -> Dict[Any, Any]:
    data = get_data()
    response_data = {'data': [{'name': name, 'stock': stock}
                              for name, stock in data.items()]}
    return response_data


@app.route('/search/<string:query>')
def search(query: str) -> Dict[Any, Any]:
    data = get_data()
    query = query.lower()
    response_data = {'data': [{'name': name, 'stock': stock}
                              for name, stock in data.items()
                              if query in name.lower()]}
    return response_data


def get_data() -> Dict[str, int]:
    response = requests.get(endpoint)
    response_data = response.json()['data']
    data: Dict[str, int] = {}
    for d in response_data:
        if not isinstance(d['stock'], int):
            d['stock'] = 0

        if d['name'] in data:
            data[d['name']] += d['stock']
        else:
            data[d['name']] = d['stock']

    return data


if __name__ == '__main__':
    app.run()
