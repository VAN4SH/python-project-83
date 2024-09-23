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


@app.route("/")
def main_page():
    return render_template("main_page.html")


@app.route("/urls", methods=["POST"])
def add_url():
    url_to_add = request.form.get("url")
    parsed_url = urlparse(url_to_add)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    if not validate_url(normalized_url):
        flash("Некорректный URL", "danger")
        return render_template("main_page.html"), 422

    with db_tools.db_connect(app) as connection:
        url = db_tools.get_url_by("name", normalized_url, connection=connection)
        if url:
            flash("Страница уже существует", "warning")
            return redirect(url_for("url_page", id=url.id))

        url = db_tools.insert_url(normalized_url, connection)

    flash("Страница успешно добавлена", "success")
    return redirect(url_for("url_page", id=url.id))


@app.route("/urls", methods=["GET"])
def urls():
    with db_tools.db_connect(app) as connection:
        urls = db_tools.get_all_urls(app, connection=connection)
    return render_template("urls.html", urls=urls)


@app.route("/urls/<int:id>", methods=["GET"])
def url_page(id):
    with db_tools.db_connect(app) as connection:
        url = db_tools.get_url_by("id", id, connection=connection)
        url_checks = db_tools.get_url_checks(id, connection=connection)

        if not url:
            flash("Запрашиваемая страница не найдена", "warning")
            return redirect(url_for("main_page"))

    return render_template("url_page.html", url=url, url_checks=url_checks)


@app.route("/urls/<int:id>/checks", methods=["POST"])
def check_url(id):
    url_rec = None
    url_name = None

    with db_tools.db_connect(app) as connection:
        url_rec = db_tools.get_url_by("id", id, connection=connection)

        if not url_rec:
            flash("Запрашиваемая страница не найдена", "warning")
            return redirect(url_for("main_page"))

        url_name = url_rec.name

    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("url_page", id=id))

    with db_tools.db_connect(app) as connection:
        db_tools.add_url_check(
            id, url_parsing.get_url_data(response), connection=connection
        )

    flash("Страница успешно проверена", "success")
    return redirect(url_for("url_page", id=id))
