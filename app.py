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
            expiration_date TEXT NOT NULL,
            duracion INTEGER DEFAULT 30        
        )
    ''')
    conn.commit()
    conn.close()

# Obtener todos los clientes o filtrados por nombre
def get_clients(search=None):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    if search:
        cursor.execute('SELECT * FROM clients WHERE name LIKE ?', ('%' + search + '%',))
    else:
        cursor.execute('SELECT * FROM clients')
    clients = cursor.fetchall()
    conn.close()
    return clients

# Agregar un nuevo cliente
def add_client(name, email, registration_date, expiration_date, duracion=30):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (name, email, registration_date, expiration_date, duracion) VALUES (?, ?, ?, ?, ?)', 
                   (name, email, registration_date, expiration_date, duracion))
    conn.commit()
    conn.close()

# Editar un Cliente
def update_client(client_id, name, email, duracion):
    conn = sqlite3.connect('clients.db')
    cursor = conn.cursor()
    expiration_date = (datetime.now() + timedelta(days=duracion)).strftime('%Y-%m-%d')
    cursor.execute('UPDATE clients SET name = ?, email = ?, expiration_date = ?, duracion = ? WHERE id = ?', 
                   (name, email, expiration_date, duracion, client_id))
    conn.commit()
    conn.close()

# Eliminar un Cliente
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
        
        # Verificar que la duración sea un número positivo
        try:
            duracion = int(request.form['duracion'])
            if duracion <= 0:
                raise ValueError("La duración debe ser un número positivo.")
        except ValueError as e:
            return f"Error en la entrada de datos: {e}", 400
        
        registration_date = datetime.now().strftime('%Y-%m-%d')
        expiration_date = (datetime.now() + timedelta(days=duracion)).strftime('%Y-%m-%d')
        add_client(name, email, registration_date, expiration_date, duracion)
        return redirect(url_for('index'))
    
    search = request.args.get('search')  # Obtener el valor de búsqueda desde la URL
    clients = get_clients(search)  # Llamar a get_clients con o sin búsqueda
    return render_template('index.html', clients=clients)

@app.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit(client_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        # Verificar que la duración sea un número positivo
        try:
            duracion = int(request.form['duracion'])
            if duracion <= 0:
                raise ValueError("La duración debe ser un número positivo.")
        except ValueError as e:
            return f"Error en la entrada de datos: {e}", 400
        
        update_client(client_id, name, email, duracion)
        return redirect(url_for('index'))
    
    client = [c for c in get_clients() if c[0] == client_id]
    if not client:
        return "Cliente no encontrado", 404
    client = client[0]
    return render_template('edit.html', client=client)

@app.route('/delete/<int:client_id>')
def delete(client_id):
    delete_client(client_id)
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
