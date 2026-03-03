# Revisión del proyecto — Echedey Henríquez Hernández

**Fuente de verdad:** rama `03-testing` → raíz del repositorio `logistica/`
**Fases detectadas:** 01 (capas), 02 (documentación), 03 (testing) — en rama `03-testing`

---

## REVISIÓN FASE 01 - 2026-03-03 — Nota: 8.5/10

### Cumple

- Repositorio creado y compartido en GitHub (`EchedeyHenr/logistica`).
- `README.md` presente con descripción bilingüe (inglés/español), objetivos, instrucciones de ejecución, diagramas UML del ciclo de vida y estructura del proyecto.
- El proyecto está organizado correctamente en capas: `domain/`, `application/`, `infrastructure/`, `presentation/`.
- Estructura de ficheros correcta: paquetes con `__init__.py`, módulos bien separados.
- POO aplicado con solidez:
  - **Encapsulamiento:** atributos privados con doble guión bajo (`__tracking_code`, `__sender`, etc.) y propiedades de solo lectura con `@property`.
  - **Herencia:** `FragileShipment` y `ExpressShipment` extienden `Shipment`.
  - **Polimorfismo:** cada subtipo sobreescribe `increase_priority`, `decrease_priority` y la propiedad `shipment_type` con comportamiento diferenciado.
- Contratos de repositorio definidos en `domain/` (clases base con `NotImplementedError`) e implementaciones en `infrastructure/`.
- Menú con 17 opciones organizadas en tres apartados (envíos, centros, rutas).
- Inyección de dependencias en los servicios (constructor injection).
- Identificadores significativos y conformes a PEP8.

### Errores y aspectos a mejorar

- **[BUG] `presentation/menu.py:76` — La opción 3 ("Quitar envío de ruta") falla en tiempo de ejecución.** Se llama `route_service.remove_shipment_from_route(tracking_code)` con un solo argumento, pero el método requiere dos: `tracking_code` y `route_id`. Al elegir esta opción el programa lanzará un `TypeError` y crasheará.
  - *Cómo resolverlo:* Añade un `input` para pedir el ID de la ruta y pásalo como segundo argumento: `route_service.remove_shipment_from_route(tracking_code, route_id)`.

- **[BUG] `presentation/menu.py:43-46` — `CenterService` recibe el repositorio de rutas en lugar del de envíos.** El constructor `CenterService(center_repo, shipment_repo)` espera un repositorio de envíos como segundo argumento, pero el menú le pasa `repos["routes"]`. Todas las operaciones del servicio que accedan al repositorio de envíos (opciones 9, 10, 11) funcionarán de forma incorrecta o lanzarán errores.
  - *Cómo resolverlo:* Cambia `repos["routes"]` por `repos["shipments"]` en la línea 45.

- **[DISEÑO] Lógica de negocio en la capa de aplicación.** El `ShipmentService` decide qué clase instanciar según el tipo de envío (`standard` → `Shipment`, `fragile` → `FragileShipment`, `express` → `ExpressShipment`). También, `RouteService.dispatch_route()` evalúa si una ruta "ya fue despachada" comprobando el estado de sus envíos. Ambas son reglas del dominio, no de la capa de aplicación.
  - *Cómo resolverlo:* La decisión de qué tipo de envío crear puede delegarse a un método de fábrica en el dominio (p.ej. `Shipment.create(tipo, ...)`). La condición de "ya despachada" debería estar en `Route` y lanzar una excepción que el servicio simplemente deje pasar.

- **[DISEÑO] Doble fuente de verdad entre `Route._shipments` y los repositorios.** `Route` mantiene internamente la lista de envíos asignados, y los mismos objetos `Shipment` viven también en el repositorio de envíos. Esta duplicación puede generar inconsistencias si un envío se modifica a través de una vía sin que la otra lo refleje.
  - *Cómo resolverlo:* La entidad `Route` debería almacenar solo los códigos de seguimiento de los envíos asignados (referencias) y delegar la consulta de sus datos al repositorio cuando sea necesario.


## REVISIÓN FASE 02 - 2026-03-03 — Nota: 8/10

### Cumple

- Docstrings de módulo en los ficheros de dominio (`shipment.py`, `center.py`, `route.py`, etc.) y en la capa de infraestructura (`memory_shipment.py`, etc.).
- Docstrings en todas las clases y métodos públicos del dominio y de la aplicación, con descripción, parámetros, retorno y excepciones.
- Reglas de negocio referenciadas por código en los comentarios (p.ej. `RN-010`, `RN-034`, `RN-016`), vinculando el código con la documentación.
- Bloques no evidentes comentados con el **porqué** (no el qué): por qué se devuelve copia, por qué se usa lista en lugar de dict, supuestos de diseño y efectos laterales.
- `README.md` muy completo: bilingüe, diagramas UML, estructura del proyecto, instrucciones de ejecución y testing.
- `CHANGELOG.md` presente en la raíz del repositorio con entradas `[0.1.0]` y `[0.2.0]` correctamente formateadas.
- Carpeta `docs/` con los documentos: `DESCRIPCION_Y_ALCANCE.md`, `EJECUCION.md`, `ARQUITECTURA_POR_CAPAS.md`, `CASOS_DE_USO.md`, `REGLAS_DE_NEGOCIO.md`, `MODELO_DE_DOMINIO.md`, `CONTRATO_REPOSITORIO.md`, `DATOS_INICIALES.md`, `TROUBLESHOOTING.md`.

