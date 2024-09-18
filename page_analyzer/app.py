from flask import (Flask, render_template, request, redirect,
                   url_for, flash)
import os
from urllib.parse import urlparse
from validators.url import url as validate_url
from dotenv import load_dotenv
from . import db_tools, url_parsing
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


@app.route('/')
def main_page():
    return render_template('index.html')


@app.post('/urls')
def add_url():
    url_to_add = request.form.get('url')
    normalized_url = normalize_url(url_to_add) 
    if not validate_url(normalized_url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html'), 422
    url = db_tools.get_url_by('name', normalized_url)
    if url:
        flash('Страница уже существует', 'warning')
        return redirect(url_for('url_page', id=url.id))
    url = db_tools.insert_url(normalized_url)
    flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_page', id=url.id))


@app.get('/urls')
def urls():
    urls = db_tools.get_all_urls()
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:id>')
def url_page(id):
    url = db_tools.get_url_by('id', id)
    url_checks = db_tools.get_url_checks(id)
    if not url:
        flash('Запрашиваемая страница не найдена', 'warning')
        return redirect(url_for('index'), 404)
    return render_template('url_page.html', url=url, url_checks=url_checks)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url_data = db_tools.get_url_by('id', id)
    if not url_data:
        flash('Запрашиваемая страница не найдена', 'warning')
        return redirect(url_for('index'))
    url_name = url_data.name

    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('url_page', id=id))
    db_tools.add_url_check(id, url_parsing.get_url_data(response))
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_page', id=id))
