# 📦 Casos de Uso del Sistema Logístico
<hr>

## 📋 Índice de Casos de Uso

### 🔄 Gestión de Envíos
- [UC-01: Registrar Nuevo Envío](#uc-01-registrar-nuevo-envío)
- [UC-02: Consultar Envío Específico](#uc-02-consultar-envío-específico)
- [UC-03: Listar Todos los Envíos](#uc-03-listar-todos-los-envíos)
- [UC-04: Actualizar Estado de Envío](#uc-04-actualizar-estado-de-envío)
- [UC-05: Modificar Prioridad de Envío](#uc-05-modificar-prioridad-de-envío)

### 🏭 Gestión de Centros Logísticos
- [UC-06: Registrar Nuevo Centro](#uc-06-registrar-nuevo-centro)
- [UC-07: Listar Centros Existentes](#uc-07-listar-centros-existentes)
- [UC-08: Consultar Inventario de Centro](#uc-08-consultar-inventario-de-centro)

### 🚛 Gestión de Rutas de Transporte
- [UC-09: Crear Nueva Ruta](#uc-09-crear-nueva-ruta)
- [UC-10: Listar Rutas Disponibles](#uc-10-listar-rutas-disponibles)
- [UC-11: Asignar Envíos a Ruta](#uc-11-asignar-envíos-a-ruta)
- [UC-12: Retirar Envío de Ruta](#uc-12-retirar-envío-de-ruta)
- [UC-13: Despachar Ruta](#uc-13-despachar-ruta)
- [UC-14: Completar Ruta](#uc-14-completar-ruta)

---

## 🔄 Gestión de Envíos

### UC-01: Registrar Nuevo Envío
**ID**: `UC-01`  
**Actor**: Operador Logístico  
**Descripción**: Registrar un nuevo envío en el sistema con sus datos básicos y tipo específico.

#### 📋 Precondiciones
- El operador está autenticado en el sistema (implícito en esta versión)
- No existe otro envío con el mismo código de seguimiento

#### 🔄 Flujo Principal
1. El operador selecciona "Registrar envío" (opción 1)
2. El sistema solicita:
   - Código de seguimiento (único)
   - Remitente
   - Destinatario
   - Prioridad (1, 2 o 3)
   - Tipo de envío (standard, fragile, express)
3. El operador introduce los datos
4. El sistema valida:
   - Código único
   - Datos no vacíos
   - Prioridad válida según tipo
5. El sistema crea el envío con estado `REGISTERED`
6. El sistema confirma el registro exitoso

#### ⚠️ Flujos Alternativos
**FA-01a: Código duplicado**
- En paso 4, si el código ya existe
- Sistema muestra error: "Ya existe un envío con ese código"
- Vuelve al paso 2

**FA-01b: Prioridad inválida para frágil**
- En paso 4, si tipo es `fragile` y prioridad < 2
- Sistema muestra error: "Un envío frágil no puede tener prioridad inferior a 2"
- Vuelve al paso 2

**FA-01c: Tipo de envío inválido**
- En paso 4, si tipo no es `standard`, `fragile` o `express`
- Sistema muestra error: "Tipo de envío no válido"
- Vuelve al paso 2

#### 📋 Postcondiciones
- Un nuevo envío existe en el sistema con estado `REGISTERED`
- El envío tiene un historial con un único estado
- El envío no está asignado a ninguna ruta



### UC-02: Consultar Envío Específico
**ID**: `UC-02`
**Actor**: Operador Logístico
**Descripción**: Obtener información detallada de un envío específico, incluyendo su historial de estados.

#### 📋 Precondiciones
- Existe un envío con el código proporcionado

#### 🔄 Flujo Principal
1. El operador selecciona "Ver detalles de un envío" (opción 6)
2. El sistema solicita código de seguimiento
3. El operador introduce el código
4. El sistema recupera el envío
5. El sistema muestra:
   - Información básica (remitente, destinatario, prioridad, tipo)
   - Estado actual
   - Ruta asignada (si tiene)
   - Historial completo de estados

#### ⚠️ Flujos Alternativos

**FA-02a: Envío no encontrado**
- En paso 4, si no existe el envío
- Sistema muestra error: "No existe el envío con código..."
- Vuelve al menú principal

#### 📋 Postcondiciones

- El operador tiene información completa del envío
- No se modifican datos del sistema

### UC-03: Listar Todos los Envíos

**ID**: `UC-03`
**Actor**: Operador Logístico
**Descripción**: Ver un resumen de todos los envíos en el sistema, ordenados alfabéticamente por código.

#### 📋 Precondiciones
- Ninguna específica (funciona incluso sin envíos)

#### 🔄 Flujo Principal

1. El operador selecciona "Listar envíos" (opción 5)
2. El sistema recupera todos los envíos
3. El sistema ordena por código de seguimiento (case-insensitive)
4. El sistema muestra para cada envío:
   - Código de seguimiento
   - Estado actual
   - Prioridad
   - Tipo de envío
   - Ruta asignada (o "(sin ruta)")

#### ⚠️ Flujos Alternativos

**FA-03a: No hay envíos**
- En paso 2, si no hay envíos
- Sistema muestra lista vacía o mensaje informativo

#### 📋 Postcondiciones

- El operador tiene visión general del estado de todos los envíos
- No se modifican datos del sistema

### UC-04: Actualizar Estado de Envío

**ID**: `UC-04`
**Actor**: Operador Logístico o Sistema Automático
**Descripción**: Cambiar el estado de un envío, siguiendo las transiciones permitidas.

#### 📋 Precondiciones
- Existe el envío con el código proporcionado
- La transición de estado es válida según reglas de negocio

#### 🔄 Flujo Principal
1. El operador selecciona "Actualizar estado de envío" (opción 2)
2. El sistema solicita:
   - Código de seguimiento
   - Nuevo estado (REGISTERED, IN_TRANSIT, DELIVERED)
3. El operador introduce los datos
4. El sistema valida:
   - Existencia del envío
   - Transición válida (REGISTERED→IN_TRANSIT→DELIVERED)
5. El sistema actualiza el estado
6. El sistema registra el cambio en el historial
7. El sistema confirma la actualización

#### ⚠️ Flujos Alternativos

**FA-04a: Transición no permitida**
- En paso 4, si la transición no es válida
- Sistema muestra error: "Transición no permitida: de X a Y"
- Vuelve al paso 2

**FA-04b: Estado inválido**
- En paso 4, si el estado no es uno de los permitidos
- Sistema muestra error: "Estado no válido"
- Vuelve al paso 2

#### 📋 Reglas de Validación

```
VALID_TRANSITIONS = {
    "REGISTERED": ["IN_TRANSIT"],
    "IN_TRANSIT": ["DELIVERED"],
    "DELIVERED": []  # Estado final
}
```

#### 📋 Postcondiciones
- El envío tiene nuevo estado
- El historial del envío incluye el nuevo estado
- Si el estado es DELIVERED, el envío se considera completado

### UC-05: Modificar Prioridad de Envío
**ID**: `UC-05`
**Actor**: Operador Logístico
**Descripción**: Aumentar o disminuir la prioridad de un envío existente, respetando las restricciones por tipo.

#### 📋 Precondiciones
- Existe el envío con el código proporcionado
- La operación es permitida según el tipo de envío

#### 🔄 Flujo Principal (Aumentar)
1. El operador selecciona "Aumentar prioridad del envío" (opción 3)
2. El sistema solicita código de seguimiento
3. El operador introduce el código
4. El sistema valida:
   - Existencia del envío
   - Que se pueda aumentar (no sea express o ya tenga prioridad 3)
   - Que sea frágil y no baje de 2 (si aplica)
5. El sistema aumenta la prioridad en 1
6. El sistema confirma la operación

#### 🔄 Flujo Principal (Disminuir)
1. El operador selecciona "Disminuir prioridad del envío" (opción 4)
2. Seguir pasos 2-6 similares, validando que no baje del mínimo

#### ⚠️ Flujos Alternativos

**FA-05a: Límite alcanzado**
- En paso 4, si el envío ya tiene prioridad máxima/mínima
- Sistema muestra error específico según tipo

**FA-05b: Envío Express**
- En paso 4, si el envío es tipo Express
- Sistema muestra: "Un envío express ya tiene prioridad máxima (3)"

#### 📋 Reglas por Tipo de Envío

| Tipo | Prioridad Inicial | Mínimo | Máximo | ¿Se puede modificar? |
| :--- | :--- | :---: | :---: | :--- |
| **Standard** | Especificada por usuario | 1 | 3 | Sí |
| **Fragile** | $\ge 2$ (valida al crear) | 2 | 3 | Sí, pero no bajo 2 |
| **Express** | Siempre 3 | 3 | 3 | No (fija en 3) |

#### 📋 Postcondiciones
- El envío tiene nueva prioridad
- No se modifica el estado ni otros atributos

## 🏭 Gestión de Centros Logísticos

### UC-06: Registrar Nuevo Centro

**ID**: `UC-06`
**Actor**: Administrador del Sistema
**Descripción**: Agregar un nuevo centro logístico a la red de distribución.

#### 📋 Precondiciones
- No existe otro centro con el mismo ID

#### 🔄 Flujo Principal
1. El operador selecciona "Registrar centro" (opción 7)
2. El sistema solicita:
   - Identificador del centro
   - Nombre del centro
   - Ubicación
3. El operador introduce los datos
4. El sistema valida:
   - ID único
   - Datos no vacíos
5. El sistema crea el centro con inventario vacío
6. El sistema confirma el registro

#### 📋 Postcondiciones
- Nuevo centro disponible en la red
- El centro tiene inventario vacío
- Puede ser usado como origen/destino de rutas

### UC-07: Listar Centros Existentes

**ID**: `UC-07`
**Actor**: Operador Logístico
**Descripción**: Ver todos los centros logísticos registrados en el sistema.

#### 📋 Precondiciones
- Ninguna específica

#### 🔄 Flujo Principal
1. El operador selecciona "Listar centros" (opción 8)
2. El sistema recupera todos los centros
3. El sistema muestra para cada centro:
   - Identificador
   - Nombre
   - Ubicación

#### 📋 Postcondiciones
- Operador tiene visión completa de la red de centros
- No se modifican datos

### UC-08: Consultar Inventario de Centro

**ID**: `UC-08`
**Actor**: Operador Logístico
**Descripción**: Ver qué envíos están actualmente almacenados en un centro específico.

#### 📋 Precondiciones
- Existe el centro con el ID proporcionado

#### 🔄 Flujo Principal
1. El operador selecciona "Ver envíos en un centro" (opción 9)
2. El sistema solicita identificador del centro
3. El operador introduce el ID
4. El sistema valida existencia del centro
5. El sistema recupera la lista de envíos en el centro
6. El sistema muestra los códigos de seguimiento

#### ⚠️ Flujos Alternativos

**FA-08a: Centro no encontrado**
- En paso 4, si no existe el centro
- Sistema muestra error: "No existe un centro con el identificador..."
- Vuelve al paso 2

**FA-08b: Centro vacío**
- En paso 5, si el centro no tiene envíos
- Sistema muestra lista vacía o mensaje informativo

#### 📋 Postcondiciones
- Operador conoce el contenido del centro
- No se modifican datos

## 🚛 Gestión de Rutas de Transporte

### UC-09: Crear Nueva Ruta

**ID**: `UC-09`
**Actor**: Planificador de Rutas
**Descripción**: Definir una nueva ruta de transporte entre dos centros logísticos.

#### 📋 Precondiciones
- Existen ambos centros (origen y destino)
- Los centros son diferentes
- No existe otra ruta con el mismo ID

#### 🔄 Flujo Principal
1. El operador selecciona "Crear ruta" (opción 10)
2. El sistema solicita:
   - Identificador de la ruta
   - ID del centro de origen
   - ID del centro de destino
3. El operador introduce los datos
4. El sistema valida:
   - ID único de ruta
   - Existencia de ambos centros
   - Origen ≠ destino
5. El sistema crea la ruta en estado "Activa"
6. El sistema confirma la creación

#### ⚠️ Flujos Alternativos

**FA-09a: Centros iguales**
- En paso 4, si origen y destino son el mismo
- Sistema muestra: "El centro de origen y destino no pueden ser el mismo"
- Vuelve al paso 2

**FA-09b: Centro no existe**
- En paso 4, si algún centro no existe
- Sistema muestra: "El centro de [origen/destino] no existe"
- Vuelve al paso 2

#### 📋 Postcondiciones
- Nueva ruta disponible en el sistema
- Ruta en estado "Activa" (puede recibir envíos)
- Ruta con lista de envíos vacía

### UC-10: Listar Rutas Disponibles

**ID**: `UC-10`
**Actor**: Operador Logístico
**Descripción**: Ver todas las rutas registradas en el sistema con su información básica.

#### 📋 Precondiciones
- Ninguna específica

#### 🔄 Flujo Principal
1. El operador selecciona "Listar rutas" (opción 11)
2. El sistema recupera todas las rutas
3. El sistema muestra para cada ruta:
   - Identificador
   - Centro de origen
   - Centro de destino
   - Estado (Activa/Finalizada)

#### 📋 Postcondiciones
- Operador conoce la red de rutas disponible
- No se modifican datos

### UC-11: Asignar Envíos a Ruta

**ID**: `UC-11`
**Actor**: Operador Logístico
**Descripción**: Asignar uno o varios envíos simultáneamente a una ruta mediante un input separado por comas.

#### 📋 Precondiciones
- Existen el envío y la ruta
- La ruta está activa
- El envío no está asignado a otra ruta
- El envío está en estado REGISTERED o IN_TRANSIT

#### 🔄 Flujo Principal
1. El operador selecciona "Asignar envíos a una ruta" (opción 12)
2. El sistema solicita:
   - ID de la ruta
   - Códigos de seguimiento separados por comas
3. El operador introduce los datos
4. El sistema valida uno a uno la validez e inyecta la confirmación.
5. El sistema confirma la asignación devolviendo una lista "OK" y "Error".

#### ⚠️ Flujos Alternativos

**FA-11a: Ruta inactiva**
- En paso 4, si la ruta está finalizada
- Sistema muestra en error: "La ruta 'X' no está activa"

**FA-11b: Envío ya asignado**
- En paso 4, si el envío ya tiene ruta
- Sistema expulsa el código bajo la cabecera: "El envío 'X' ya está asignado a una ruta"

#### 📋 Postcondiciones
- Todos los listados exitosos se asignan a la ruta
- Envíos registrados en inventario del centro origen

### UC-12: Retirar Envío de Ruta

**ID**: `UC-12`
**Actor**: Operador Logístico
**Descripción**: Remover un envío de la ruta a la que está asignado.

#### 📋 Precondiciones
- Existen el envío y la ruta
- El envío está asignado a la ruta especificada
- La ruta está activa (o no, según implementación)

#### 🔄 Flujo Principal
1. El operador selecciona "Quitar envío de ruta" (opción 13)
2. El sistema solicita código de seguimiento
3. El operador introduce el código y la ruta.
4. El sistema valida:
   - Existencia del envío
   - Que tenga ruta asignada
5. El sistema retira el envío de la ruta
6. El sistema remueve la asignación del envío
7. El sistema remueve el envío del inventario del centro origen
8. El sistema confirma la operación

#### ⚠️ Flujos Alternativos

**FA-12a: Envío sin ruta**
- En paso 4, si el envío no tiene ruta asignada
- Sistema expulsa fallo indicando que no hay ruta asignada.

#### 📋 Postcondiciones
- Envío sin ruta asignada
- Envío removido del inventario del centro origen
- Ruta actualizada (sin el envío)

### UC-13: Despachar Ruta

**ID**: `UC-13`
**Actor**: Operador Logístico
**Descripción**: Marcar una ruta como "en tránsito", actualizando el estado de sus envíos.

#### 📋 Precondiciones
- Existe la ruta
- La ruta está activa
- La ruta tiene al menos un envío asignado
- La ruta no ha sido ya despachada

#### 🔄 Flujo Principal
1. El operador selecciona "Despachar ruta" (opción 14)
2. El sistema solicita ID de la ruta
3. El operador introduce el ID
4. El sistema valida:
   - Existencia de la ruta
   - Que esté activa
   - Que no haya sido ya despachada
5. Para cada envío en la ruta:
   - Actualiza estado a IN_TRANSIT
   - Remueve del inventario del centro origen
6. El sistema confirma el despacho

#### ⚠️ Flujos Alternativos

**FA-13a: Ruta ya despachada**
- En paso 4, si todos los envíos ya están IN_TRANSIT
- Sistema muestra: "La ruta 'X' ya ha sido despachada"
- Vuelve al paso 2

#### 📋 Postcondiciones
- Todos los envíos de la ruta en estado IN_TRANSIT
- Envíos removidos del inventario del centro origen
- Ruta sigue activa (puede completarse después)

### UC-14: Completar Ruta

**ID**: `UC-14`
**Actor**: Operador Logístico
**Descripción**: Finalizar una ruta, marcando sus envíos como entregados en el centro destino.

#### 📋 Precondiciones
- Existe la ruta
- La ruta está activa
- La ruta ha sido despachada (envíos en IN_TRANSIT)

#### 🔄 Flujo Principal
1. El operador selecciona "Completar ruta" (opción 15)
2. El sistema solicita ID de la ruta
3. El operador introduce el ID
4. El sistema valida:
   - Existencia de la ruta
   - Que esté activa
5. Para cada envío en la ruta:
   - Actualiza estado a DELIVERED
   - Agrega al inventario del centro destino
6. La ruta se marca como "Finalizada"
7. La lista de envíos de la ruta se vacía
8. El sistema confirma la finalización

#### ⚠️ Flujos Alternativos

**FA-14a: Ruta ya finalizada**
- En paso 4, si la ruta ya está finalizada
- Sistema muestra: "La ruta 'X' ya se encuentra finalizada"
- Vuelve al paso 2

#### 📋 Postcondiciones
- Todos los envíos de la ruta en estado DELIVERED
- Envíos agregados al inventario del centro destino
- Ruta marcada como "Finalizada" (inactiva)
- Ruta vacía (sin envíos asignados)

## 🎯 Resumen de Operaciones del Menú

| Opción | Caso de Uso | Actor Principal | Precondiciones Clave |
| :--- | :--- | :--- | :--- |
| **1** | UC-01: Crear Envío | Operador | Código único |
| **2** | UC-04: Cambiar Estado | Operador/Sistema | Transición válida |
| **3** | UC-05: Aumentar Prioridad | Operador | No sea Express, no sea prioridad 3 |
| **4** | UC-05: Disminuir Prioridad | Operador | No sea prioridad 1 (o 2 si frágil) |
| **5** | UC-03: Listar Envíos | Operador | - |
| **6** | UC-02: Consultar Envío | Operador | Envío existente |
| **7** | UC-06: Crear Centro | Administrador | ID único de centro |
| **8** | UC-07: Listar Centros | Operador | - |
| **9** | UC-08: Consultar Centro | Operador | Centro existente |
| **10** | UC-09: Crear Ruta | Planificador | Centros existentes y diferentes |
| **11** | UC-10: Listar Rutas | Operador | - |
| **12** | UC-11: Asignar a Ruta | Operador | Ruta activa |
| **13** | UC-12: Quitar de Ruta | Operador | Envío asignado a ruta |
| **14** | UC-13: Despachar Ruta | Operador | Ruta activa con envíos |
| **15** | UC-14: Finalizar Ruta | Operador | Ruta activa despachada |
| **16** | Salir del Sistema | Todos | - |

## ⚠️ Errores Representativos y Su Significado

| Error | Causa Probable | Solución |
| :--- | :--- | :--- |
| **"Ya existe un envío con el código..."** | Código de seguimiento duplicado | Usar un código diferente |
| **"Transición no permitida: de X a Y"** | Secuencia de estados incorrecta | Seguir: REGISTERED → IN_TRANSIT → DELIVERED |
| **"La ruta 'X' no está activa."** | Ruta finalizada o no existe | Usar ruta activa o crear una nueva |
| **"Un envío frágil no puede tener prioridad inferior a 2."** | Violación de regla de negocio | Usar prioridad 2 o 3 para envíos frágiles |
| **"Un envío express ya tiene prioridad máxima."** | Express siempre tiene prioridad 3 | No intentar modificar prioridad de Express |
| **"El centro de origen y destino no pueden ser el mismo."** | Error de coherencia lógica | Seleccionar centros diferentes |
| **"El envío 'X' ya está asignado a una ruta."** | El envío ya tiene una asignación | Retirar de la ruta actual primero (opción 13) |
| **"No hay ruta asignada para eliminar."** | El envío no estaba en ninguna ruta | Verificar estado del envío (opción 6) |
| **"No se puede aumentar/disminuir la prioridad..."** | Límites de prioridad alcanzados | Consultar las reglas por tipo de envío |
| **"No existe un centro con el identificador..."** | Centro no registrado | Verificar el ID o registrar el centro (opción 7) |

