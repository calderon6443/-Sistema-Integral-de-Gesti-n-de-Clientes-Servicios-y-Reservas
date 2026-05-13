# 🏢 Sistema Integral de Gestión de Clientes, Servicios y Reservas

Sistema integral orientado a objetos para la gestión de clientes, servicios y reservas. Desarrollado en Python puro, sin uso de bases de datos, aplicando los principios fundamentales de la Programación Orientada a Objetos.

---

## 👥 Equipo de desarrollo

> - Carlos Alberto Calderon

---

## 📋 Descripción general

La empresa ofrece tres tipos de servicios:

- 🏠 **Reserva de salas** — Salas de reuniones y conferencias con opciones de proyector y control de aforo.
- 💻 **Alquiler de equipos** — Equipos tecnológicos por horas con gestión de stock y seguro opcional.
- 🎓 **Asesorías especializadas** — Consultoría con expertos en diferentes niveles (junior, senior, principal).

---

## 🗂️ Estructura del proyecto

```
proyecto/
│
├── entidades.py       # Clase abstracta base (EntidadBase)
├── excepciones.py     # Excepciones personalizadas del sistema
├── logger.py          # Sistema de registro de eventos y errores
├── cliente.py         # Clase Cliente con encapsulación y validaciones
├── servicios.py       # Clase abstracta Servicio + 3 clases derivadas
├── reserva.py         # Clase Reserva con ciclo de vida completo
├── gestor.py          # Controlador central del sistema
├── main.py            # Punto de entrada y simulación de operaciones
├── .gitignore
└── README.md
```

---

## ⚙️ Requisitos

- Python **3.10** o superior (se usan anotaciones de tipo modernas como `X | None`)
- No requiere librerías externas ni bases de datos

---

## 🚀 Cómo ejecutar

```bash
# 1. Clona el repositorio
git clone https://github.com/TU_USUARIO/sistema-gestion.git

# 2. Entra a la carpeta
cd sistema-gestion

# 3. Ejecuta el sistema
python main.py
```

Al finalizar, se genera automáticamente el archivo `eventos.log` con el registro de todos los eventos y errores de la sesión.

---

## 🏗️ Arquitectura y principios POO

### Abstracción
`EntidadBase` (en `entidades.py`) es la clase abstracta raíz. Define los métodos `describir()` y `validar()` que todas las entidades del sistema deben implementar obligatoriamente.

### Herencia
```
EntidadBase
├── Cliente
└── Servicio (abstracta)
    ├── ReservaSala
    ├── AlquilerEquipo
    └── AsesoriaEspecializada
```

### Encapsulación
La clase `Cliente` protege sus atributos con prefijo `_` y los expone únicamente mediante propiedades con validación. Ningún atributo sensible es modificable directamente desde fuera de la clase.

### Polimorfismo
Cada servicio sobreescribe el método `calcular_costo()` con lógica propia:
- `ReservaSala` aplica recargo por aforo mayor a 20 personas y costo de proyector.
- `AlquilerEquipo` multiplica por cantidad de unidades y aplica seguro opcional.
- `AsesoriaEspecializada` ajusta el precio según el nivel del experto e incluye informe opcional.

### Métodos sobrecargados (simulados)
La clase `Reserva` expone tres variantes del cálculo de costo:

```python
reserva.calcular_costo()                                  # Con IVA y descuento del cliente
reserva.calcular_costo_sin_iva()                          # Sin IVA
reserva.calcular_costo_con_descuento_personalizado(0.25)  # Descuento arbitrario
```

---

## 🚨 Manejo de excepciones

### Excepciones personalizadas (en `excepciones.py`)

