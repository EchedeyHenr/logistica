# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-03 (Fase 03: Pruebas Unitarias y Resoluciones de Bugs)

### Added
- **Suite de pruebas unitarias** completa en `logistica/tests/`:
  - `test_shipment.py`
  - `test_shipment_types.py`
  - `test_center.py`
  - `test_route.py`
  - `test_center_service.py`
  - `test_shipment_service.py`
  - `test_route_service.py`
- **Cobertura de código** documentada con `coverage`.
- **docs/README.md** como punto de entrada de la documentación.

### Changed
- Refactorización de **Route** y **Shipment** aplicando principios de agregados de DDD:
  - `Route` delega el instanciamiento de la lógica hacia clases de dominio.
  - `Shipment` expone una factoría `create` y asume su propia carga.
- Nombres de tests modificados (de `TEST_Y_PASOS.md` a `TESTS_Y_PASOS.md`).
- Correcciones menores de indentaciones e inputs en `menu.py` y carga de IDs en variables.

### Fixed
- **Bug crítico de la opción 8**: Corregida captura de punteros vacíos al buscar un envío.
- **Inyección de Dependencias**: Corregida inyección en `CenterService` para utilizar el repositorio correcto.
- **Generación de rutas (opción 3)**: Corregida firma incorrrecta de la funcionalidad en presentación.

## [0.2.0] - 2026-01-28 (Fase 02: Documentación Completa)

### Added
- **Documentación completa del sistema** en `docs/` con 11 archivos detallados:
  - `README.md` - Índice principal de documentación
  - `DESCRIPCION_Y_ALCANCE.md` - Visión general y límites del proyecto (20+ páginas)
  - `EJECUCION.md` - Guías detalladas de instalación y ejecución
  - `ARQUITECTURA_POR_CAPAS.md` - Arquitectura completa con diagramas y dependencias
  - `CASOS_DE_USO.md` - 15 casos de uso documentados con flujos y validaciones
  - `REGLAS_DE_NEGOCIO.md` - 33 reglas de negocio documentadas y organizadas
  - `MODELO_DE_DOMINIO.md` - Modelo completo con 5 entidades, invariantes y colaboraciones
  - `CONTRATO_REPOSITORIO.md` - Contratos e implementaciones de repositorios
  - `DATOS_INICIALES.md` - Datos de seed y configuración para pruebas
  - `TESTS_Y_PASOS.md` - Guía completa de pruebas y verificación (100+ tests)
  - `TROUBLESHOOTING.md` - Solución de problemas y depuración (20+ categorías)
- **Comentarios en el código** centrados en el **por qué** (reglas de negocio, normalización, supuestos y efectos laterales) para aclarar segmentos no obvios
- **README.md principal bilingüe** (inglés/español) con:
  - Descripción general del proyecto
  - Objetivos específicos
  - Entidades principales del dominio
  - Alcance del proyecto
  - Instrucciones de ejecución
  - Workflow de desarrollo
  - Diagramas UML del ciclo de vida
  - Estructura completa del proyecto
- **Diagramas de arquitectura** en formato texto para claridad visual
- **Tablas comparativas** para facilitar la referencia rápida
- **Checklists** para mantenimiento y troubleshooting
- **Ejemplos de código real** integrados en la documentación

### Changed
- **README.md** principal expandido y mejorado para incluir todos los aspectos recogidos en los apuntes sobre documentación
- **Estructura de documentación** reorganizada siguiendo mejores prácticas
- **Documentación de arquitectura** ampliada con diagramas de dependencias y responsabilidades
- **Casos de uso** detallados con flujos principales y alternativos
- **Reglas de negocio** categorizadas y documentadas individualmente
- **Mensajes de error** más descriptivos y consistentes
- **Validaciones** mejoradas con mensajes específicos

### Fixed
- **Documentación inconsistente** - Unificada terminología y formato
- **Referencias cruzadas** - Añadidas entre documentos relacionados
- **Ejemplos de uso** - Mejorados con pasos reales y verificables
- **Inconsistencias en nombres** de métodos y propiedades
- **Validaciones faltantes** en entidades del dominio
- **Manejo de errores** en casos bordes

### Removed
- **Contenido duplicado** entre diferentes documentos

## [0.1.0] - 2026-01-14 (Fase 01: Versión Inicial)

