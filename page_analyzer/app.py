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

    url = db.get_url_by_name(normalized_url)
    if url:
        flash("Страница уже существует", "warning")
        return redirect(url_for("get_url", id=url.id))

    url = db.insert_url(normalized_url)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("get_url", id=url.id))


@app.get("/urls")
def get_urls():
    urls = db.get_all_urls()
    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:id>")
def get_url(id):
    url = db.get_url_by_id(id)
    url_checks = db.get_url_checks(id)

    if not url:
        flash("Запрашиваемая страница не найдена", "warning")
        return redirect(url_for("index"))

    return render_template("url_page.html", url=url, url_checks=url_checks)


@app.post("/urls/<int:id>/checks")
def check_url(id):
    url_data = db.get_url_by_id(id)
    if not url_data:
        flash("Запрашиваемая страница не найдена", "warning")
        return redirect(url_for("index"))

    url_name = url_data.name
    try:
        response = requests.get(url_name)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        flash("Произошла ошибка при проверке", "danger")
        return redirect(url_for("get_url", id=id))

    db.insert_url_check(id, url_parsing.get_url_data(response))
    flash("Страница успешно проверена", "success")
    return redirect(url_for("get_url", id=id))
