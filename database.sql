DROP TABLE if exists urls CASCADE;
DROP TABLE if exists url_checks CASCADE;


CREATE TABLE urls (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name varchar(255) UNIQUE NOT NULL,
    created_at date DEFAULT CURRENT_DATE NOT NULL
    );


CREATE TABLE url_checks (
    id int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id int REFERENCES urls (id) NOT NULL,
    status_code int,
    h1 varchar(255),
    title varchar(255),
    description text,
    created_at date DEFAULT CURRENT_DATE NOT NULL
    );
