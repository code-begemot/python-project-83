from flask import (Flask, redirect, render_template, request,
                   url_for, get_flashed_messages, flash)
from dotenv import load_dotenv
import psycopg2
import os
from urllib.parse import urlparse
import validators
import requests
from bs4 import BeautifulSoup
from contextlib import contextmanager
from page_analyzer import db

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@contextmanager
def conn_context_manager(url):
    conn = psycopg2.connect(url)
    try:
        yield conn.cursor()
    finally:
        conn.commit()
        conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.post('/urls')
def post_url():
    url = str(request.form.to_dict()['url'])
    is_valid = validators.url(url)
    if is_valid and len(url) < 256:
        o = urlparse(url)
        norm_url = f"{o.scheme}://{o.netloc}"
        with conn_context_manager(DATABASE_URL) as curr:
            curr.execute(db.is_exist_url(norm_url))
            exist = curr.fetchone()
        print(exist)
        if exist[0]:
            with conn_context_manager(DATABASE_URL) as curr:
                curr.execute(db.id_by_url(norm_url))
                id = curr.fetchone()[0]
            flash("Страница уже существует", category='alert-info')
            return redirect(url_for('show_url', id=id))
        with conn_context_manager(DATABASE_URL) as curr:
            print(curr)
            curr.execute(db.insert_url(norm_url))
            curr.execute(db.id_by_url(norm_url))
            id = curr.fetchone()[0]
            print(curr.fetchone())
        flash('Страница успешно добавлена', category='alert-success')
        return redirect(url_for('show_url', id=id), code=302)
    else:
        return render_template('index.html', url=url), 422


@app.get('/urls')
def get_urls():
    messages = get_flashed_messages(with_categories=True)
    with conn_context_manager(DATABASE_URL) as curr:
        curr.execute(db.get_urls())
        urls = curr.fetchall()
    return render_template(
        'urls/index.html',
        urls=urls, messages=messages
    )


@app.route('/urls/<id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    with conn_context_manager(DATABASE_URL) as curr:
        curr.execute(db.url_by_id(id))
        url = curr.fetchone()
        curr.execute(db.checks_by_id(id))
        checks = curr.fetchall()
    return render_template(
        'urls/show.html',
        url=url,
        checks=checks,
        id=id,
        messages=messages
    )


@app.post('/urls/<id>/checks')
def check(id):
    with conn_context_manager(DATABASE_URL) as curr:
        curr.execute(db.url_by_id(id))
        url = curr.fetchone()[1]
        print(url)
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            flash('Произошла ошибка при проверке', category='alert-danger')
            return redirect(url_for('show_url', id=id))
        else:
            code = r.status_code
            html = r.text
            soup = BeautifulSoup(html, 'html.parser')
            try:
                h1 = soup.h1.string
            except AttributeError:
                h1 = ""
            try:
                title = soup.title.string
            except AttributeError:
                title = ""
            try:
                description = soup.find('meta',
                                        {'name': 'description'})['content']
            except TypeError:
                description = ""
            curr.execute(db.insert_checks(id, code, h1, title, description))
            flash('Страница успешно проверена', category='alert-success')
            return redirect(url_for('show_url', id=id))
