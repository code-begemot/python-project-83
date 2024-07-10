from flask import Flask, redirect, render_template, request, url_for, get_flashed_messages, flash
from dotenv import load_dotenv
import psycopg2
import os
from urllib.parse import urlparse
import validators

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')

conn = psycopg2.connect(DATABASE_URL)
curr = conn.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

print(SECRET_KEY)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"

@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    print(messages)
    return render_template('index.html', messages=messages)


@app.post('/urls')
def post_url():
    messages = get_flashed_messages(with_categories=True)
    print(messages)
    url = str(request.form.to_dict()['url'])
    is_valid = validators.url(url)
    if is_valid and len(url) < 256:
        print((is_valid))
        o = urlparse(url)
        norm_url = o.netloc
        curr.execute(f"SELECT EXISTS(SELECT 1 FROM urls WHERE name = '{norm_url}');")
        exist = curr.fetchone()
        print(exist)
        if exist[0]:
            curr.execute(f"SELECT id FROM urls WHERE name = '{norm_url}';")
            id = curr.fetchone()[0]
            flash("Страница уже существует", category='alert-info')
            return redirect(url_for('show_url', id=id))
        curr.execute(f"INSERT INTO urls (name) VALUES ('{norm_url}');")
        conn.commit()
        curr.execute(f"SELECT id FROM urls WHERE name = '{norm_url}';")
        id = curr.fetchone()[0]
        flash('Страница успешно добавлена', category='alert-success')
        return redirect(url_for('show_url', id=id), code=302)
    else:
        print('you')
        flash('Некорректный URL', category='alert-danger')
        flash(url, category='error')
        return redirect(url_for('index'))

@app.get('/urls')
def get_urls():
    messages = get_flashed_messages(with_categories=True)
    curr.execute(f"SELECT EXISTS(SELECT 1 FROM url_checks);")
    exist = curr.fetchone()
    print(exist)
    if exist[0]:
        curr.execute(f"SELECT DISTINCT ON (urls.id) urls.id, urls.name, url_checks.created_at, status_code FROM url_checks INNER JOIN urls ON url_checks.url_id = urls.id ORDER BY urls.id DESC, created_at DESC;")
        urls = curr.fetchall()
        curr.execute(f"SELECT COUNT(*) FROM urls;")
        test = curr.fetchall()
        print(test)
    else:
        curr.execute("SELECT * FROM urls;")
        urls = curr.fetchall()
        print(urls)
    return render_template(
        'urls/index.html',
        urls=urls, messages=messages
    )


@app.route('/urls/<id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    print(messages)
    curr.execute(f"SELECT * FROM urls WHERE id = {id};")
    #curr.execute(f"SELECT * FROM urls_checks WHERE url_id = {id};")
    url = curr.fetchone()
    curr.execute(f"SELECT * FROM url_checks WHERE url_id = {id} AND EXISTS (SELECT * FROM url_checks) ORDER BY id DESC;")
    checks = curr.fetchall()
    print(url)
    print(checks)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'urls/show.html',
        url=url,
        checks=checks,
        id=id,
        messages=messages
    )


@app.post('/urls/<id>/checks')
def check(id):
    curr.execute(f"INSERT INTO url_checks (url_id) VALUES ({id});")
    conn.commit()
    checks = curr.execute(f"SELECT id, created_at FROM url_checks WHERE url_id = {id};")
    print(curr.fetchall())
    flash('Страница успешно проверена', category='alert-success')
    return redirect(url_for('show_url', id=id, checks=checks))