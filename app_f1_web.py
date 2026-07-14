# PARA ABRIR LA PAG WEB ↓↓↓
# cd "c:\Users\Usuario\Desktop\CURSO DE PYTHON D\EJERCICIOS\PROYECTOS"
#python -m streamlit run app_f1_web.py


import base64
import os
import requests
import streamlit as st
import dbF1app 

db = dbF1app.BaseDeDatosF1()

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="F1 Stats Lab", page_icon="🏎️", layout="centered")

def set_fondo(image_file):
    with open(image_file, "rb") as f:
        img_data = f.read()
    
    # Convertimos la imagen local a un format que el CSS entienda
    b64_string = base64.b64encode(img_data).decode()
    
    # Este es el código CSS que "pinta" el fondo en toda la aplicación
    st.markdown(
        f"""
        <style>
        /* 🎯 Apuntamos al contenedor exacto de la app */
        [data-testid="stAppViewContainer"] {{
            /* Mezclamos el oscurecido (60%) y la imagen todo junto para que no falle */
            background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                              url("data:image/jpg;base64,{b64_string}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        
        /* 🔓 Volvemos transparente la barra de arriba para que no tape el fondo */
        [data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0) !important;
        }}
        
        /* Aseguramos la legibilidad de los textos principales */
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stSubheader, p {{
            color: white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True    
    ) 
    
carpeta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_imagen = os.path.join(carpeta_actual, "fotos_f1", "background.jpg")  

try:
    set_fondo(ruta_imagen)
except FileNotFoundError:
    st.warning("⚠️ No se encontró el archivo 'background.jpg' para el fondo. Verificá que esté en la carpeta del proyecto.")


# --- TU DICCIONARIO DE ALIASES ---
TRADUCTOR_PILOTOS = {
    "verstappen": "max_verstappen",
    "max": "max_verstappen",
    "checo": "perez",
    "lewis": "hamilton",
    "schumacher": "michael_schumacher",
    "senna": "senna",
    "ayrton": "senna",
    "fangio": "fangio",
    "kimi": "antonelli",
}


# --- 🛠️ APARTADO DE LÓGICA (FUNCIONES) ---

def buscar_piloto(apellido_piloto, anio):
    apellido_limpio = apellido_piloto.lower().strip()
    apellido_api = TRADUCTOR_PILOTOS.get(apellido_limpio, apellido_limpio)

    # Armamos la URL según el año
    temporada = "current" if anio == "Actual" else anio
    url = f"https://api.jolpi.ca/ergast/f1/{temporada}/drivers/{apellido_api}/driverStandings.json"

    try:
        res = requests.get(url)
        if res.status_code == 200:
            datos = res.json()
            listas = datos["MRData"]["StandingsTable"]["StandingsLists"]
            if listas:
                info_campeonato = listas[0]["DriverStandings"][0]
                info_piloto = info_campeonato["Driver"]
                return info_campeonato, info_piloto, apellido_api
    except Exception as e:
        st.error(f"Error de conexión: {e}")

    return None, None, apellido_api


def obtener_temporadas_piloto(apellido_api):
    """Viaja a la API y devuelve una lista con todos los años que corrió el piloto"""
    url = f"https://api.jolpi.ca/ergast/f1/drivers/{apellido_api}/seasons.json"
    try:
        respuesta = requests.get(url)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            lista_seasons = datos["MRData"]["SeasonTable"]["Seasons"]
            anios = [item["season"] for item in lista_seasons]
            return anios
    except Exception as e:
        print(f"Error al buscar temporadas: {e}")
    return []


# --- 📺 APARTADO VISUAL (INTERFAZ UI) ---

col_menu, _ = st.columns([2, 1])
with col_menu:
    opcion_menu = st.radio(
        "",  
        ["🔍 Buscador Histórico", "🏁 Mi Perfil de Corredor"],
        horizontal=True
    )

st.markdown("---")


# =====================================================================
# 📂 SECCIÓN 1: BUSCADOR HISTÓRICO & ACTUALIDAD
# =====================================================================
if opcion_menu == "🔍 Buscador Histórico":
    st.title("🏎️ F1 Histórico & Actualidad")
    st.write("Buscá las estadísticas de tus pilotos favoritos y reviví la historia...")
    
    apellido_ingresado = st.text_input(
        "¿Qué piloto buscás? (Ej: Verstappen, Senna, Colapinto)"
    )

    if apellido_ingresado:
        apellido_limpio = apellido_ingresado.lower().strip()
        apellido_api = TRADUCTOR_PILOTOS.get(apellido_limpio, apellido_limpio)

        with st.spinner("Buscando temporadas en el archivo histórico..."):
            anios_competidos = obtener_temporadas_piloto(apellido_api)

        if anios_competidos:
            anio_seleccionado = st.selectbox(
                "📅 Seleccioná el año:",
                options=anios_competidos,
                index=len(anios_competidos) - 1,
            ) 
            
            # 🎯 EL BOTÓN ÚNICO Y DEFINITIVO
            if st.button("Buscar Piloto 🏁", key="boton_definitivo_f1"):
                with st.spinner("Conectando con los servidores de F1..."):
                    info_camp, info_piloto, driver_id = buscar_piloto(
                        apellido_ingresado, anio_seleccionado
                    )

                if info_camp and info_piloto:
                    st.success("¡Datos encontrados!")

                    col1, col2 = st.columns([1, 2])

                    with col1:
                        # 🖼️ LÓGICA DE LA FOTO
                        carpeta_del_proyecto = os.path.dirname(os.path.abspath(__file__))
                        apellido_archivo = apellido_ingresado.lower().strip()

                        ruta_png = os.path.join(carpeta_del_proyecto, "fotos_f1", f"{apellido_archivo}.png")
                        ruta_jpg = os.path.join(carpeta_del_proyecto, "fotos_f1", f"{apellido_archivo}.jpg")

                        if os.path.exists(ruta_png):
                            st.image(ruta_png, use_container_width=True)
                        elif os.path.exists(ruta_jpg):
                            st.image(ruta_jpg, use_container_width=True)
                        else:
                            ruta_incognito = os.path.join(carpeta_del_proyecto, "fotos_f1", "anonimo.png")
                            if os.path.exists(ruta_incognito):
                                st.image(ruta_incognito, use_container_width=True)
                            else:
                                st.warning("No se encontró la foto del piloto ni la silueta de respaldo.")

                    with col2:
                        st.markdown(f"""
                            <p style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                            <span style="font-size: 45px; color: #8cc6ff; font-weight: 650;">{info_piloto['givenName']} {info_piloto['familyName']}</span>
                            </p>
                            <p style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 5px;">
                            <span style="font-size: 24px; color: #ff4b4b; font-weight: 300;">Piloto N°:</span> 
                            <span style="font-size: 32px; color: #8cc6ff; font-weight: 300; letter-spacing: 1px;">{info_piloto.get('permanentNumber', 'N/A')}</span>
                            </p>
                            <p style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 5px;">
                            <span style="font-size: 24px; color: #ff4b4b; font-weight: 300;">Escudería:</span> 
                            <span style="font-size: 32px; color: #8cc6ff; font-weight: 300; letter-spacing: 1px;">{info_camp['Constructors'][0]['name']}</span>
                            </p>
                            <p style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 5px;">
                            <span style="font-size: 24px; color: #ff4b4b; font-weight: 300;">Posición en el Mundial:</span> 
                            <span style="font-size: 32px; color: #8cc6ff; font-weight: 300; letter-spacing: 1px;">{info_camp['position']}º</span>
                            </p>
                            <p style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin-bottom: 2px;">
                            <span style="font-size: 24px; color: #ff4b4b; font-weight: 300;">Puntos:</span> 
                            <span style="font-size: 32px; color: #8cc6ff; font-weight: 300; letter-spacing: 1px;">{info_camp['points']}</span>
                            </p>
                        """, unsafe_allow_html=True)
                else:
                    st.warning(f"No se encontraron registros para '{apellido_ingresado}' en la temporada {anio_seleccionado}.")
        else:
            st.warning("No se encontraron temporadas. Verificá que el apellido esté bien escrito.")
            
# =====================================================================
# 📂 SECCIÓN 2: MI PERFIL DE CORREDOR
# =====================================================================
elif opcion_menu == "🏁 Mi Perfil de Corredor":
    st.title("🏁 Mi Perfil de Corredor")
    st.write("Gestioná tu carrera, registrá telemetría de tus carreras y seguí tus estadísticas en tiempo real.")
    
    perfil = db.obtener_perfil() 
    
    tab_panel, tab_registrar, tab_config = st.tabs([
        "📊 Mi Panel y Estadísticas", 
        "✍️ Registrar Carrera", 
        "⚙️ Configurar Perfil"
    ])
    
    # PESTAÑA 1: MI PANEL Y ESTADÍSTICAS
    with tab_panel:
        if not perfil:
            st.warning("⚠️ Todavía no creaste tu perfil. Andá a la pestaña **'⚙️ Configurar Perfil'** para arrancar.")
        else:
            st.markdown(f"### 🏎️ Piloto: {perfil[0]} {perfil[1]}")
            st.markdown(f"**Escudería / Club:** {perfil[2]}")
            st.divider()
            
            carreras = db.obtener_mis_carreras()
            
            if not carreras:
                st.info("Aún no registraste carreras propias. ¡Salí a la pista y sumá kilómetros!")
            else:
                total_carreras = len(carreras)
                total_puntos = sum(c[3] for c in carreras)
                
                m1, m2 = st.columns(2)
                with m1:
                    st.metric(label="🏁 Carreras Disputadas", value=total_carreras)
                with m2:
                    st.metric(label="🏆 Puntos Totales", value=f"{total_puntos} pts")
                
                st.write("#### 📜 Historial de Competencias")
                
                for c in carreras:
                    emoji_tipo = "🎮" if c[0] == "Simulador" else "🏎️"
                    st.markdown(f"{emoji_tipo} **{c[0]}** en *{c[1]}* — **Puesto:** {c[2]}° | 🪙 **+{c[3]} pts**")

    # PESTAÑA 2: REGISTRAR TELEMETRÍA / CARRERA
    with tab_registrar:
        if not perfil:
            st.error("⚠️ Primero debés configurar tu perfil para poder registrar carreras.")
        else:
            st.subheader(f"Registrar nueva carrera para {perfil[0]}")
            
            # 🔔 NUEVO: Revisamos si dejamos una nota en memoria para mostrar el cartel de éxito
            if "guardado_ok" in st.session_state and st.session_state["guardado_ok"]:
                st.success("¡Datos guardados con éxito en tu base de datos!")
                st.session_state["guardado_ok"] = False # Limpiamos la nota para que no aparezca siempre
            
            with st.expander("💡 Ver sistema de puntuación de referencia (Estilo F1)"):
                st.write("Podés usar esta tabla oficial como guía para asignar tus puntos:")
                tabla_puntos = {
                    "Posición de Llegada": ["1°", "2°", "3°", "4°", "5°", "6°", "7°", "8°", "9°", "10°"],
                    "Puntos Otorgados": [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
                }
                st.table(tabla_puntos)
                st.caption("ℹ️ *Tip: Si lograste la Vuelta Rápida y terminaste en el Top 10, podés sumarte 1 punto extra.*")
            
            with st.form("form_carrera", clear_on_submit=True):
                tipo_evento = st.selectbox("Tipo de evento:", ["Simulador", "Karting"])
                circuito = st.text_input("Nombre del Circuito:").strip().capitalize()
                
                col_pos, col_pts = st.columns(2)
                with col_pos:
                    posicion = st.number_input("Posición de llegada:", min_value=1, step=1, value=1)
                with col_pts:
                    puntos = st.number_input("Puntos sumados:", min_value=0, step=1, value=0)
                
                boton_guardar_carrera = st.form_submit_button("Guardar en Base de Datos 💾")
                
                if boton_guardar_carrera:
                    if circuito:
                        # 1. Guardamos en la base de datos
                        db.registrar_carrera_propia(tipo_evento, circuito, int(posicion), int(puntos))
                        
                        # 2. 📝 Dejamos anotado en la memoria que salimos campeones
                        st.session_state["guardado_ok"] = True
                        
                        # 3. 🔄 Forzamos el rerun instantáneo para actualizar el marcador
                        st.rerun()
                    else:
                        st.error("Por favor, ingresá el nombre de circuito.")
    
    # PESTAÑA 3: CONFIGURAR / EDITAR PERFIL
    with tab_config:
        st.subheader("Configurá tus datos de Piloto")
        
        nombre_def = perfil[0] if perfil else ""
        apellido_def = perfil[1] if perfil else ""
        equipo_def = perfil[2] if perfil else ""
        
        nombre = st.text_input("Tu Nombre:", value=nombre_def).strip().capitalize()
        apellido = st.text_input("Tu Apellido:", value=apellido_def).strip().capitalize()
        equipo = st.text_input("Tu Escudería / Club de Karting:", value=equipo_def).strip().capitalize()
        
        if st.button("Guardar Perfil Local 💾"):
            if nombre and apellido and equipo:
                db.guardar_perfil(nombre, apellido, equipo)
                st.success("¡Tu perfil local fue guardado con éxito!")
                st.rerun()
            else:
                st.error("Por favor, completá todos los campos para guardar tu perfil.")