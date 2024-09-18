from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
)
import os
from urllib.parse import urlparse
from validators.url import url as validate_url
from dotenv import load_dotenv
from . import db_tools, url_parsing
import requests


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.database_url = os.getenv("DATABASE_URL")


def normalize_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


@app.route("/")
def main_page():
    connection = db_tools.db_connect(app)
    messages = get_flashed_messages(with_categories=True)
    return render_template("index.html", messages=messages)


@app.post("/urls")
def add_url():
    connection = db_tools.db_connect(app)

    url_to_add = request.form.get("url")
    normalized_url = normalize_url(url_to_add)
    if not validate_url(normalized_url):
        flash("Некорректный URL", "danger")
        messages = get_flashed_messages(with_categories=True)
        return render_template("index.html", messages=messages), 422

    url = db_tools.get_url_by("name", normalized_url, connection=connection)
    if url:
        flash("Страница уже существует", "warning")
        return redirect(url_for("url_page", id=url.id))
    url = db_tools.insert_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_page", id=url.id))


@app.get("/urls")
def urls():
    connection = db_tools.db_connect(app)
    messages = get_flashed_messages(with_categories=True)
    urls = db_tools.get_all_urls()
    return render_template("urls.html", messages=messages, urls=urls)


@app.get("/urls/<int:id>")
def url_page(id):
    connection = db_tools.db_connect(app)
    messages = get_flashed_messages(with_categories=True)
    url = db_tools.get_url_by("id", id, connection=connection)
    url_checks = db_tools.get_url_checks(id, connection=connection)
    if not url:
        flash("Запрашиваемая страница не найдена", "warning")
        return redirect(url_for("index"), 404)
    return render_template(
        "url_page.html", messages=messages, url=url, url_checks=url_checks
    )


@app.post("/urls/<int:id>/checks")
def check_url(id):
    connection = db_tools.db_connect(app)

    url_name = db_tools.get_url_by("id", id, connection=connection).name
    if not url_name:
        flash("Запрашиваемая страница не найдена", "warning")
        return redirect(url_for("index"))

    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("url_page", id=id))

    db_tools.add_url_check(
        id, url_parsing.get_url_data(response), connection=connection
    )
    flash("Страница успешно проверена", "success")
    return redirect(url_for("url_page", id=id))