### Errores y aspectos a mejorar

- **Falta `docs/README.md`.** que sirva de índice de la documentación.

- **El fichero de tests se llama `TEST_Y_PASOS.md` en lugar de `TESTS_Y_PASOS.md` (falta la `S`).** Es un error menor de nombre pero el fichero debe llamarse `TESTS_Y_PASOS.md`.
  - *Cómo resolverlo:* Renómbralo con `git mv docs/TEST_Y_PASOS.md docs/TESTS_Y_PASOS.md`.

- **[IMPORTANTE] `echedey/logistica/main.py` está vacío pero el README lo presenta como punto de entrada**

- **[IMPORTANTE] `docs/EJECUCION.md` usa IDs con formato antiguo en los ejemplos.** El apartado "Flujo rápido de ejemplo" usa identificadores como `VAL-01`, `MAD-16` y `BCN-03`, pero el sistema ahora exige el formato `VAL01`, `MAD16`, `BCN03` (3-4 letras + 2 dígitos, sin guión). Quien siga estos ejemplos obtendrá un `ValueError` al registrar los centros.

- **`infrastructure/seed_data.py` no tiene docstring de módulo ni de la función `seed_repository`**

- **README documenta un fichero que no existe: `echedey/logistica/README.md:280` y `echedey/logistica/README.md:533` mencionan `domain/shipment_types.py`, pero en `domain/` no existe ese módulo.

- **[DISEÑO] `domain/route.py:185` — El método `list_shipment` está en singular cuando debería estar en plural.** Por convención, los métodos que devuelven colecciones se nombran en plural (`list_shipments`), igual que el método equivalente en `Center` (`list_shipments()`).
  - *Cómo resolverlo:* Renombra el método a `list_shipments` y actualiza todas las llamadas que lo usen (incluyendo en `route_service.py`).

#### Nombres que no siguen recomendaciones

- **`presentation/menu.py:35` — variable `repos` (abreviatura)**. Es un diccionario de repositorios y el nombre no deja claro el significado. Renombra a `repositories`, `repositorios` o `repositorios_por_tipo`.
- **`presentation/menu.py:102` — `s_type` abreviatura rara.** Renómbralo a `shipment_type` (o `tipo_envio`) y ajusta el `print`.
- **`presentation/menu.py:137` — `c_id`, `c_name`, `c_location` son abreviaturas.** Aunque se entienden, pierdes intención y consistencia con el resto de variables (`center_id`, etc.).Renómbralas a `center_id`, `center_name`, `center_location` (o en español, pero consistente).
- **`presentation/menu.py:176` — `assigned` y `failed` son nombres demasiado genéricos.** En realidad representan listas de resultados de asignación. Renómbralas a `assigned_tracking_codes` y `failed_assignments` (o equivalentes en español).
- **`infrastructure/seed_data.py:28` — `route_01`/`route_02` no describen intención.** Los números no aportan información sobre qué ruta es. Usa nombres por dominio, por ejemplo `route_mad16_bcn03_standard` o `route_mad16_lpa06_express`.
- **`infrastructure/seed_data.py:38` — `envio1..envio5` mezcla idioma + numeración sin intención.** En el resto del código usas términos en inglés (`Shipment`, `Route`, etc.), pero aquí están en español. Mantén consistencia: o todo en inglés (`shipment_amazon_standard`, `shipment_apple_express`, …) o todo en español, pero sin numeración opaca.


## REVISIÓN FASE 03 - 2026-03-03 — Nota: 8.5/10

### Cumple

- Tests reorganizados en subcarpeta `logistica/tests/` con `__init__.py`.
- Tests escritos con `unittest.TestCase` para todas las capas: dominio, servicios de aplicación e infraestructura:
  - `test_shipment.py`, `test_shipment_types.py`, `test_center.py`, `test_route.py`
  - `test_center_service.py`, `test_shipment_service.py`, `test_route_service.py`
- **Todos los 117 tests pasan** con `python3 -m unittest discover -s logistica/tests`.
- `requirements.txt` incluye `coverage==7.13.4` como dependencia declarada.
- `docs/TEST_Y_PASOS.md` describe los tests existentes y los comandos de ejecución.

### Errores y aspectos a mejorar

- **[IMPORTANTE] `CHANGELOG.md` no tiene entrada para la versión `0.3.0`.** 

- **[IMPORTANTE] `docs/EJECUCION.md` no incluye los pasos para ejecutar `coverage`.** El documento describe cómo arrancar la aplicación pero no cómo correr los tests ni generar el informe de cobertura, que es un requisito de esta fase.
  - *Cómo resolverlo:* Añade una sección con los comandos necesarios:
    ```bash
    # Ejecutar tests
    python3 -m unittest discover -s logistica/tests
    # Ejecutar con coverage
    coverage run -m unittest discover -s logistica/tests
    coverage report
    coverage html
    ```

- **[IMPORTANTE] El fichero se llama `TEST_Y_PASOS.md` en lugar de `TESTS_Y_PASOS.md` (falta la `S`).** Mismo punto que en Fase 02. Renómbralo con `git mv docs/TEST_Y_PASOS.md docs/TESTS_Y_PASOS.md`.
.
