import page_analyzer.db as db

import os
import logging

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv
from validators.url import url
from flask import \
    Flask, \
    render_template, \
    request, flash, \
    url_for, redirect, \
    get_flashed_messages

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
        flash('Некорректный URL', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url=url_address,
            messages=messages
        ), 422

    correct_url = get_correct_url(url_address)
    exist = db.is_exist_url(correct_url)

    if exist:
        flash('Страница уже существует', 'alert-info')
        return redirect(
            url_for('get_url_check', id=db.find_url(correct_url).id)
        )

    result = db.add_url(correct_url)

    if result is None:
        flash('Произошла ошибка', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url=correct_url,
            messages=messages
        ), 500
    else:
        flash('Страница успешно добавлена', 'alert-success')
        return redirect(url_for('get_url_check', id=result))


@app.get('/urls/<int:id>')
def get_url_check(id):
    url_address = db.find_url(id)
    checks = db.get_checks(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'url_analyze.html',
        url=url_address,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<int:id>/checks')
def url_check(id):
    url = db.find_url(id)
    try:
        response = requests.get(url.name)
        status_code = response.status_code
        if status_code != 200:
            raise Exception
        page_data = get_page_data(url.name)
        db.add_check({
            'id': id,
            'status_code': status_code,
            'h1': page_data.get('h1'),
            'title': page_data.get('title'),
            'description': page_data.get('description')
        })
        flash('Страница успешно проверена', 'alert-success')
        return redirect(url_for('get_url_check', id=id))
    except Exception as err:
        logging.error(err)
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('get_url_check', id=id))


def get_correct_url(url_address: str) -> str:
    correct_url = urlparse(url_address)
    return correct_url._replace(
        path='',
        params='',
        query='',
        fragment=''
    ).geturl()


def get_page_data(url):
    page_data = {
        'h1': '',
        'title': '',
        'content': ''
    }

    response = requests.get(url)
    data = response.text
    soup = BeautifulSoup(data, 'html.parser')
    h1 = soup.h1
    title = soup.title
    description = soup.find('meta', attrs={'name': 'description'})['content']

    page_data.update(
        {'h1': h1.get_text()}
    ) if h1 is not None else page_data.setdefault('h1', '')

    page_data.update(
        {'title': title.get_text()}
    ) if title is not None else page_data.setdefault('title', '')

    page_data.update(
        {'description': description}
    ) if description is not None else page_data.setdefault('content', '')

    return page_data
