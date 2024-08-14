import os

from flask import (
    Flask,
    render_template,
    request,
    flash,
    url_for,
    redirect,
)
from dotenv import load_dotenv

import page_analyzer.db as db
import page_analyzer.html as html
import page_analyzer.urls as urls


load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

DATABASE_URL = os.getenv('DATABASE_URL')

url_repository = db.UrlRepository(db.DatabaseConnection(DATABASE_URL))


@app.route('/')
def index():
    return render_template(
        'index.html',
    )


@app.get('/urls')
def get_urls_list():
    urls = url_repository.get_urls()
    return render_template(
        'urls.html',
        urls=urls,
    )


@app.post('/urls')
def save_urls():
    data = request.form.to_dict()['url']

    if not urls.is_valid_url(data):
        flash('Некорректный URL', 'error')
        return render_template(
            'index.html',
        ), 422

    url = urls.normalaize_url(data)

    if existed_url := url_repository.find_url_by_name(url):
        id = existed_url.id
        flash('Страница уже существует', 'info')
    else:
        id = url_repository.save(url)
        flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url_details', id=id))


@app.get('/urls/<int:id>')
def url_details(id):
    url_checks = url_repository.get_url_checks(id)
    url = url_repository.get(id)
    if not url:
        return render_template(
            '404.html'
        )

    return render_template(
        'show.html',
        id=id,
        url=url,
        url_checks=url_checks
    )


@app.post('/urls/<int:id>/checks')
def check_urls(id):
    url_name = url_repository.get(id).name

    status_code = urls.check_url(url_name)
    if not status_code:
        flash('Произошла ошибка при проверке', 'error')
    else:
        url_content = html.get_url_content(html.parse_url(url_name))
        url_repository.save_check(id, url_content, status_code)
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('url_details', id=id, ))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
