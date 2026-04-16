# presentation/menu.py

from logistica.application.shipment_service import ShipmentService
from logistica.application.route_service import RouteService
from logistica.application.center_service import CenterService
from logistica.infrastructure.seed_data import seed_repository
from logistica.infrastructure.errores import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PersistenceError
)


def mostrar_menu():
    print("\n=== LOGÍSTICA - GESTIÓN DE ENVÍOS ===")
    print("\n=== APARTADO - ENVÍOS ===")
    print("1. Registrar envío")
    print("2. Actualizar estado de envío")
    print("3. Aumentar prioridad del envío")
    print("4. Disminuir prioridad del envío")
    print("5. Listar envíos")
    print("6. Ver detalles de un envío")
    print("\n=== APARTADO - CENTROS LOGÍSTICOS ===")
    print("7. Registrar centro logístico")
    print("8. Listar centro logístico")
    print("9. Ver envíos en un centro")
    print("\n=== APARTADO - RUTAS ===")
    print("10. Crear ruta")
    print("11. Listar rutas")
    print("12. Asignar envíos a una ruta")
    print("13. Quitar envío de ruta")
    print("14. Despachar ruta")
    print("15. Completar ruta")
    print("\n16. Salir")


def main():
    repositories = seed_repository()

    shipment_service = ShipmentService(repositories["shipments"])
    route_service = RouteService(
        repositories["routes"],
        repositories["shipments"],
        repositories["centers"]
    )
    center_service = CenterService(
        repositories["centers"],
        repositories["shipments"]
    )

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()


        try:
            if opcion == "1":
                tracking_code = input("Código de seguimiento (3 letras + 3 dígitos, ej. ABC123): ").strip()
                sender = input("Remitente: ").strip()
                recipient = input("Destinatario: ").strip()
                priority = int(input("Prioridad (1-normal, 2-media, 3-alta): ").strip() or 1)
                shipment_type = input("Tipo de envío (standard / fragile / express): ").strip().lower()

                shipment_service.register_shipment(tracking_code, sender, recipient, priority, shipment_type)
                print(f"✔ Envío {tracking_code} registrado con éxito.")


            elif opcion == "2":
                tracking_code = input("Código de seguimiento: ").strip()
                new_status = input("Nuevo estado (REGISTERED, IN_TRANSIT, DELIVERED): ").strip().upper()

                shipment_service.update_shipment_status(tracking_code, new_status)
                print(f"✔ Estado del envío {tracking_code} actualizado a {new_status}.")


            elif opcion == "3":
                tracking_code = input("Código de seguimiento: ").strip()
                shipment_service.increase_shipment_priority(tracking_code)
                print(f"✔ Prioridad del envío {tracking_code} aumentada.")


            elif opcion == "4":
                tracking_code = input("Código de seguimiento: ").strip()
                shipment_service.decrease_shipment_priority(tracking_code)
                print(f"✔ Prioridad del envío {tracking_code} disminuida.")


            elif opcion == "5":
                envios = shipment_service.list_shipments()
                for code, status, priority, shipment_type, route in envios:
                    route_str = route or "(sin ruta)"
                    print(f"- {code:<10} | {status:^13} | P:{priority:<2} | {shipment_type:<10} | Ruta: {route_str}")


            elif opcion == "6":
                tracking_code = input("Código de seguimiento del envío: ").strip()
                shipment = shipment_service.get_shipment(tracking_code)

                if shipment is None:
                    print(f"X No se encontró el envío {tracking_code}.")
                else:
                    print(f"\nDetalles del envío {tracking_code.upper()}:")
                    print(f"Remitente: {shipment.sender}")
                    print(f"Destinatario: {shipment.recipient}")
                    print(f"Prioridad: {shipment.priority}")
                    print(f"Tipo de envío: {shipment.shipment_type}")
                    print(f"Estado actual: {shipment.current_status}")
                    route_str = shipment.assigned_route if shipment.assigned_route else "(sin ruta)"
                    print(f"Ruta asignada: {route_str}")
                    print("\n=== Historial de estados ===")
                    for i, estado in enumerate(shipment.get_status_history(), start=1):
                        print(f"  {i}. {estado}")


            elif opcion == "7":
                center_id = input("Identificador del centro (3-4 letras y 2 dígitos, ej. MAD01): ").strip()
                center_name = input("Nombre del centro logístico: ").strip()
                location_name = input("Ubicación del centro logístico: ").strip()

                center_service.register_center(center_id, center_name, location_name)
                print(f"✔ Centro {center_id} registrado con éxito.")


            elif opcion == "8":
                centers = center_service.list_centers()

                for center_id, center_name, center_location in centers:
                    print(f"- {center_id:<8} | {center_name:^30} | Ubicación: {center_location}")


            elif opcion == "9":
                center_id = input("Identificador del centro logístico: ").strip()
                shipments_in_center = center_service.list_shipments_in_center(center_id)

                print(f"\n=== Envios en el Centro {center_id.upper()} ===")

                for i, shipment in enumerate(shipments_in_center, start=1):
                    print(f"  {i}. {shipment.tracking_code}")


            elif opcion == "10":
                route_id = input("Identificador de la ruta (formato ORIGEN-DESTINO-STD|FRG|EXP-999, ej. MAD01-BCN02-EXP-001): ").strip()
                origin_center_id = input("Identificador del centro de origen: ").strip()
                destination_center_id = input("Identificador del centro de destino: ").strip()

                route_service.create_route(route_id, origin_center_id, destination_center_id)
                print(f"✔ Ruta {route_id} registrada con éxito.")


            elif opcion == "11":
                routes = route_service.list_routes()

                for route_id, origin_center_id, destination_center_id, status in routes:
                    print(f"- {route_id:<18} | Origen: {origin_center_id:<8} | Destino: {destination_center_id:<8} | Estado: {status:^13}")


            elif opcion == "12":
                route_id = input("Identificador de la ruta: ").strip()
                tracking_code = input("Introduce un código de envío, o varios separados por comas: ")
                tracking_codes = [
                    code.strip().upper()
                    for code in tracking_code.split(",")
                    if code.strip()
                ]

                assigned_tracking_codes, failed_assignments = [], []

                for code in tracking_codes:
                    try:
                        route_service.assign_shipment_to_route(code, route_id)
                        assigned_tracking_codes.append(code)
                    except (ValueError, EntityAlreadyExistsError, EntityNotFoundError, PersistenceError) as e:
                        failed_assignments.append((code, str(e)))

                print("\n=== Resumen de asignación ===")

                if assigned_tracking_codes:
                    print("✔ Envíos asignados correctamente:")
                    for code in assigned_tracking_codes:
                        print(f"  - {code}")

                if failed_assignments:
                    print("✖ Envíos con error:")
                    for code, error in failed_assignments:
                        print(f"  - {code}: {error}")


            elif opcion == "13":
                tracking_code = input("Código de seguimiento: ").strip()
                route_id = input("ID de ruta: ").strip()
                route_service.remove_shipment_from_route(tracking_code, route_id)
                print(f"✔ Envío {tracking_code} eliminado de la ruta {route_id}.")


            elif opcion == "14":
                route_id = input("Identificador de la ruta: ").strip()
                route_service.dispatch_route(route_id)
                print(f"✔ La ruta {route_id} está en transito.")


            elif opcion == "15":
                route_id = input("Identificador de la ruta: ").strip()
                route_service.complete_route(route_id)
                print(f"✔ La ruta {route_id} se ha completado correctamente.")


            elif opcion == "16":
                print("Hasta luego.")
                break


            else:
                print("Opción no válida.")


        except (ValueError, EntityAlreadyExistsError, EntityNotFoundError, PersistenceError) as e:
            print("X " + str(e))


if __name__ == "__main__":
    main()
