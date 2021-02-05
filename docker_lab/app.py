from flask import Flask

app = Flask(__name__)
visits = 0


@app.route('/')
def default():
    global visits
    visits += 1
    return f'<h1>{visits}</h1>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
