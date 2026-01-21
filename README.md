# PROYECTO: Sistema de Gestión de Expediciones y Envíos (Logística)


### Descripción general

El proyecto consiste en el diseño y desarrollo de un sistema para la gestión integral de envíos y logística de paquetería, orientado al control de almacenes, la clasificación de mercancías y el seguimiento del ciclo de vida de las expediciones.
El sistema modela una red logística compuesta por centros de distribución donde se reciben, clasifican y despachan paquetes. Cada envío se gestiona según su naturaleza y urgencia, lo que condiciona su prioridad, el tipo de transporte asignado y las reglas de validación en cada estado.
Asimismo, el sistema asegura la trazabilidad total de cada bulto, desde que se registra en el almacén de origen hasta que se confirma su entrega final, garantizando que solo se realicen transiciones de estado coherentes y que se respeten las restricciones de seguridad y manejo de cada tipo de carga.

La propuesta se centra en describir el comportamiento y las reglas del dominio logístico, sin entrar en detalles técnicos ni decisiones de implementación, de forma que el diseño sea independiente de la tecnología utilizada.

### Objetivos

* **Objetivo general**:
  Desarrollar un sistema modular y extensible que permita gestionar de forma coherente el flujo logístico de expediciones y el control de inventario en centros de distribución.

* **Objetivos específicos**:

  * Gestionar diferentes tipos de envíos con reglas de transporte y prioridades diferenciadas mediante herencia y polimorfismo.
  * Controlar los estados de las expediciones garantizando un flujo lógico y trazable.
  * Modelar la infraestructura de centros logísticos y su capacidad de almacenamiento.
  * Implementar validaciones de negocio que impidan operaciones incoherentes (ej. entregar un paquete no enviado).


### Características principales

El sistema se articula en torno a varias entidades principales del dominio, entre las que destacan el Envío, el Centro Logístico y la Ruta de Transporte, las cuales colaboran entre sí para gestionar el ciclo completo de una expedición, desde su registro hasta su entrega final.

#### Centros Logísticos y Almacenamiento

* El sistema permitirá registrar centros de distribución con datos como código identificador, ubicación y capacidad operativa.
* Cada centro mantiene un registro de los paquetes que se encuentran físicamente en sus instalaciones.
* Se podrá consultar el volumen de carga actual de un centro para determinar si puede recibir nuevas expediciones.

#### Tipología de Envíos (Jerarquía de Clases)

El sistema gestionará una clase base de la que heredarán al menos tres tipos especializados, cada uno con comportamiento propio:

  * **Envío Estándar**: Sigue rutas convencionales y tiene una prioridad base.
  * **Envío Exprés**: Posee un atributo de "Tiempo de Entrega Garantizado". Su lógica de prioridad es superior y tiene restricciones de tiempo en cada estado.
  * **Envío Frágil/Especial**: Incluye protocolos de manejo (ej. "No apilar") y requiere una validación adicional de "Seguro de Carga" antes de ser despachado.

Mediante polimorfismo, cada tipo de envío implementará su propio método para calcularCosteLogistico() y validarRequisitosDespacho().

#### Ciclo de Vida y Gestión de Estados

Las expediciones deben pasar por estados estrictos para asegurar la coherencia:

* **Registrado**: El paquete está en el sistema pero no ha llegado al almacén.
* **En Almacén (Origen)**: Recibido y clasificado, listo para tránsito.
* **En Tránsito**: Vinculado a un vehículo o ruta de transporte.
* **En Reparto (Destino)**: En el último tramo para la entrega.
* **Entregado**: Finalización exitosa del ciclo.
* **Incidencia/Retenido**: Estado especial ante problemas (dirección incorrecta, rotura, etc.).


#### Operaciones de Logística

* **Asignación de Rutas**: Vincular uno o varios envíos a un manifiesto de transporte.
* **Actualización de Estado**: Cambiar la situación de un envío validando que el cambio es permitido (ej. no se puede pasar de "Registrado" a "En Reparto" directamente).
* **Gestión de Carga**: Registrar la entrada y salida de bultos en los centros de distribución para mantener el inventario sincronizado.

#### Acciones y consultas disponibles

Los operadores logísticos interactúan con el sistema para registrar, consultar y actualizar la información de las expediciones y centros de distribución. El sistema permitirá realizar, entre otras, las siguientes acciones:

* Registrar nuevas expediciones definiendo remitente, destinatario, tipo de bulto y destino.
* Consultar el historial completo de estados (trazabilidad) de un código de seguimiento.
* Listar todos los paquetes que se encuentran actualmente en un centro logístico específico.
* Cambiar masivamente el estado de paquetes asignados a una ruta de transporte.
* Generar un informe de rendimiento (envíos entregados vs. envíos con incidencia).


### Alcance del proyecto

#### Incluye

* Modelado de clases para Centros, Envíos (con su jerarquía), Rutas y Usuarios (Operadores).
* Lógica de negocio para el cálculo de costes y prioridades según el tipo de envío.
* Sistema de validación de estados para evitar transiciones imposibles.
* Gestión de la ubicación actual de cada paquete en la red.

#### No incluye

* Integración con APIs externas de mapas o GPS para seguimiento en tiempo real.
* Pasarela de pagos real para los costes de envío.
* Gestión de flota vehicular (mantenimiento de camiones, consumo de combustible).
* Interfaz de usuario compleja (se centra en la lógica de dominio y consola).

Este alcance permite desarrollar un sistema coherente y completo a nivel de lógica de negocio, manteniendo una complejidad adecuada al nivel del curso.

## Arbol del proyecto

```
📦logistica
 ┣ 📜__init__.py
 ┣ 📜main.py
 ┣ 📂presentation
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜menu.py
 ┣ 📂application
 ┃ ┣ 📜__init__.py
 ┃ ┗ 📜services.py           # Lógica para crear rutas y asignarles envíos
 ┣ 📂domain
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜shipment.py           # Clase base "Envio"
 ┃ ┣ 📜shipment_types.py     # EnvioEstandar, EnvioExpress, EnvioFragil
 ┃ ┣ 📜center.py             # Clase CentroLogistico (donde se originan las rutas)
 ┃ ┣ 📜route.py              # Clase Ruta (agrupa envios y gestiona el transporte
 ┃ ┗ 📜repository.py
 ┗ 📂infrastructure
   ┣ 📜__init__.py
   ┗ 📜memory.py             # Repositorios para Envios, Centros y Rutas
```

