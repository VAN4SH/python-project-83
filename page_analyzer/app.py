from flask import (Flask, render_template, request, redirect,
                   url_for, flash, get_flashed_messages)
import os
from urllib.parse import urlparse
from validators.url import url as validate_url
from dotenv import load_dotenv
from . import db_tools, url_parsing
import requests


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('7c5aa61654fdbd2a939c6bebb12b14a6')


@app.route('/')
def main_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'main_page.html',
        messages=messages
    )


@app.post('/urls')
def add_url():

    url_to_add = request.form.get('url')
    parsed_url = urlparse(url_to_add)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    if not validate_url(normalized_url):
        flash('Некорректный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main_page.html', messages=messages), 422

    url = db_tools.get_url_by('name', normalized_url)
    if url:
        flash('Страница уже существует', 'warning')
        return redirect(url_for('url_page', id=url.id))
    url = db_tools.insert_url(normalized_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_page', id=url.id))


@app.get('/urls')
def urls():
    messages = get_flashed_messages(with_categories=True)
    urls = db_tools.get_all_urls()
    return render_template('urls.html', messages=messages,
                           urls=urls)


@app.get('/urls/<int:id>')
def url_page(id):
    messages = get_flashed_messages(with_categories=True)
    url = db_tools.get_url_by('id', id)
    url_checks = db_tools.get_url_checks(id)
    if not url:
        flash('Запрашиваемая страница не найдена', 'warning')
        return redirect(url_for('main_page'), 404)
    return render_template('url_page.html', messages=messages,
                           url=url, url_checks=url_checks)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url_name = db_tools.get_url_by('id', id).name
    if not url_name:
        flash('Запрашиваемая страница не найдена', 'warning')
        return redirect(url_for('main_page'))

    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_page', id=id))

    db_tools.add_url_check(id, url_parsing.get_url_data(response))
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_page', id=id))
