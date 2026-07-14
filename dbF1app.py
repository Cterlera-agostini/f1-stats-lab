import sqlite3
import requests

class BaseDeDatosF1:
    def __init__(self, nombre_base_datos="f1_app.db"):
        self.nombre_bd = nombre_base_datos
        self.crear_tablas()

    def conectar(self):
        return sqlite3.connect(self.nombre_bd)

    def crear_tablas(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        # 1. Tabla para el perfil del usuario (Vos como piloto)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS perfil_usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                equipo TEXT NOT NULL
            )
        """)
        
        # 2. Tabla para tu historial de carreras (Simulador o Karting)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mis_carreras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_evento TEXT NOT NULL, -- 'Simulador' o 'Karting'
                circuito TEXT NOT NULL,
                posicion INTEGER NOT NULL,
                puntos INTEGER DEFAULT 0
            )
        """)
        conexion.commit()
        conexion.close()

    # --- MÉTODOS DE PERSISTENCIA LOCAL ---
    def guardar_perfil(self, nombre, apellido, equipo):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM perfil_usuario")  # Resetea para tener solo un perfil activo
        cursor.execute("""
            INSERT INTO perfil_usuario (nombre, apellido, equipo) 
            VALUES (?, ?, ?)
        """, (nombre, apellido, equipo))
        conexion.commit()
        conexion.close()

    def obtener_perfil(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, apellido, equipo FROM perfil_usuario LIMIT 1")
        perfil = cursor.fetchone()
        conexion.close()
        return perfil

    def registrar_carrera_propia(self, tipo, circuito, posicion, puntos):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO mis_carreras (tipo_evento, circuito, posicion, puntos) 
            VALUES (?, ?, ?, ?)
        """, (tipo, circuito, posicion, puntos))
        conexion.commit()
        conexion.close()

    def obtener_mis_carreras(self):
        conexion = self.conectar()
        cursor = conexion.cursor()
        cursor.execute("SELECT tipo_evento, circuito, posicion, puntos FROM mis_carreras ORDER BY id DESC")
        carreras = cursor.fetchall()
        conexion.close()
        return carreras


# === FUNCIÓN PARA CONSULTAR LA API DE INTERNET (JOLPICA F1) ===
def buscar_piloto_F1_en_web(apellido_piloto, anio="Actual"):
    
    apellido_limpio = apellido_piloto.lower().strip()
    
    # 🗺️ TABLA DE TRADUCCIÓN (Diccionario de Aliases)
    # De un lado ponés lo que puede escribir el usuario, del otro lo que quiere la API
    TRADUCTOR_PILOTOS = {
        "verstappen": "max_verstappen",
        "max": "max_verstappen",
        "checo": "perez",
        "lewis": "hamilton",
        "schumacher": "michael_schumacher",
        "franco": "colapinto",
        "lando": "norris" 
    }
    

    apellido_limpio = TRADUCTOR_PILOTOS.get(apellido_limpio, apellido_limpio)

    # Si por alguna razón llega vacío, aseguramos que sea el actual
    anio_limpio = str(anio).strip()
    if not anio_limpio or anio_limpio.lower() == "current":
        anio_limpio = "Actual"
        
    texto_temporada = "la temporada actual" if anio_limpio == "Actual" else f"el año {anio_limpio}"
    print(f"\nConectando con los servidores de F1 para buscar a '{apellido_piloto}' en {texto_temporada}...")
        
    texto_temporada = "la temporada actual" if anio_limpio == "Actual" else f"el año {anio_limpio}"
    print(f"\nConectando con los servidores de F1 para buscar a '{apellido_piloto}' en {texto_temporada}...")
    
    anio_url = "current" if anio_limpio == "Actual" else anio_limpio
    
    url = f"https://api.jolpi.ca/ergast/f1/{anio_url}/drivers/{apellido_limpio}/driverstandings.json"
    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        respuesta = requests.get(url, headers=cabeceras, timeout=15)
        
        if respuesta.status_code == 200:
            datos = respuesta.json()
            listado = datos["MRData"]["StandingsTable"]["StandingsLists"]
            
            if not listado or not listado[0]["DriverStandings"]:
                print(f" ⚠️ No se encontraron registros para '{apellido_piloto}' en {texto_temporada}.")
                return
                
            info_campeonato = listado[0]["DriverStandings"][0]
            
            puntos = info_campeonato.get("points", "0")
            posicion = info_campeonato.get("position", "N/A")
            victorias = info_campeonato.get("wins", "0")
            
            info_piloto = info_campeonato["Driver"]
            nombre_completo = f"{info_piloto.get('givenName', '')} {info_piloto.get('familyName', '')}"
            nacionalidad_piloto = info_piloto.get("nationality", "Desconocida")
            fecha_nacimiento = info_piloto.get("dateOfBirth", "No disponible")
            
            numero_piloto = info_piloto.get("permanentNumber", "N/A")
            info_escuderia = info_campeonato["Constructors"][0]
            nombre_escuderia = info_escuderia.get("name", "Desconocida")
            nacionalidad_escuderia = info_escuderia.get("nationality", "Desconocida")
            
            print("\n" + "="*45)
            print(f"🏎️  FICHA DE RENDIMIENTO - TEMPORADA: {anio_limpio.upper()}")
            print(f"👤 PILOTO: {nombre_completo.upper()}")
            print("="*45)
            print(f"👤 Nacionalidad: {nacionalidad_piloto}")
            print(f"📅 Nacimiento: {fecha_nacimiento}")
            print("-"*45)
            print(f"🔢 Número Dorsal Registrado: {numero_piloto}")
            print(f"🏁 Escudería: {nombre_escuderia} ({nacionalidad_escuderia})")
            print(f"📊 Posición Mundial: N° {posicion}")
            print(f"🏆 Puntos en el Campeonato: {puntos} pts")
            print(f"🥇 Carreras ganadas este año: {victorias}")
            print("="*45 + "\n")
            
        elif respuesta.status_code == 400:
            print(" ❌ Error 400: Consulta inválida. Revisá el apellido o el año ingresado.")
        else:
            print(f" ❌ Error de servidor: Código {respuesta.status_code}")
            
    except Exception as error_real:
        print(f" ❌ Error de conexión: {error_real}")

# === BUCLE PRINCIPAL DE LA APP ===
db = BaseDeDatosF1()
""""
#while True:
#    print("\n=====================================")
#    print("      F1 HYBRID APP: PILOT PORTAL    ")
    print("=====================================")
    print("1 Buscar rendimiento de un piloto (Temporada Actual)")
    print("2 Archivo Histórico: Buscar piloto en años anteriores")
    print("3. Crear/Editar Mi Perfil de Corredor")
    print("4. Registrar Mi Última Carrera (Simulador/Karting)")
    print("5. Ver Mi Tablero Personal de Estadísticas")
    print("6. Salir")
    
    opcion = input("\nSeleccioná una opción (1-6): ").strip()

    if opcion == "1":
        print("\n--- BÚSQUEDA TEMPORADA ACTUAL ---")
        apellido = input("Ingresá el apellido del piloto: ")
        buscar_piloto_F1_en_web(apellido, anio="Actual")
        
        #apellido = input("\nApellido del piloto de F1 (ej: Colapinto, Alonso, Verstappen): ").strip()
        #if apellido:
        #    buscar_piloto_F1_en_web(apellido)
        
    elif opcion == "2":
        # Opción histórica: exige obligatoriamente ambos datos
        print("\n--- ARCHIVO HISTÓRICO DE F1 ---")
        apellido = input("Ingresá el apellido del piloto: ")
        anio_historico = input("¿Qué año querés consultar? (Ej: 2004, 2012, 2024): ")
        
        # Validamos rápido que no ponga cualquier cosa
        if anio_historico.isdigit():
            buscar_piloto_F1_en_web(apellido, anio=anio_historico)
        else:
            print(" ❌ Por favor, ingresá un año válido de 4 números.")   
                 
    elif opcion == "3":
        print("\n--- CONFIGURAR MI PERFIL ---")
        nombre = input("Tu Nombre: ").strip().capitalize()
        apellido = input("Tu Apellido: ").strip().capitalize()
        equipo = input("Tu Escudería / Club de Karting: ").strip().capitalize()
        db.guardar_perfil(nombre, apellido, equipo)
        print("\n¡Tu perfil local fue guardado con éxito!")
        
    elif opcion == "4":
        perfil = db.obtener_perfil()
        if not perfil:
            print("\n⚠️ Primero debés crear tu perfil en la opción 2.")
            continue
            
        print(f"\n--- REGISTRAR TELEMETRÍA PARA {perfil[0].upper()} ---")
        tipo = input("Tipo de evento (1: Simulador / 2: Karting): ").strip()
        tipo_evento = "Simulador" if tipo == "1" else "Karting"
        
        circuito = input("Nombre del Circuito: ").strip().capitalize()
        try:
            posicion = int(input("Posición de llegada (ej: 1, 3, 10): "))
            puntos = int(input("Puntos sumados en el campeonato: "))
            db.registrar_carrera_propia(tipo_evento, circuito, posicion, puntos)
            print("\n¡Datos guardados en tu base de datos!")
        except ValueError:
            print("\n Error: Posición y puntos deben ser números enteros.")
            
    elif opcion == "5":
        perfil = db.obtener_perfil()
        if not perfil:
            print("\n No hay perfiles creados en esta computadora todavía.")
            continue
            
        print(f"\n=====================================")
        print(f"  PILOTO: {perfil[0]} {perfil[1]}")
        print(f"  EQUIPO: {perfil[2]}")
        print(f"=====================================")
        
        carreras = db.obtener_mis_carreras()
        if not carreras:
            print("Aún no registraste carreras propias. ¡Salí a la pista!")
        else:
            total_puntos = sum(c[3] for c in carreras)
            print(f"Carreras: {len(carreras)} | Puntos Totales: {total_puntos} pts")
            print("-------------------------------------")
            for c in carreras:
              
    elif opcion == "6":
        print("\n¡Apagando motores y vaciando tanques! Hasta la próxima carrera.")
        break
    else:
        print("\nOpción inválida. Volvé a intentar.") 
"""     
        
        
        
        
    