| Excepción | Descripción |
|---|---|
| `ClienteYaExisteError` | ID de cliente duplicado |
| `ClienteNoEncontradoError` | Cliente no registrado en el sistema |
| `DatosClienteInvalidosError` | Campo de cliente con valor inválido |
| `ServicioNoDisponibleError` | Servicio inactivo o en mantenimiento |
| `ServicioNoEncontradoError` | Servicio no existe en el catálogo |
| `ParametroServicioInvalidoError` | Parámetro requerido inválido o faltante |
| `ReservaYaConfirmadaError` | Intento de reconfirmar una reserva |
| `ReservaCanceladaError` | Operación sobre reserva cancelada |
| `DuracionInvalidaError` | Duración menor al mínimo permitido |
| `CostoInconsistenteError` | Resultado de cálculo negativo o incoherente |
| `OperacionNoPermitidaError` | Acción no permitida en el estado actual |
| `LogError` | Fallo al escribir en el archivo de log |

### Bloques utilizados

```python
# try / except / else / finally — usado en Reserva.confirmar()
try:
    costo = self.calcular_costo()
except ServicioNoDisponibleError as e:
    logger.error(...)
    raise
else:
    self._estado = "CONFIRMADA"   # solo si no hubo excepción
finally:
    logger.info(...)              # siempre se ejecuta

# Encadenamiento de excepciones — usado en main.py
try:
    horas = float(valor_externo)
except ValueError as e:
    raise DuracionInvalidaError(valor_externo) from e
```

---

## 📊 Operaciones simuladas en `main.py`

El archivo `main.py` ejecuta **18 operaciones** que demuestran el comportamiento del sistema ante entradas válidas e inválidas:

| # | Operación | Resultado esperado |
|---|---|---|
| 1 | Registrar cliente válido (premium) | ✔ Éxito |
| 2 | Registrar cliente válido (corporativo) | ✔ Éxito |
| 3 | Cliente con email inválido | ✘ `DatosClienteInvalidosError` |
| 4 | Cliente con nombre con números | ✘ `DatosClienteInvalidosError` |
| 5 | Cliente con ID duplicado | ✘ `ClienteYaExisteError` |
| 6 | Agregar 5 servicios válidos | ✔ Éxito |
| 7 | Servicio con precio negativo | ✘ `ParametroServicioInvalidoError` |
| 8 | Desactivar un servicio | ✔ Servicio marcado como no disponible |
| 9 | Reserva y confirmación exitosa | ✔ Costo calculado con IVA y descuento |
| 10 | Reserva sobre servicio desactivado | ✘ `ServicioNoDisponibleError` |
| 11 | Reserva con duración de 0.1 horas | ✘ `DuracionInvalidaError` |
| 12 | Alquiler de equipos con seguro | ✔ Éxito |
| 13 | Asesoría nivel senior con informe | ✔ Éxito |
| 14 | Cancelar reserva confirmada | ✔ Cancelación registrada |
| 15 | Reconfirmar reserva ya confirmada | ✘ `ReservaYaConfirmadaError` |
| 16 | Reserva para cliente inexistente | ✘ `ClienteNoEncontradoError` |
| 17 | Encadenamiento de excepciones | ✘ `DuracionInvalidaError` desde `ValueError` |
| 18 | Asesoría con nivel de experto inválido | ✘ `ParametroServicioInvalidoError` |

---

## 📄 Archivo de logs

Cada ejecución genera o actualiza `eventos.log` con el siguiente formato:

```
[2026-05-13 01:10:26] [EVENT] [CLIENTE_REGISTRADO] CLI001 | Ana Gómez | premium
[2026-05-13 01:10:26] [EVENT] [RESERVA_CONFIRMADA] RES-0001 | Costo: $310,590.00 COP
[2026-05-13 01:10:26] [ERROR] [ERR_RESERVA] La reserva 'RES-0001' ya fue confirmada previamente.
```

El sistema **nunca se detiene** ante errores — todos se capturan, se registran en el log y la ejecución continúa.

---

## 📦 Tecnologías

- **Lenguaje:** Python 3.10+
- **Paradigma:** Programación Orientada a Objetos
- **Persistencia:** Ninguna (todo en memoria con `dict` y `list`)
- **Logging:** Archivo de texto plano (`.log`)
- **Librerías:** Solo módulos de la biblioteca estándar (`abc`, `re`, `datetime`)

---

## 📝 Licencia

Proyecto académico — uso educativo.
