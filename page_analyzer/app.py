import page_analyzer.db as db

import os
import logging

from urllib.parse import urlparse
from dotenv import load_dotenv
from validators.url import url
from flask import Flask, render_template, request, flash, url_for, redirect

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

client = app.test_client()

logging.basicConfig(
    filename='logs.log',
    filemode='w',
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


def get_correct_url(url_address: str) -> str:
    correct_url = urlparse(url_address)
    return correct_url._replace(
        path='',
        params='',
        query='',
        fragment=''
    ).geturl()


@app.route('/')
def main_page():
    return render_template('index.html', main_page=main_page)


@app.get('/urls')
def get_urls():
    urls = db.get_urls()
    return render_template('urls.html', urls=urls)


@app.post('/urls')
def post_urls():
    input_ = request.form.to_dict()
    url_address = input_['url']

    if not url(url_address):
        flash('Invalid URL', 'alert-danger')
        return render_template(
            'index.html',
            main_page=main_page,
            url=url_address
        ), 422

    correct_url = get_correct_url(url_address)
    exist = db.is_exist_url(correct_url)

    if exist:
        flash('Page already exists', 'alert-info')
        return redirect(
            url_for('get_url_check', id=db.find_url(correct_url).id)
        )

    result = db.add_url(correct_url)

    match result:
        case None:
            flash('An error has occurred', 'alert-danger')
            return render_template(
                'index.html',
                url=correct_url
            ), 500
        case _:
            flash('Page successfully added', 'alert-success')
            return redirect(url_for('get_url_check', id=result))


@app.get('/urls/<int:id>')
def get_url_check(id):
    url_address = db.find_url(id)
    return render_template(
        'url_analyze.html',
        url=url_address
    )