### Added
- **Aplicación base de sistema logístico por capas**:
  - **Capa Presentation**: Menú de consola interactivo en `presentation/menu.py`
  - **Capa Application**: Servicios y casos de uso en `application/`:
    - `shipment_service.py` - Gestión de envíos
    - `route_service.py` - Gestión de rutas
    - `center_service.py` - Gestión de centros logísticos
  - **Capa Domain**: Entidades y reglas de negocio en `domain/`:
    - `shipment.py` - Clase base de envío
    - `fragile_shipment.py` - Envío frágil con prioridad especial
    - `express_shipment.py` - Envío express con prioridad fija
    - `center.py` - Centro logístico con inventario
    - `route.py` - Ruta de transporte entre centros
    - Repositorios abstractos (`*_repository.py`)
  - **Capa Infrastructure**: Implementaciones técnicas en `infrastructure/`:
    - `memory_shipment.py` - Repositorio en memoria para envíos
    - `memory_center.py` - Repositorio en memoria para centros
    - `memory_route.py` - Repositorio en memoria para rutas
    - `seed_data.py` - Datos iniciales para demostración
- **Sistema completo de gestión logística** con:
  - Registro de tres tipos de envíos (Estándar, Frágil, Express)
  - Gestión de centros logísticos y su inventario
  - Creación y administración de rutas de transporte
  - Asignación de envíos a rutas
  - Seguimiento del ciclo de vida de envíos (REGISTERED → IN_TRANSIT → DELIVERED)
  - Sistema de prioridades con reglas específicas por tipo
  - Validación de transiciones de estado
- **Tests unitarios y de integración**:
  - `test_domain_shipments.py` - Validación de reglas de envíos
  - `test_domain_centers.py` - Gestión de centros logísticos
  - `test_domain_routes.py` - Flujo de transporte
  - `test_infra_and_services.py` - Integración completa
  - `test_shipment_logic.py` - Lógica polimórfica
  - `test_robustness.py` - Resiliencia del sistema
- **Características principales implementadas**:
  - Polimorfismo en tipos de envío con comportamientos diferenciados
  - Validación de invariantes del dominio
  - Persistencia en memoria con normalización case-insensitive
  - Relaciones bidireccionales consistentes
  - Historial completo de estados por envío
  - Prevención de operaciones incoherentes

### Arquitectura Implementada
- Separación clara en 4 capas (Presentation, Application, Domain, Infrastructure)
- Inyección de dependencias para desacoplamiento
- Patrón Repository para abstraer la persistencia
- Contratos/interfaces definidos en Domain
- Implementaciones específicas en Infrastructure
- Flujo unidireccional de dependencias

---


## Notas de Versionamiento

### Convenciones
- **Versión 0.x.y**: Versiones de desarrollo, API puede cambiar
- **Versión 1.0.0**: Primera versión estable, API pública congelada
- **Semantic Versioning**: MAJOR.MINOR.PATCH
  - MAJOR: Cambios incompatibles en API
  - MINOR: Nuevas funcionalidades compatibles
  - PATCH: Correcciones de bugs compatibles

### Mantenimiento
- Cada entrega/fase corresponde a una versión MINOR
- Las correcciones críticas se liberan como PATCH
- Las versiones mayores requieren migración documentada

---

## Historial de Cambios Completos

| Versión | Fecha | Estado | Cambios Principales |
|---------|-------|--------|---------------------|
| 0.1.0 | 2026-01-14 | ✅ Completado | Implementación inicial por capas |
| 0.2.0 | 2026-01-28 | ✅ Completado | Documentación completa del sistema |
| 0.3.0 | 2026-03-03 | ✅ Completado | Pruebas unitarias y resoluciones |
| 1.0.0 | Por planificar | 📅 Planeado | Versión estable para producción |

---

## Compatibilidad / Cambios Rompedores

### De 0.1.0 a 0.2.0
- **Sin cambios en API** del código ejecutable
- **Documentación expandida** sin afectar funcionalidad
- **Mejoras en mensajes de error** más descriptivos
- **Validaciones mejoradas** pero compatibles con datos existentes

### Próximos cambios (0.3.0+)
- **Posibles cambios en repositorios** al añadir persistencia real
- **Nuevos endpoints** en API REST
- **Extensiones del modelo de dominio** para nuevas funcionalidades
- **Cambios en interfaces** para soportar autenticación

---

## Autores y Contribuidores

- **Echedey Henríquez Hernández** - [EchedeyHenr](https://github.com/EchedeyHenr)
  - Arquitectura inicial y diseño por capas
  - Implementación completa del dominio
  - Sistema de gestión logística completo
  - Documentación exhaustiva del proyecto

---

## Referencias

- [Keep a Changelog](https://keepachangelog.com/)
- [Semantic Versioning](https://semver.org/)
- [Documentación de Python](https://docs.python.org/)
- [Arquitectura Hexagonal/Ports & Adapters](https://alistair.cockburn.us/hexagonal-architecture/)

---

*Este CHANGELOG se actualiza con cada entrega significativa del proyecto.*