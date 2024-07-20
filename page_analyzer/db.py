def is_exist_url(url):
    return f"SELECT EXISTS(SELECT 1 FROM urls WHERE name = '{url}');"


def id_by_url(url):
    return f"SELECT id FROM urls WHERE name = '{url}';"


def insert_url(url):
    return f"INSERT INTO urls (name) VALUES ('{url}');"


def get_urls():
    return ("SELECT DISTINCT ON (urls.id) urls.id, urls.name, "
            "url_checks.created_at, status_code "
            "FROM urls "
            "LEFT JOIN url_checks "
            "ON urls.id = url_checks.url_id "
            "ORDER BY urls.id DESC, created_at DESC;")


def url_by_id(id):
    return f"SELECT * FROM urls WHERE id = {id};"


def checks_by_id(id):
    return (f"SELECT * FROM url_checks "
            f"WHERE url_id = {id} AND "
            f"EXISTS (SELECT * FROM url_checks) ORDER BY id DESC;")


def insert_checks(id, code, h1, title, description):
    return (f"INSERT INTO url_checks "
            f"(url_id, status_code, h1, title, description) "
            f"VALUES ({id}, {code}, '{h1}', '{title}', '{description}');")
