from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
import os
from validators.url import url as validate_url
from dotenv import load_dotenv
from . import db, url_parsing
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.database_url = os.getenv("DATABASE_URL")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/urls")
def add_url():
    url_to_add = request.form.get("url")
    normalized_url = url_parsing.normalize_url(url_to_add)
    if not validate_url(normalized_url):
        flash("Некорректный URL", "danger")
        return render_template("index.html"), 422

    connection = db.db_connect(app)
    with connection:
        url = db.get_url_by("name", normalized_url, connection=connection)
        if url:
            flash("Страница уже существует", "warning")
            return redirect(url_for("get_url", id=url.id))

        url = db.insert_url(normalized_url, connection)

    flash("Страница успешно добавлена", "success")
    return redirect(url_for("get_url", id=url.id))


@app.get("/urls")
def get_urls():
    connection = db.db_connect(app)
    with connection:
        urls = db.get_all_urls(app, connection=connection)
    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:id>")
def get_url(id):
    connection = db.db_connect(app)
    with connection:
        url = db.get_url_by("id", id, connection=connection)
        url_checks = db.get_url_checks(id, connection=connection)

        if not url:
            flash("Запрашиваемая страница не найдена", "warning")
            return redirect(url_for("index"))

    return render_template("url_page.html", url=url, url_checks=url_checks)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    connection = db.db_connect(app)
    with connection:
        url_data = db.get_url_by("id", id, connection=connection)
        if not url_data:
            flash("Запрашиваемая страница не найдена", "warning")
            return redirect(url_for("index"))

        url_name = url_data.name
        try:
            response = requests.get(url_name)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            flash("Произошла ошибка при проверке", "danger")
            return redirect(url_for("url_page", id=id))

        db.insert_url_check(
            id, url_parsing.get_url_data(response), connection=connection
        )
        flash("Страница успешно проверена", "success")

    return redirect(url_for("get_url", id=id))
