# -*- coding: utf-8 -*-
"""
    Flaskr Plus
    ~~~~~~
    A microblog example application written with Flask and sqlite3.
    Author: Abhirup Das
    Source-Code: Mark Liffiton and Armin Ronacher.

    Source-Code Copyright: (c) 2015 by Armin Ronacher.
    License: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('SELECT title, text, id, category FROM entries ORDER BY id DESC')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (title, text, category) values (?, ?, ?)',
               [request.form['title'], request.form['text'], request.form['category']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def del_entry():
    db = get_db()
    db.execute('DELETE FROM entries WHERE id = ?',[request.form.get('id')])
    db.commit()
    flash('New entry was successfully deleted')
    return redirect(url_for('show_entries'))


@app.route('/filter_entries', methods=['GET'])
def filter_entries():
    db = get_db()
    filter_category = request.args.get('category')
    category = db.execute('SELECT DISTINCT category FROM entries').fetchall()
    if filter_category == "all":
        all_entries = db.execute('SELECT * FROM entries ORDER BY id DESC').fetchall()
        return render_template('show_entries.html', entries=all_entries, category=category)
    else:
        entries = db.execute('SELECT * FROM entries WHERE category = ? ORDER BY id DESC', (filter_category,)).fetchall()
        return render_template('show_entries.html', entries=entries, category=category)


@app.route('/update', methods=['POST'])
def update_entry():
    db = get_db()
    db.execute("update entries set title = ?, category = ?, text = ?  where id = ? ",
               [request.form['title'], request.form['category'], request.form['text'], request.form.get('id')])
    db.commit()
    flash('Entry was successfully updated', 'info')
    return redirect(url_for('show_entries'))


@app.route('/update-redirect', methods=['GET'])
def update_redirect():
    id = request.args.get("id")
    return render_template('update.html', id=id)