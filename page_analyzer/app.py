from flask import Flask, render_template


app = Flask(__name__)

client = app.test_client()


@app.route('/')
def main_page():
    return render_template('index.html', main_page=main_page)
