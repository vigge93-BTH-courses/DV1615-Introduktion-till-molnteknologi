from flask import Flask, render_template, request, flash, jsonify, redirect, url_for
import requests
from typing import Dict, Any, List, Union, Optional
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\x8c\x1eZ\x8f{k\x15\xfa\xbdA\xa5\xae\x1a\xd18I\xf5\x05U\xb7\xd0\'U\xb7'

stock_api_endpoint = 'https://dv1615-viar19-project-lager-api.azurewebsites.net/v2/products/everything'
cognitive_services_endpoint = 'https://dv1615-apimanagement-lab.azure-api.net'
cognitive_services_access_token = '6af7226881af4bf4a83ccd810023a5a0'


@app.route('/')
def index() -> Any:
    return redirect(url_for('image_search'))


@app.route('/image_search', methods=('GET', 'POST'))
def image_search() -> str:

    if request.method == 'POST':
        image_url = request.form['image-url']
        tags = process_image(image_url)
        if not tags:
            return render_template('index.html')
        translations = translate_text(tags)
        if not translations:
            return render_template('index.html')
        result = set()
        raw_data = get_data()
        data = process_data(raw_data)
        for word in translations:
            res = search_data(data, word)
            for r in res:
                result.add(json.dumps(r))
        return render_template('index.html',
                               items=[json.loads(res) for res in result],
                               img_url=image_url)
    return render_template('index.html')


def get_data() -> List[Dict[str, Any]]:
    response = requests.get(stock_api_endpoint)
    response_data: List[Dict[str, Any]] = response.json()['data']
    return response_data


def process_data(raw_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    data: Dict[str, Dict[str, Union[str, int]]] = {}
    for d in raw_data:
        if not isinstance(d['stock'], int):
            d['stock'] = 0

        if d['name'] in data:
            data[d['name']]['stock'] += d['stock']
        else:
            data[d['name']] = {'stock': d['stock'],
                               'description': d['description']}
    return data


def process_image(img_url: str) -> Optional[List[str]]:
    url = f'{cognitive_services_endpoint}/vision/v2.0/analyze?visualFeatures=Tags'
    body = {'url': img_url}
    headers = {'Ocp-Apim-Subscription-Key': cognitive_services_access_token}

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        if response.status_code == 429:
            flash(
                f'Bildigenkänning misslyckades, försök igen om {response.headers["Retry-After"]} sekunder')
        elif response.status_code == 400:
            flash('Felaktig url, dubbelkolla länken och försök igen')
        else:
            flash('Bildigenkänning misslyckades, försök igen senare')
        return None
    print(response.json())
    data = response.json()['tags']

    return [d['name'] for d in data if d['confidence'] > 0.99]


def translate_text(texts: List[str]) -> Optional[List[str]]:
    url = f'{cognitive_services_endpoint}/translate?api-version=3.0&from=en&to=sv'
    body = [{'text': t} for t in texts]
    headers = {'Ocp-Apim-Subscription-Key': cognitive_services_access_token}
    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        if "Retry-After" in response.headers:
            flash(
                f'Översättning misslyckades, försök igen om {response.headers["Retry-After"]} sekunder')
        else:
            flash('Översättning misslyckades, försök igen senare')
        return None
    data = response.json()
    result = []
    for translation in data:
        for t in translation['translations']:
            if t['to'] == 'sv':
                result.append(t['text'])
    return result


def search_data(data: Dict[str, Dict[str, Any]], query: str) -> List[Dict[str, Union[int, str]]]:
    query = query.lower()
    response_data = [{'name': name, 'stock': value['stock'],
                      'description': value['description']}
                     for name, value in data.items()
                     if query in name.lower()
                     or value['description'] and query in value['description']]
    return response_data


if __name__ == '__main__':
    app.run()
