# 🏎️ F1 Stats Lab & Race Tracker

¡Bienvenido a **F1 Stats Lab**! Esta es una aplicación web interactiva desarrollada en Python y Streamlit que combina la pasión por la Fórmula 1 con el registro y seguimiento de competencias personales de karting o simuladores.

👉 **[Hacé clic acá para probar la aplicación en vivo](https://f1-stats-lab-cterlagos-f1-stats.streamlit.app/#f1-historico-and-actualidad)** 🚀

---

## 🌟 Características Principales

### 🔍 1. Buscador Histórico y Actualidad de F1
* **Búsqueda inteligente de pilotos:** Sistema adaptado con un traductor interno de alias (ej: ingresando "Checo" busca a "Pérez", "Kimi" busca a "Antonelli", etc.).
* **Historial de temporadas:** Conexión en tiempo real con la API de F1 (`jolpi.ca/ergast`) para consultar dinámicamente las temporadas en las que compitió un piloto y seleccionar el año específico.
* **Fichas técnicas personalizadas de pilotos:** Interfaz visual estilizada con HTML/CSS que muestra la escudería, número, posición en el mundial y puntos del año seleccionado, acompañado de la foto del piloto.

### 🏁 2. Panel del Corredor (Estadísticas y Telemetría)
* **Perfil de Piloto:** Registro y edición de perfil local (Nombre, Apellido, Escudería/Club).
* **Base de Datos Local (SQL):** Integración con una base de datos relacional para registrar carreras (tipo de evento, circuito, posición de llegada y puntos sumados).
* **Visualizador de Métricas:** Panel interactivo que calcula automáticamente las estadísticas acumuladas (puntos totales, carreras disputadas) e historial de competencias del usuario de forma inmediata.

---

## 🛠️ Tecnologías y Conceptos Aplicados

* **Frontend:** [Streamlit](https://streamlit.io/) — para la creación rápida de la interfaz de usuario web.
* **Lenguaje:** Python 3 — estructurado con modularización de código.
* **Bases de Datos:** SQLite / SQL — para la persistencia del perfil y carreras del usuario.
* **Consumo de APIs:** Librería `requests` de Python para peticiones HTTP de datos dinámicos.
* **UX/UI Customizada:** Inyección de CSS y HTML interactivo para el fondo de pantalla estilizado y diseño de tarjetas dinámicas.
* **Manejo de Estado Complejo:** Implementación avanzada de `st.session_state` y control manual del ciclo de vida de la aplicación (`st.rerun()`) para sincronizar de forma instantánea el ingreso de datos en los formularios con el panel de estadísticas.

---

## 🚀 Cómo ejecutar el proyecto de forma local

1. Cloná este repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/TU_REPOSITORIO.git](https://github.com/TU_USUARIO/TU_REPOSITORIO.git)
