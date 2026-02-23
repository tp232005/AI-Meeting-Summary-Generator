import sqlite3
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, g

# Add parent dir to path so nlp package resolves
import sys
sys.path.insert(0, os.path.dirname(__file__))

from nlp import preprocess, summarize, extract_action_items, extract_decisions

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')


# ──────────────────────────── Database helpers ────────────────────────────────

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT NOT NULL,
                raw_text    TEXT NOT NULL,
                summary     TEXT NOT NULL,
                bullets     TEXT NOT NULL,
                actions     TEXT NOT NULL,
                decisions   TEXT NOT NULL,
                keywords    TEXT NOT NULL,
                word_count  INTEGER,
                length      TEXT,
                created_at  TEXT NOT NULL
            )
        ''')
        db.commit()


# ──────────────────────────────── Routes ──────────────────────────────────────

@app.route('/', methods=['GET'])
def index():
    db = get_db()
    recent = db.execute(
        'SELECT id, title, word_count, length, created_at FROM summaries ORDER BY id DESC LIMIT 8'
    ).fetchall()
    return render_template('index.html', recent=recent)


@app.route('/summarize', methods=['POST'])
def summarize_meeting():
    title = request.form.get('title', '').strip() or 'Untitled Meeting'
    text = request.form.get('transcript', '').strip()
    length = request.form.get('length', 'medium')

    if not text:
        return redirect(url_for('index'))

    # NLP pipeline
    preprocessed = preprocess(text)
    result = summarize(preprocessed, length=length)
    actions = extract_action_items(preprocessed['sentences'])
    decisions = extract_decisions(preprocessed['sentences'])

    # Persist to DB
    db = get_db()
    db.execute(
        '''INSERT INTO summaries
           (title, raw_text, summary, bullets, actions, decisions, keywords, word_count, length, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            title,
            text,
            result['summary'],
            json.dumps(result['bullet_points']),
            json.dumps(actions),
            json.dumps(decisions),
            json.dumps(preprocessed['keywords']),
            preprocessed['word_count'],
            length,
            datetime.now().strftime('%Y-%m-%d %H:%M'),
        )
    )
    db.commit()
    row_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]

    return redirect(url_for('result', summary_id=row_id))


@app.route('/result/<int:summary_id>')
def result(summary_id):
    db = get_db()
    row = db.execute('SELECT * FROM summaries WHERE id = ?', (summary_id,)).fetchone()
    if not row:
        return redirect(url_for('index'))

    data = dict(row)
    data['bullets'] = json.loads(data['bullets'])
    data['actions'] = json.loads(data['actions'])
    data['decisions'] = json.loads(data['decisions'])
    data['keywords'] = json.loads(data['keywords'])

    return render_template('result.html', data=data)


@app.route('/delete/<int:summary_id>', methods=['POST'])
def delete(summary_id):
    db = get_db()
    db.execute('DELETE FROM summaries WHERE id = ?', (summary_id,))
    db.commit()
    return redirect(url_for('index'))


# ────────────────────────────────── Entry ─────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
