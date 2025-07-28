from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'items.db'

# Connect to the database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

# Close the connection when the app context ends
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Initialize DB (run once at startup)
def init_db():
    if not os.path.exists(DATABASE):
        with app.app_context():
            db = get_db()
            db.execute('''
                CREATE TABLE items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT
                )
            ''')
            db.commit()

# Home (list items)
@app.route('/')
def index():
    db = get_db()
    items = db.execute('SELECT * FROM items').fetchall()
    return render_template('index.html', items=items)

# Add item
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        db = get_db()
        db.execute('INSERT INTO items (name, description) VALUES (?, ?)', (name, description))
        db.commit()
        return redirect(url_for('index'))
    return render_template('add.html')

# Edit item
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        db.execute('UPDATE items SET name = ?, description = ? WHERE id = ?', (name, description, id))
        db.commit()
        return redirect(url_for('index'))
    item = db.execute('SELECT * FROM items WHERE id = ?', (id,)).fetchone()
    return render_template('edit.html', item=item)

# Delete item
@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    db.execute('DELETE FROM items WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))

# Main entry
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
