from flask import Flask, redirect, url_for
from logistica.infrastructure.seed_data import seed_repository
from logistica.application.shipment_service import ShipmentService
from logistica.application.route_service import RouteService
from logistica.application.center_service import CenterService
from logistica.infrastructure.errores import EntityNotFoundError, EntityAlreadyExistsError, PersistenceError

app = Flask(__name__)

repos = seed_repository(use_sqlite=True)
shipment_service = ShipmentService(repos["shipments"])
center_service = CenterService(repos["centers"], repos["shipments"])
route_service = RouteService(repos["routes"], repos["shipments"], repos["centers"])

@app.errorhandler(EntityNotFoundError)
def handle_not_found(error):
    return str(error), 404

@app.errorhandler(EntityAlreadyExistsError)
def handle_already_exists(error):
    return str(error), 409

@app.errorhandler(ValueError)
def handle_value_error(error):
    return str(error), 400

@app.errorhandler(PersistenceError)
def handle_persistence_error(error):
    return str(error), 500

@app.route("/")
def bienvenida():
    return (
        "<h1>Bienvenido al sistema de logística</h1>"
        "<p>Consultas:</p>"
        "<ul>"
        f"<li><a href='{url_for('listar_envios')}'>/shipments</a>: lista todos los envíos</li>"
        f"<li><a href='{url_for('list_centers')}'>/centers</a>: lista todos los centros logísticos</li>"
        f"<li><a href='{url_for('list_routes')}'>/routes</a>: lista todas las rutas</li>"
        "</ul>"
    )


# === RUTAS DE ENVÍOS ===
@app.route("/shipments")
def listar_envios():
    envios = shipment_service.list_shipments()
    if not envios:
        return "No hay envíos registrados."
    lineas = [
        f"{tracking_code} — Estado: {current_status} — Prioridad: {priority} — Tipo: {shipment_type} — Ruta: {assigned_route or '(sin ruta)'}"
        for tracking_code, current_status, priority, shipment_type, assigned_route in envios
    ]
    return "<br>".join(lineas)

@app.route("/shipments/<string:tracking_code>")
def get_shipment(tracking_code):
    shipment = shipment_service.get_shipment(tracking_code)
    historial = "<br>&nbsp;&nbsp;- ".join([""] + shipment.get_status_history()) if shipment.get_status_history() else ""
    return (f"Detalles del envío {tracking_code}:<br>"
            f"Remitente: {shipment.sender}<br>"
            f"Destinatario: {shipment.recipient}<br>"
            f"Tipo: {shipment.shipment_type}<br>"
            f"Prioridad: {shipment.priority}<br>"
            f"Estado: {shipment.current_status}<br>"
            f"Ruta asignada: {shipment.assigned_route or '(sin ruta)'}<br>"
            f"Historial:{historial}")

# Ruta con prioridad 1 por defecto, o con prioridad elegida.
@app.route("/shipments/nuevo/<string:tracking_code>/<string:tipo>/<string:sender>/<string:recipient>")
@app.route("/shipments/nuevo/<string:tracking_code>/<string:tipo>/<int:priority>/<string:sender>/<string:recipient>")
def register_shipment(tracking_code, tipo, sender, recipient, priority=1):
    shipment_service.register_shipment(tracking_code, sender, recipient, priority=priority, shipment_type=tipo)
    return redirect(url_for('listar_envios'))

@app.route("/shipments/<string:tracking_code>/estado/<string:nuevo_estado>")
def update_shipment_status(tracking_code, nuevo_estado):
    shipment_service.update_shipment_status(tracking_code, nuevo_estado)
    return redirect(url_for('get_shipment', tracking_code=tracking_code))

@app.route("/shipments/<string:tracking_code>/prioridad/aumentar")
def increase_shipment_priority(tracking_code):
    shipment_service.increase_shipment_priority(tracking_code)
    return redirect(url_for('get_shipment', tracking_code=tracking_code))

@app.route("/shipments/<string:tracking_code>/prioridad/disminuir")
def decrease_shipment_priority(tracking_code):
    shipment_service.decrease_shipment_priority(tracking_code)
    return redirect(url_for('get_shipment', tracking_code=tracking_code))


# === RUTAS DE CENTROS ===
@app.route("/centers")
def list_centers():
    centers = center_service.list_centers()
    if not centers:
        return "No hay centros registrados."
    lineas = [
        f"{center_id} — {name} — Ubicación: {location}"
        for center_id, name, location in centers
    ]
    return "<br>".join(lineas)

@app.route("/centers/<string:center_id>/shipments")
def list_shipments_in_center(center_id):
    shipments = center_service.list_shipments_in_center(center_id)
    if not shipments:
        return f"No hay envíos en el centro {center_id}."
    return "<br>".join(s.tracking_code for s in shipments)

@app.route("/centers/nuevo/<string:center_id>/<string:nombre>/<string:ciudad>")
def register_center(center_id, nombre, ciudad):
    center_service.register_center(center_id, nombre, ciudad)
    return redirect(url_for('list_centers'))


# === RUTAS DE RUTAS LOGÍSTICAS ===
@app.route("/routes")
def list_routes():
    routes = route_service.list_routes()
    if not routes:
        return "No hay rutas registradas."
    lineas = [
        f"{route_id} — Origen: {origin_center_id} — Destino: {destination_center_id} — Estado: {status}"
        for route_id, origin_center_id, destination_center_id, status in routes
    ]
    return "<br>".join(lineas)

@app.route("/routes/<string:route_id>/shipments")
def route_shipments(route_id):
    shipments = route_service.list_shipments_in_route(route_id)
    if not shipments:
        return f"No hay envíos asignados a la ruta {route_id}."
    return "<br>".join(shipments)

@app.route("/routes/nuevo/<string:route_id>/<string:center_origen>/<string:center_destino>/<string:tipo>")
def create_route(route_id, center_origen, center_destino, tipo):
    route_service.create_route(route_id, center_origen, center_destino)
    return redirect(url_for('list_routes'))

@app.route("/routes/<string:route_id>/asignar/<string:tracking_code>")
def assign_shipment(route_id, tracking_code):
    route_service.assign_shipment_to_route(tracking_code, route_id)
    return redirect(url_for('route_shipments', route_id=route_id))

@app.route("/routes/<string:route_id>/quitar/<string:tracking_code>")
def remove_shipment(route_id, tracking_code):
    route_service.remove_shipment_from_route(tracking_code, route_id)
    return redirect(url_for('route_shipments', route_id=route_id))

@app.route("/routes/<string:route_id>/despachar")
def dispatch_route(route_id):
    route_service.dispatch_route(route_id)
    return redirect(url_for('list_routes'))

@app.route("/routes/<string:route_id>/completar")
def complete_route(route_id):
    route_service.complete_route(route_id)
    return redirect(url_for('list_routes'))

if __name__ == "__main__":
    app.run(debug=True)
