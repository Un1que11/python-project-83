import page_analyzer.db as db
from page_analyzer.config import Config
from page_analyzer.services import get_response, get_page_data, get_correct_url

import logging

from validators.url import url as valid
from flask import \
    Flask, \
    render_template, \
    request, flash, \
    url_for, redirect, \
    get_flashed_messages

app = Flask(__name__)
app.config.from_object(Config)

logging.basicConfig(
    filename='logs.log',
    filemode='w',
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger(__name__)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500


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

    if result is None:
        flash('Произошла ошибка', 'alert-danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html',
            url=url,
            messages=messages), 500
    else:
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
        response = get_response(url.name)
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
