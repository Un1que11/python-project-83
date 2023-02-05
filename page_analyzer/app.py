import page_analyzer.db as db

import os
import logging

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv
from validators.url import url as valid
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


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404


@app.route('/')
def main_page():
    return render_template('index.html', main_page=main_page)


@app.get('/urls')
def get_urls():
    urls = db.get_urls()
    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def post_urls():
    input = request.form.to_dict()
    url = input['url']

    if not valid(url):
        flash('Некорректный URL', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url=url,
            messages=messages), 422

    url = get_correct_url(url)
    exists = db.is_exist_url(url)

    if exists:
        flash('Страница уже существует', 'alert-info')
        return redirect(url_for('url_get', id=db.find_url(url).id))

    result = db.add_url(url)

    match result:
        case None:
            flash('Произошла ошибка', 'alert-danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template(
                'index.html',
                url=url,
                messages=messages), 500
        case _:
            flash('Страница успешно добавлена', 'alert-success')
            return redirect(url_for('url_get', id=result))


@app.get('/urls/<int:id>')
def url_get(id):
    url = db.find_url(id)
    checks = db.get_checks(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'url_analyze.html',
        url=url,
        checks=checks,
        messages=messages
    )


@app.post('/urls/<int:id>/checks')
def url_check(id):
    url = db.find_url(id)
    try:
        response = requests.get(url.name)
        response.raise_for_status()
        page = get_page_data(url.name)
        db.add_check({
            'id': id,
            'status_code': response.status_code,
            'h1': page['h1'],
            'title': page['title'],
            'description': page['description']})
        flash('Страница успешно проверена', 'alert-success')
        return redirect(url_for('url_get', id=id))
    except Exception as err:
        logging.error(err)
        flash('Произошла ошибка при проверке', 'alert-danger')
        return redirect(url_for('url_get', id=id))


def get_correct_url(url: str) -> str:
    url = urlparse(url)
    return url._replace(
        path='',
        params='',
        query='',
        fragment='').geturl()


def get_page_data(url):
    page_data = {
        'h1': '',
        'title': '',
        'description': ''
    }
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1
    title = soup.title
    content = soup.find(
        "meta", attrs={'name': 'description'})

    page_data.update(
        {'h1': h1.get_text()}
    ) if h1 is not None else page_data.setdefault('h1', '')
    page_data.update(
        {'title': title.get_text()}
    ) if title is not None else page_data.setdefault('title', '')
    page_data.update(
        {'description': content["content"]}
    ) if content is not None else page_data.setdefault('description', '')
    return page_data
