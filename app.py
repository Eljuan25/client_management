from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Crear la base de datos
def init_db():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            registration_date TEXT NOT NULL,
            expiration_date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Obtener todos los clientes
def get_clients():
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    conn.close()
    return clients

# Agregar un nuevo cliente
def add_client(name, email, registration_date, expiration_date):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (name, email, registration_date, expiration_date) VALUES (?, ?, ?, ?)', 
                   (name, email, registration_date, expiration_date))
    conn.commit()
    conn.close()


#Editar un Cliente

def update_client(client_id,name,email):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE clients SET name = ?, email = ? WHERE id = ?', 
                   (name, email, client_id))
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()




@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        registration_date = datetime.now().strftime('%Y-%m-%d')
        expiration_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        add_client(name, email, registration_date, expiration_date)
        return redirect(url_for('index'))
    
    clients = get_clients()
    return render_template('index.html', clients=clients)


@app.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit(client_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        update_client(client_id, name, email)
        return redirect(url_for('index'))
    
    client = [c for c in get_clients() if c[0] == client_id][0]
    return render_template('edit.html', client=client)

@app.route('/delete/<int:client_id>')
def delete(client_id):
    delete_client(client_id)
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0',port=5000, debug=True)
