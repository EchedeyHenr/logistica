"""Script para crear la base de datos de logistica con datos iniciales."""
import sqlite3
import os

# Eliminar la base de datos si ya existe (para recrearla limpia)
if os.path.exists("logistica.db"):
    os.remove("logistica.db")

conn = sqlite3.connect("logistica.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

# Crear tablas
cursor.execute("""
    CREATE TABLE IF NOT EXISTS centers (
        center_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS routes (
        route_id TEXT PRIMARY KEY,
        origin_center_id TEXT NOT NULL,
        destination_center_id TEXT NOT NULL,
        active INTEGER NOT NULL,
        FOREIGN KEY (origin_center_id) REFERENCES centers(center_id),
        FOREIGN KEY (destination_center_id) REFERENCES centers(center_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS shipments (
        tracking_code TEXT PRIMARY KEY,
        sender TEXT NOT NULL,
        recipient TEXT NOT NULL,
        priority INTEGER NOT NULL,
        current_status TEXT NOT NULL,
        shipment_type TEXT NOT NULL,
        assigned_route_id TEXT,
        current_center_id TEXT,
        FOREIGN KEY (assigned_route_id) REFERENCES routes(route_id),
        FOREIGN KEY (current_center_id) REFERENCES centers(center_id)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS shipment_status_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tracking_code TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (tracking_code) REFERENCES shipments(tracking_code)
    )
""")

# Insertar centros
cursor.execute("INSERT INTO centers VALUES ('MAD16', 'Madrid Centro', 'Calle inventada 16')")
cursor.execute("INSERT INTO centers VALUES ('BCN03', 'Barcelona Centro', 'Carrer inventat 03')")
cursor.execute("INSERT INTO centers VALUES ('LPA06', 'Las Palmas de Gran Canaria', 'Calle León y Castillo 06')")

# Insertar rutas (activas por defecto = 1)
cursor.execute("INSERT INTO routes VALUES ('MAD16-BCN03-STD-001', 'MAD16', 'BCN03', 1)")
cursor.execute("INSERT INTO routes VALUES ('MAD16-BCN03-EXP-006', 'MAD16', 'BCN03', 1)")
cursor.execute("INSERT INTO routes VALUES ('MAD16-LPA06-STD-003', 'MAD16', 'LPA06', 1)")
cursor.execute("INSERT INTO routes VALUES ('MAD16-LPA06-EXP-009', 'MAD16', 'LPA06', 1)")

# Función de ayuda para insertar envíos y su historial inicial
def insertar_envio(tracking_code, sender, recipient, priority, shipment_type):
    cursor.execute("""
        INSERT INTO shipments (tracking_code, sender, recipient, priority, current_status, shipment_type, assigned_route_id, current_center_id)
        VALUES (?, ?, ?, ?, 'REGISTERED', ?, NULL, NULL)
    """, (tracking_code, sender, recipient, priority, shipment_type))
    
    cursor.execute("""
        INSERT INTO shipment_status_history (tracking_code, status)
        VALUES (?, 'REGISTERED')
    """, (tracking_code,))

insertar_envio("ABC123", "Amazon", "Juan Pérez", 1, "STANDARD")
insertar_envio("EXP456", "Zara", "María López", 2, "STANDARD")
insertar_envio("URG789", "Apple", "Carlos Gómez", 3, "EXPRESS")
insertar_envio("ALB882", "Alibaba", "Victor Aldama", 1, "STANDARD")
insertar_envio("SHN114", "Shein", "Atteneri López", 2, "FRAGILE")

conn.commit()
print("Base de datos creada con datos iniciales.")

# Opcional: Mostrar los datos para verificar
print("\n--- Centers ---")
cursor.execute("SELECT * FROM centers")
for fila in cursor.fetchall():
    print(fila)

print("\n--- Routes ---")
cursor.execute("SELECT * FROM routes")
for fila in cursor.fetchall():
    print(fila)

print("\n--- Shipments ---")
cursor.execute("SELECT * FROM shipments")
for fila in cursor.fetchall():
    print(fila)

conn.close()
print("\nBase de datos guardada en logistica.db")
