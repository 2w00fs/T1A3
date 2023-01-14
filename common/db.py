from flask import Flask, request, redirect, url_for
from shared import db, ma

from settings import (
    db_name,
    db_address,
    db_user,
    db_pass,
)


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{db_user}:{db_pass}@{db_address}:5432/{db_name}'


db.init_app(app)
ma.init_app(app)


@app.route("/")
def welcome():
    return f"<html><body style='text-align:center;margin-top:30vh;background-color:black;color:white;'> \
    <h1>It's a Comedy Show</h1><h1>Henlo</h1></body></html>"


@app.route('/create_all/')
def create_db_all():
    db.create_all()
    # db.session.add_all(jb_seed)
    db.session.commit()
    print("All Done")
    return f'<html style="background-color:black;color:white"><h1 style="color:white">All Done!</h1></html>'


if __name__ == "__main__":
    app.run(port="8111")
