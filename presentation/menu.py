# presentation/menu.py
from logisticaEnvios.application.shipment_service import ShipmentService
from logisticaEnvios.infrastructure.memory_shipment import ShipmentRepositoryMemory
from logisticaEnvios.infrastructure.seed_data import seed_repository

def mostrar_menu():
    print("\n=== LOGÍSTICA - GESTIÓN DE ENVÍOS ===")
    print("1. Registrar envío")
    print("2. Asignar envío a ruta")
    print("3. Quitar envío de ruta")
    print("4. Actualizar estado de envío")
    print("5. Aumentar prioridad")
    print("6. Disminuir prioridad")
    print("7. Listar envíos")
    print("8. Ver detalles de un envío")
    print("9. Salir")

def main():
#    repo = ShipmentRepositoryMemory()
    repo = seed_repository()
    servicio = ShipmentService(repo)

    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ").strip()

        try:
            if opcion == "1":
                tracking_code = input("Código de seguimiento: ").strip()
                sender = input("Remitente: ").strip()
                recipient = input("Destinatario: ").strip()
                priority = int(input("Prioridad (1-normal, 2-media, 3-alta): ").strip() or 1)
                servicio.register_shipment(tracking_code, sender, recipient, priority)
                print(f"✔ Envío {tracking_code} registrado con éxito.")

            elif opcion == "2":
                tracking_code = input("Código de seguimiento: ").strip()
                route_id = input("ID de ruta: ").strip()
                servicio.assign_shipment_to_route(tracking_code, route_id)
                print(f"✔ Envío {tracking_code} asignado a la ruta {route_id}.")

            elif opcion == "3":
                tracking_code = input("Código de seguimiento: ").strip()
                servicio.remove_shipment_from_route(tracking_code)
                print(f"✔ Envío {tracking_code} eliminado de su ruta.")

            elif opcion == "4":
                tracking_code = input("Código de seguimiento: ").strip()
                new_status = input("Nuevo estado (REGISTERED, IN_TRANSIT, DELIVERED): ").strip().upper()
                servicio.update_shipment_status(tracking_code, new_status)
                print(f"✔ Estado del envío {tracking_code} actualizado a {new_status}.")

            elif opcion == "5":
                tracking_code = input("Código de seguimiento: ").strip()
                servicio.increase_shipment_priority(tracking_code)
                print(f"✔ Prioridad del envío {tracking_code} aumentada.")

            elif opcion == "6":
                tracking_code = input("Código de seguimiento: ").strip()
                servicio.decrease_shipment_priority(tracking_code)
                print(f"✔ Prioridad del envío {tracking_code} disminuida.")

            elif opcion == "7":
                envios = servicio.list_shipments()
                if not envios:
                    print("(No hay envíos registrados)")
                else:
                    print("\nListado de envíos:")
                    for tracking_code, status, priority, route in envios:
                        route_str = route if route else "(sin ruta)"
                        print(f"- {tracking_code} | Estado: {status} | Prioridad: {priority} | Ruta: {route_str}")

            elif opcion == "8":
                tracking_code = input("Código de seguimiento del envío: ").strip()
                shipment = servicio._repo.get_by_tracking_code(tracking_code)
                if shipment is None:
                    print(f"No existe el envío {tracking_code}.")
                else:
                    print(f"\nDetalles del envío {tracking_code}:")
                    print(f"Remitente: {shipment.sender}")
                    print(f"Destinatario: {shipment.recipient}")
                    print(f"Prioridad: {shipment.priority}")
                    print(f"Estado actual: {shipment.current_status}")
                    route_str = shipment.assigned_route if shipment.assigned_route else "(sin ruta)"
                    print(f"Ruta asignada: {route_str}")
                    print("Historial de estados:")
                    for i, estado in enumerate(shipment.get_status_history(), start=1):
                        print(f"  {i}. {estado}")

            elif opcion == "9":
                print("Hasta luego.")
                break

            else:
                print("Opción no válida.")

        except ValueError as e:
            print("X " + str(e))


if __name__ == "__main__":
    main()
