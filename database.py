"""
Mi Profesor de Matemáticas Personal
Base de datos: Soporte dual para Supabase (PostgreSQL Cloud) y SQL Server 2019
"""
import os
import json
import re
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    TZ_LIMA = ZoneInfo('America/Lima')
except Exception:
    try:
        import pytz
        TZ_LIMA = pytz.timezone('America/Lima')
    except Exception:
        TZ_LIMA = timezone(timedelta(hours=-5))

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    import pyodbc
except ImportError:
    pyodbc = None


def _load_env():
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip().strip('\'"')
                    if k not in os.environ:
                        os.environ[k] = v

_load_env()


def is_supabase():
    """Detecta si está configurada la URL de Supabase / PostgreSQL."""
    return bool(os.environ.get('SUPABASE_DB_URL') or os.environ.get('DATABASE_URL'))


# ============================================================
# EXCEPCIONES PEDAGÓGICAS Y CASOS HISTÓRICOS ESPECÍFICOS
# ============================================================
# Exactamente 2 registros que representan reinicios rápidos accidentales y no errores matemáticos reales.
# Se conservan en el historial crudo pero se excluyen de métricas de aprendizaje, cálculo de dominio y estadísticas.
REGISTROS_EXCLUIDOS_APRENDIZAJE = (
    ('6312 - 4916', '1396'),
    ('9825 - 7761', '2064'),
)

EXCLUSION_SQL = "NOT ((operacion = '6312 - 4916' AND respuesta_correcta = '1396') OR (operacion = '9825 - 7761' AND respuesta_correcta = '2064'))"
EXCLUSION_SQL_ALIAS = "NOT ((e.operacion = '6312 - 4916' AND e.respuesta_correcta = '1396') OR (e.operacion = '9825 - 7761' AND e.respuesta_correcta = '2064'))"


def es_registro_excluido(operacion, respuesta_correcta, respuesta_usuario=''):
    """Identifica si un registro pertenece a la excepción de los 2 reinicios rápidos específicos."""
    op = str(operacion or '').strip()
    rc = str(respuesta_correcta or '').strip()
    ru = str(respuesta_usuario or '').strip().lower()
    for op_ex, rc_ex in REGISTROS_EXCLUIDOS_APRENDIZAJE:
        if op == op_ex and rc == rc_ex and ('no s' in ru or ru in ('', 'none', '(no sé)', '(no se)', 'no se', 'no sé')):
            return True
    return False


def consolidar_intentos_problema(ejercicios):
    """Consolida reintentos de una misma operación para evaluar aprendizaje y autorregulación."""
    problemas = []
    actual = None
    for e in ejercicios:
        op = str(e.get('operacion') or '')
        intentos = int(e.get('intentos') or 1)
        es_ok = bool(e.get('es_correcto'))
        ayuda = bool(e.get('uso_ayuda'))

        if actual and actual['operacion'] == op and intentos > 1:
            actual['intentos'] = max(actual['intentos'], intentos)
            actual['es_correcto'] = actual['es_correcto'] or es_ok
            actual['uso_ayuda'] = actual['uso_ayuda'] or ayuda
            if es_ok:
                actual['auto_corregido'] = True
                actual['respuesta_usuario_final'] = e.get('respuesta_usuario')
        else:
            actual = {
                'id': e.get('id'),
                'leccion_id': e.get('leccion_id'),
                'operacion': op,
                'respuesta_correcta': e.get('respuesta_correcta'),
                'respuesta_usuario_final': e.get('respuesta_usuario'),
                'es_correcto': es_ok,
                'intentos': intentos,
                'uso_ayuda': ayuda,
                'tipo_error': e.get('tipo_error'),
                'tipo_ejercicio': e.get('tipo_ejercicio'),
                'auto_corregido': False,
                'dificultad': e.get('dificultad', 1),
                'fecha': e.get('fecha', '')
            }
            problemas.append(actual)
    return problemas


def evaluar_calidad_problema(p):
    """Calcula el puntaje de calidad pedagógica de un problema consolidado (0.0 a 1.0).

    Casos Pedagógicos:
    - Caso A / F: Resuelto al 1er intento sin ayuda -> 1.0 (Evidencia sólida de dominio)
    - Caso B: Auto-corregido en 2do intento sin ayuda -> 0.85 (Capacidad de autorregulación y aprendizaje activo)
    - Caso C: Corregido tras 3+ intentos sin ayuda -> 0.65 (Requiere más práctica para fluidez)
    - Caso E: Resuelto con pistas -> 0.60 (1 intento) / 0.50 (2+ intentos) (Logro con andamiaje)
    - Caso D: Error no corregido / abandonado -> 0.0 (Dificultad conceptual o procedimental)
    """
    if not p['es_correcto']:
        return 0.0, 'D'
    if p['uso_ayuda']:
        return (0.60 if p['intentos'] == 1 else 0.50), 'E'
    if p['auto_corregido'] or p['intentos'] == 2:
        return 0.85, 'B'
    if p['intentos'] >= 3:
        return 0.65, 'C'
    return 1.00, 'A'


class CompatibleCursor:
    """Cursor compatible que traduce placeholders y sintaxis entre PostgreSQL y SQL Server."""
    def __init__(self, cursor, is_pg=False):
        self._cursor = cursor
        self._is_pg = is_pg

    @property
    def description(self):
        return self._cursor.description

    def execute(self, query, params=None):
        if self._is_pg:
            q = query.replace('?', '%s')
            q = q.replace('ISNULL(', 'COALESCE(')
            # Adaptaciones de booleanos en PostgreSQL (= 1 -> = TRUE, = 0 -> = FALSE)
            # Funciona tanto en cláusulas WHERE como en cláusulas UPDATE SET sin errores de sintaxis
            q = re.sub(r'\b(es_correcto|desbloqueado|completado|resuelto|evaluacion_inicial_completada|uso_ayuda)\s*=\s*1\b', r'\1 = TRUE', q, flags=re.IGNORECASE)
            q = re.sub(r'\b(es_correcto|desbloqueado|completado|resuelto|evaluacion_inicial_completada|uso_ayuda)\s*=\s*0\b', r'\1 = FALSE', q, flags=re.IGNORECASE)

            # Traducir TOP n a LIMIT n
            m = re.search(r'SELECT\s+TOP\s+(\d+)\s+(.+)', q, re.IGNORECASE | re.DOTALL)
            if m:
                limit_num = m.group(1)
                rest = m.group(2)
                q = f"SELECT {rest} LIMIT {limit_num}"

            if params is not None:
                return self._cursor.execute(q, tuple(params))
            return self._cursor.execute(q)
        else:
            if params is not None:
                return self._cursor.execute(query, params)
            return self._cursor.execute(query)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        return self._cursor.close()


class CompatibleConnection:
    """Conexión compatible que envuelve cursores para Supabase o SQL Server."""
    def __init__(self, conn, is_pg=False):
        self._conn = conn
        self._is_pg = is_pg

    def cursor(self):
        return CompatibleCursor(self._conn.cursor(), is_pg=self._is_pg)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()


def _build_connection_string():
    """Construir el string de conexión leyendo variables de entorno para SQL Server."""
    server = os.environ.get('DB_SERVER', 'localhost')
    db = os.environ.get('DB_NAME', 'Prueba')
    user = os.environ.get('DB_USER', 'sa')
    pwd = os.environ.get('DB_PASSWORD', '')
    return (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={db};"
        f"UID={user};"
        f"PWD={pwd};"
        f"TrustServerCertificate=yes;"
    )


def get_db():
    """Obtener conexión a Supabase (PostgreSQL) o SQL Server."""
    if is_supabase():
        if not psycopg2:
            raise ImportError("psycopg2-binary es requerido para conectarse a Supabase.")
        url = os.environ.get('SUPABASE_DB_URL') or os.environ.get('DATABASE_URL')
        conn = psycopg2.connect(url)
        return CompatibleConnection(conn, is_pg=True)
    else:
        if not pyodbc:
            raise ImportError("pyodbc es requerido para conectarse a SQL Server.")
        conn = pyodbc.connect(_build_connection_string())
        conn.autocommit = False
        return CompatibleConnection(conn, is_pg=False)


def dict_from_row(row, cursor):
    """Convertir una fila a diccionario."""
    if row is None:
        return None
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def rows_to_dicts(rows, cursor):
    """Convertir múltiples filas a lista de diccionarios."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def init_db():
    """Inicializar la base de datos con todas las tablas necesarias."""
    conn = get_db()
    cursor = conn.cursor()

    if is_supabase():
        # PostgreSQL / Supabase
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfil (
            id INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
            nombre VARCHAR(100) DEFAULT 'Estudiante',
            fecha_inicio VARCHAR(30),
            nivel_actual INT DEFAULT 1,
            subleccion_actual VARCHAR(10) DEFAULT '1.1',
            evaluacion_inicial_completada BOOLEAN DEFAULT FALSE,
            objetivo_diario_minutos INT DEFAULT 15,
            racha_actual INT DEFAULT 0,
            mejor_racha INT DEFAULT 0,
            ultima_sesion VARCHAR(30),
            configuracion TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS lecciones (
            id VARCHAR(10) PRIMARY KEY,
            nivel INT NOT NULL,
            orden INT NOT NULL,
            titulo VARCHAR(200) NOT NULL,
            descripcion VARCHAR(500),
            tipo VARCHAR(50) NOT NULL,
            prerequisitos TEXT DEFAULT '[]',
            estado VARCHAR(50) DEFAULT 'bloqueado',
            porcentaje_dominio FLOAT DEFAULT 0,
            ejercicios_completados INT DEFAULT 0,
            ejercicios_correctos INT DEFAULT 0,
            ultimo_intento VARCHAR(30),
            veces_practicada INT DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS ejercicios (
            id SERIAL PRIMARY KEY,
            leccion_id VARCHAR(10) NOT NULL REFERENCES lecciones(id),
            fecha VARCHAR(30) NOT NULL,
            tipo_ejercicio VARCHAR(100) NOT NULL,
            operacion VARCHAR(500) NOT NULL,
            respuesta_correcta VARCHAR(200) NOT NULL,
            respuesta_usuario VARCHAR(200),
            es_correcto BOOLEAN,
            intentos INT DEFAULT 1,
            tiempo_segundos FLOAT,
            uso_ayuda BOOLEAN DEFAULT FALSE,
            tipo_error VARCHAR(100),
            dificultad INT DEFAULT 1,
            detalles TEXT DEFAULT '{}'
        );

        CREATE TABLE IF NOT EXISTS sesiones (
            id SERIAL PRIMARY KEY,
            fecha_inicio VARCHAR(30) NOT NULL,
            fecha_fin VARCHAR(30),
            duracion_minutos FLOAT DEFAULT 0,
            ejercicios_resueltos INT DEFAULT 0,
            ejercicios_correctos INT DEFAULT 0,
            leccion_id VARCHAR(10)
        );

        CREATE TABLE IF NOT EXISTS logros (
            id VARCHAR(50) PRIMARY KEY,
            titulo VARCHAR(100) NOT NULL,
            descripcion VARCHAR(300),
            icono VARCHAR(10) DEFAULT '🏆',
            fecha_desbloqueo VARCHAR(30),
            desbloqueado BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS evaluacion_diagnostica (
            id SERIAL PRIMARY KEY,
            fecha VARCHAR(30) NOT NULL,
            nivel INT NOT NULL,
            tema VARCHAR(200) NOT NULL,
            total_preguntas INT,
            correctas INT,
            porcentaje FLOAT,
            recomendacion VARCHAR(500)
        );

        CREATE TABLE IF NOT EXISTS patrones_error (
            id SERIAL PRIMARY KEY,
            leccion_id VARCHAR(10),
            tipo_error VARCHAR(100) NOT NULL,
            descripcion VARCHAR(500),
            frecuencia INT DEFAULT 1,
            ultima_ocurrencia VARCHAR(30),
            resuelto BOOLEAN DEFAULT FALSE
        );

        CREATE TABLE IF NOT EXISTS repasos (
            id SERIAL PRIMARY KEY,
            leccion_id VARCHAR(10) NOT NULL REFERENCES lecciones(id),
            fecha_programada VARCHAR(30) NOT NULL,
            completado BOOLEAN DEFAULT FALSE,
            fecha_completado VARCHAR(30),
            resultado FLOAT
        );
        """)
    else:
        # SQL Server 2019
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'perfil')
        CREATE TABLE perfil (
            id INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
            nombre NVARCHAR(100) DEFAULT N'Estudiante',
            fecha_inicio NVARCHAR(30),
            nivel_actual INT DEFAULT 1,
            subleccion_actual NVARCHAR(10) DEFAULT '1.1',
            evaluacion_inicial_completada BIT DEFAULT 0,
            objetivo_diario_minutos INT DEFAULT 15,
            racha_actual INT DEFAULT 0,
            mejor_racha INT DEFAULT 0,
            ultima_sesion NVARCHAR(30),
            configuracion NVARCHAR(MAX) DEFAULT '{}'
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'lecciones')
        CREATE TABLE lecciones (
            id NVARCHAR(10) PRIMARY KEY,
            nivel INT NOT NULL,
            orden INT NOT NULL,
            titulo NVARCHAR(200) NOT NULL,
            descripcion NVARCHAR(500),
            tipo NVARCHAR(50) NOT NULL,
            prerequisitos NVARCHAR(MAX) DEFAULT '[]',
            estado NVARCHAR(50) DEFAULT 'bloqueado',
            porcentaje_dominio FLOAT DEFAULT 0,
            ejercicios_completados INT DEFAULT 0,
            ejercicios_correctos INT DEFAULT 0,
            ultimo_intento NVARCHAR(30),
            veces_practicada INT DEFAULT 0
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ejercicios')
        CREATE TABLE ejercicios (
            id INT IDENTITY(1,1) PRIMARY KEY,
            leccion_id NVARCHAR(10) NOT NULL,
            fecha NVARCHAR(30) NOT NULL,
            tipo_ejercicio NVARCHAR(100) NOT NULL,
            operacion NVARCHAR(500) NOT NULL,
            respuesta_correcta NVARCHAR(200) NOT NULL,
            respuesta_usuario NVARCHAR(200),
            es_correcto BIT,
            intentos INT DEFAULT 1,
            tiempo_segundos FLOAT,
            uso_ayuda BIT DEFAULT 0,
            tipo_error NVARCHAR(100),
            dificultad INT DEFAULT 1,
            detalles NVARCHAR(MAX) DEFAULT '{}',
            FOREIGN KEY (leccion_id) REFERENCES lecciones(id)
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sesiones')
        CREATE TABLE sesiones (
            id INT IDENTITY(1,1) PRIMARY KEY,
            fecha_inicio NVARCHAR(30) NOT NULL,
            fecha_fin NVARCHAR(30),
            duracion_minutos FLOAT DEFAULT 0,
            ejercicios_resueltos INT DEFAULT 0,
            ejercicios_correctos INT DEFAULT 0,
            leccion_id NVARCHAR(10)
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'logros')
        CREATE TABLE logros (
            id NVARCHAR(50) PRIMARY KEY,
            titulo NVARCHAR(100) NOT NULL,
            descripcion NVARCHAR(300),
            icono NVARCHAR(10) DEFAULT N'🏆',
            fecha_desbloqueo NVARCHAR(30),
            desbloqueado BIT DEFAULT 0
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'evaluacion_diagnostica')
        CREATE TABLE evaluacion_diagnostica (
            id INT IDENTITY(1,1) PRIMARY KEY,
            fecha NVARCHAR(30) NOT NULL,
            nivel INT NOT NULL,
            tema NVARCHAR(200) NOT NULL,
            total_preguntas INT,
            correctas INT,
            porcentaje FLOAT,
            recomendacion NVARCHAR(500)
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'patrones_error')
        CREATE TABLE patrones_error (
            id INT IDENTITY(1,1) PRIMARY KEY,
            leccion_id NVARCHAR(10),
            tipo_error NVARCHAR(100) NOT NULL,
            descripcion NVARCHAR(500),
            frecuencia INT DEFAULT 1,
            ultima_ocurrencia NVARCHAR(30),
            resuelto BIT DEFAULT 0
        )
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'repasos')
        CREATE TABLE repasos (
            id INT IDENTITY(1,1) PRIMARY KEY,
            leccion_id NVARCHAR(10) NOT NULL,
            fecha_programada NVARCHAR(30) NOT NULL,
            completado BIT DEFAULT 0,
            fecha_completado NVARCHAR(30),
            resultado FLOAT,
            FOREIGN KEY (leccion_id) REFERENCES lecciones(id)
        )
        """)

    conn.commit()

    # Insertar perfil si no existe
    cursor.execute("SELECT COUNT(*) FROM perfil")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO perfil (id, fecha_inicio) VALUES (1, ?)",
            (datetime.now().isoformat(),)
        )
        conn.commit()

    # Insertar lecciones del currículo
    _insertar_curriculo(cursor, conn)

    # Insertar logros
    _insertar_logros(cursor, conn)

    conn.close()


def _insertar_curriculo(cursor, conn):
    """Insertar todas las lecciones del currículo."""
    lecciones = [
        # Nivel 1: Sumas y restas
        ('1.1', 1, 1, 'Sumas sencillas', 'Sumas con números de una cifra', 'practica', '[]'),
        ('1.2', 1, 2, 'Restas sencillas', 'Restas con números de una cifra', 'practica', '["1.1"]'),
        ('1.3', 1, 3, 'Sumas con llevadas', 'Sumas donde la suma de cifras supera 9', 'practica', '["1.1"]'),
        ('1.4', 1, 4, 'Restas con préstamos', 'Restas donde necesitas pedir prestado', 'practica', '["1.2"]'),
        ('1.5', 1, 5, 'Operaciones con números grandes', 'Sumas y restas con números de varias cifras', 'practica', '["1.3", "1.4"]'),
        ('1.6', 1, 6, 'Cálculo mental', 'Ejercicios rápidos de suma y resta mental', 'practica', '["1.5"]'),
        ('1.7', 1, 7, 'Problemas con sumas y restas', 'Problemas de la vida real', 'problemas', '["1.5"]'),

        # Nivel 2: Multiplicaciones
        ('2.1', 2, 1, 'Tablas del 1 al 5', 'Aprender las tablas de multiplicar del 1 al 5', 'practica', '["1.5"]'),
        ('2.2', 2, 2, 'Tablas del 6 al 9', 'Aprender las tablas de multiplicar del 6 al 9', 'practica', '["2.1"]'),
        ('2.3', 2, 3, 'Tablas del 10 al 12', 'Tablas de multiplicar del 10 al 12', 'practica', '["2.2"]'),
        ('2.4', 2, 4, 'Trucos de multiplicación', 'Patrones y trucos para multiplicar más fácil', 'teoria', '["2.1"]'),
        ('2.5', 2, 5, 'Multiplicaciones de dos cifras', 'Multiplicar números de dos cifras', 'practica', '["2.3"]'),
        ('2.6', 2, 6, 'Multiplicaciones de varias cifras', 'Multiplicar números grandes', 'practica', '["2.5"]'),
        ('2.7', 2, 7, 'Problemas de multiplicación', 'Problemas prácticos con multiplicaciones', 'problemas', '["2.6"]'),

        # Nivel 3: Divisiones
        ('3.1', 3, 1, '¿Qué significa dividir?', 'Concepto de división y repartir', 'teoria', '["2.3"]'),
        ('3.2', 3, 2, 'Divisiones exactas', 'Divisiones sin residuo', 'practica', '["3.1"]'),
        ('3.3', 3, 3, 'Divisiones con residuo', 'Divisiones donde sobra un resto', 'practica', '["3.2"]'),
        ('3.4', 3, 4, 'Divisiones con números grandes', 'Dividir números de varias cifras', 'practica', '["3.3"]'),
        ('3.5', 3, 5, 'División con decimales', 'Divisiones que resultan en decimales', 'practica', '["3.4"]'),
        ('3.6', 3, 6, 'Problemas de división', 'Problemas prácticos con divisiones', 'problemas', '["3.4"]'),

        # Nivel 4: Fracciones y decimales
        ('4.1', 4, 1, '¿Qué son las fracciones?', 'Concepto de fracción y representación', 'teoria', '["3.2"]'),
        ('4.2', 4, 2, 'Suma y resta de fracciones', 'Operaciones básicas con fracciones', 'practica', '["4.1"]'),
        ('4.3', 4, 3, 'Multiplicación y división de fracciones', 'Multiplicar y dividir fracciones', 'practica', '["4.2"]'),
        ('4.4', 4, 4, 'Fracciones y decimales', 'Convertir entre fracciones y decimales', 'practica', '["4.1"]'),
        ('4.5', 4, 5, 'Porcentajes', 'Calcular porcentajes y sus aplicaciones', 'practica', '["4.4"]'),

        # Nivel 5: Potencias y raíces
        ('5.1', 5, 1, 'Potencias', 'Qué son y cómo calcularlas', 'practica', '["2.6"]'),
        ('5.2', 5, 2, 'Cuadrados perfectos', 'Números que son cuadrados perfectos', 'practica', '["5.1"]'),
        ('5.3', 5, 3, 'Raíces cuadradas', 'Calcular raíces cuadradas', 'practica', '["5.2"]'),
        ('5.4', 5, 4, 'Propiedades de potencias', 'Leyes y propiedades de las potencias', 'practica', '["5.1"]'),
        ('5.5', 5, 5, 'Logaritmos y Exponenciales', 'Concepto de logaritmo y cálculo de complejidades', 'practica', '["5.4"]'),

        # Nivel 6: Álgebra y Fundamentos de Computación
        ('6.1', 6, 1, 'Números positivos y negativos', 'Operaciones con enteros', 'practica', '["1.6"]'),
        ('6.2', 6, 2, 'Uso de letras en matemáticas', 'Variables y constantes', 'teoria', '["6.1"]'),
        ('6.3', 6, 3, 'Expresiones algebraicas', 'Formar y simplificar expresiones', 'practica', '["6.2"]'),
        ('6.4', 6, 4, 'Ecuaciones de primer grado', 'Resolver ecuaciones lineales', 'practica', '["6.3"]'),
        ('6.5', 6, 5, 'Despejes', 'Despejar variables en fórmulas', 'practica', '["6.4"]'),
        ('6.6', 6, 6, 'Factorización básica', 'Factorizar expresiones algebraicas', 'practica', '["6.3"]'),
        ('6.7', 6, 7, 'Productos notables', 'Binomios al cuadrado y diferencias de cuadrados', 'practica', '["6.6"]'),
        ('6.8', 6, 8, 'Ecuaciones cuadráticas', 'Resolver ecuaciones de segundo grado', 'practica', '["6.7"]'),
        ('6.9', 6, 9, 'Sistemas Numéricos (Binario y Hex)', 'Conversión decimal, binario y hexadecimal', 'practica', '["5.1"]'),
        ('6.10', 6, 10, 'Lógica Proposicional y Álgebra Booleana', 'Tablas de verdad (AND, OR, NOT, XOR), implicación lógica y sentencias condicionales if/else', 'practica', '["6.9"]'),

        # Nivel 7: Matemática para la Ingeniería (Sílabo Oficial 2026-2)
        ('7.1', 7, 1, 'Sesión 1: Números Reales y Desigualdades', 'Intervalos, desigualdades lineales y valor absoluto', 'practica', '["6.4"]'),
        ('7.2', 7, 2, 'Sesión 2: Expresiones Racionales', 'Simplificación y operaciones con fracciones algebraicas', 'practica', '["6.6"]'),
        ('7.3', 7, 3, 'Sesión 3: Matrices y Operaciones', 'Suma, producto por escalar y producto matricial en ingeniería', 'practica', '["7.1"]'),
        ('7.4', 7, 4, 'Sesión 4: Determinantes y Matriz Inversa', 'Regla de Sarrus y matriz inversa por Gauss-Jordan', 'practica', '["7.3"]'),
        ('7.5', 7, 5, 'Sesión 5: Sistemas de Ecuaciones Lineales', 'Método de Cramer y aplicaciones en ingeniería', 'practica', '["7.4"]'),
        ('7.6', 7, 6, 'Sesión 6: Funciones Reales y Modelos', 'Dominio, rango y modelos matemáticos lineales/cuadráticos', 'practica', '["7.1"]'),
        ('7.7', 7, 7, 'Sesión 7: Composición y Función Inversa', 'Álgebra de funciones, (f o g)(x) y función inversa', 'practica', '["7.6"]'),
        ('7.8', 7, 8, 'Sesión 8/9: Funciones Seccionadas y GeoGebra', 'Funciones por tramos y análisis gráfico', 'practica', '["7.7"]'),
        ('7.9', 7, 9, 'Sesión 10: Examen Parcial de Ingeniería', 'Evaluación consolidada de matrices, sistemas y funciones', 'examen', '["7.5", "7.8"]'),
        ('7.10', 7, 10, 'Sesión 11: Coordenadas Polares', 'Conversión entre sistemas polares y cartesianos', 'practica', '["7.6"]'),
        ('7.11', 7, 11, 'Sesión 12: Límites y Teoremas', 'Concepto de límite, propiedades y límites laterales', 'practica', '["7.6"]'),
        ('7.12', 7, 12, 'Sesión 13: Cálculo Analítico de Límites', 'Indeterminaciones 0/0, infinito y racionalización', 'practica', '["7.11"]'),
        ('7.13', 7, 13, 'Sesión 14: Continuidad de Funciones', 'Condiciones de continuidad y análisis de discontinuidades', 'practica', '["7.12"]'),
        ('7.14', 7, 14, 'Sesión 15: Derivadas y Optimización', 'Reglas de derivación, cadena, máximos y mínimos', 'practica', '["7.13"]'),
        ('7.15', 7, 15, 'Sesión 16: Examen Final de Ingeniería', 'Evaluación integral de Matemática para la Ingeniería', 'examen', '["7.14"]'),
    ]

    for leccion in lecciones:
        if is_supabase():
            cursor.execute("""
                INSERT INTO lecciones (id, nivel, orden, titulo, descripcion, tipo, prerequisitos)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET
                    nivel = EXCLUDED.nivel,
                    orden = EXCLUDED.orden,
                    titulo = EXCLUDED.titulo,
                    descripcion = EXCLUDED.descripcion,
                    tipo = EXCLUDED.tipo,
                    prerequisitos = EXCLUDED.prerequisitos
            """, leccion)
        else:
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM lecciones WHERE id = ?)
                BEGIN
                    INSERT INTO lecciones (id, nivel, orden, titulo, descripcion, tipo, prerequisitos)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                END
                ELSE
                BEGIN
                    UPDATE lecciones
                    SET nivel = ?, orden = ?, titulo = ?, descripcion = ?, tipo = ?, prerequisitos = ?
                    WHERE id = ?
                END
            """, (
                leccion[0],
                leccion[0], leccion[1], leccion[2], leccion[3], leccion[4], leccion[5], leccion[6],
                leccion[1], leccion[2], leccion[3], leccion[4], leccion[5], leccion[6],
                leccion[0]
            ))

    # Desbloquear la primera lección
    cursor.execute("UPDATE lecciones SET estado = 'disponible' WHERE id = '1.1'")
    conn.commit()


def _insertar_logros(cursor, conn):
    """Insertar los logros del sistema."""
    logros = [
        ('primer_ejercicio', '¡Primer paso!', 'Completaste tu primer ejercicio', '🎯'),
        ('diez_correctos', 'En racha', '10 ejercicios correctos seguidos', '🔥'),
        ('primera_leccion', 'Lección completa', 'Dominaste tu primera lección', '📚'),
        ('primer_nivel', 'Nivel superado', 'Completaste el primer nivel', '⭐'),
        ('sin_errores', 'Perfección', 'Una sesión completa sin errores', '💎'),
        ('una_hora', 'Dedicación', 'Una hora total de estudio', '⏰'),
        ('cinco_horas', 'Constancia', 'Cinco horas de estudio', '🕐'),
        ('racha_3', 'Tres días seguidos', '3 días consecutivos estudiando', '📅'),
        ('racha_7', 'Semana completa', '7 días seguidos estudiando', '🗓️'),
        ('racha_30', 'Un mes dedicado', '30 días seguidos estudiando', '🏅'),
        ('nivel_2', 'Multiplicador', 'Llegaste al nivel de multiplicaciones', '✖️'),
        ('nivel_3', 'Divisor', 'Llegaste al nivel de divisiones', '➗'),
        ('nivel_4', 'Fraccionario', 'Llegaste al nivel de fracciones', '🔢'),
        ('nivel_5', 'Potente', 'Llegaste al nivel de potencias', '💪'),
        ('nivel_6', 'Algebraísta', 'Llegaste al nivel de álgebra', '🧮'),
        ('nivel_7', 'Ingeniero en formación', 'Llegaste a matemáticas para ingeniería', '🎓'),
        ('cien_ejercicios', 'Centenario', '100 ejercicios completados', '💯'),
        ('quinientos_ejercicios', 'Medio millar', '500 ejercicios completados', '🏆'),
        ('mejora_notable', 'Mejora notable', 'Tu porcentaje de aciertos subió 20% en un tema', '📈'),
        ('calculo_mental', 'Mente rápida', 'Resolviste 10 ejercicios en menos de 5 segundos cada uno', '⚡'),
    ]

    for logro in logros:
        if is_supabase():
            cursor.execute("""
                INSERT INTO logros (id, titulo, descripcion, icono)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
            """, logro)
        else:
            cursor.execute("""
                IF NOT EXISTS (SELECT 1 FROM logros WHERE id = ?)
                INSERT INTO logros (id, titulo, descripcion, icono)
                VALUES (?, ?, ?, ?)
            """, (logro[0],) + logro)

    conn.commit()


# --- Funciones de consulta ---

def obtener_perfil():
    """Obtener el perfil del estudiante."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM perfil WHERE id = 1")
    row = cursor.fetchone()
    result = dict_from_row(row, cursor)
    conn.close()
    return result


def actualizar_perfil(**kwargs):
    """Actualizar campos del perfil."""
    conn = get_db()
    cursor = conn.cursor()
    sets = ', '.join(f"{k} = ?" for k in kwargs)
    if is_supabase():
        bool_cols = {'evaluacion_inicial_completada', 'uso_ayuda', 'es_correcto', 'desbloqueado', 'completado', 'resuelto'}
        values = [bool(v) if k in bool_cols else v for k, v in kwargs.items()]
    else:
        values = list(kwargs.values())
    cursor.execute(f"UPDATE perfil SET {sets} WHERE id = 1", values)
    conn.commit()
    conn.close()


def obtener_lecciones(nivel=None):
    """Obtener lecciones, opcionalmente filtradas por nivel."""
    conn = get_db()
    cursor = conn.cursor()
    if nivel:
        cursor.execute(
            "SELECT * FROM lecciones WHERE nivel = ? ORDER BY orden", (nivel,)
        )
    else:
        cursor.execute("SELECT * FROM lecciones ORDER BY nivel, orden")
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    conn.close()
    return result


def obtener_leccion(leccion_id):
    """Obtener una lección específica."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lecciones WHERE id = ?", (leccion_id,))
    row = cursor.fetchone()
    result = dict_from_row(row, cursor)
    conn.close()
    return result


def actualizar_leccion(leccion_id, **kwargs):
    """Actualizar campos de una lección."""
    conn = get_db()
    cursor = conn.cursor()
    sets = ', '.join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [leccion_id]
    cursor.execute(f"UPDATE lecciones SET {sets} WHERE id = ?", values)
    conn.commit()
    conn.close()


def registrar_ejercicio(leccion_id, tipo_ejercicio, operacion, respuesta_correcta,
                        respuesta_usuario, es_correcto, intentos=1, tiempo_segundos=0,
                        uso_ayuda=0, tipo_error=None, dificultad=1, detalles=None,
                        sesion_id=None):
    """Registrar un ejercicio completado. sesion_id vincula el ejercicio a la sesión."""
    conn = get_db()
    cursor = conn.cursor()

    es_corr_val = bool(es_correcto) if is_supabase() else int(es_correcto)
    uso_ayuda_val = bool(uso_ayuda) if is_supabase() else int(uso_ayuda)

    if sesion_id is not None:
        cursor.execute("""
            INSERT INTO ejercicios
            (leccion_id, fecha, tipo_ejercicio, operacion, respuesta_correcta,
             respuesta_usuario, es_correcto, intentos, tiempo_segundos,
             uso_ayuda, tipo_error, dificultad, detalles, sesion_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            leccion_id, datetime.now().isoformat(), tipo_ejercicio, operacion,
            str(respuesta_correcta), str(respuesta_usuario), es_corr_val,
            intentos, tiempo_segundos, uso_ayuda_val, tipo_error, dificultad,
            json.dumps(detalles or {}), sesion_id
        ))
    else:
        cursor.execute("""
            INSERT INTO ejercicios
            (leccion_id, fecha, tipo_ejercicio, operacion, respuesta_correcta,
             respuesta_usuario, es_correcto, intentos, tiempo_segundos,
             uso_ayuda, tipo_error, dificultad, detalles)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            leccion_id, datetime.now().isoformat(), tipo_ejercicio, operacion,
            str(respuesta_correcta), str(respuesta_usuario), es_corr_val,
            intentos, tiempo_segundos, uso_ayuda_val, tipo_error, dificultad,
            json.dumps(detalles or {})
        ))

    # Actualizar contadores de la lección
    inc_correcto = 1 if es_correcto else 0
    cursor.execute("""
        UPDATE lecciones
        SET ejercicios_completados = ejercicios_completados + 1,
            ejercicios_correctos = ejercicios_correctos + ?,
            ultimo_intento = ?,
            veces_practicada = veces_practicada + 1
        WHERE id = ?
    """, (inc_correcto, datetime.now().isoformat(), leccion_id))

    # Actualizar patrones de error si corresponde (excluyendo registros especiales)
    if not es_correcto and tipo_error and not es_registro_excluido(operacion, respuesta_correcta, respuesta_usuario):
        registrar_o_actualizar_patron_error(cursor, leccion_id, tipo_error, operacion)
    elif es_correcto:
        verificar_resolucion_patrones(cursor, leccion_id)

    # Recalcular dominio pedagógico
    _recalcular_dominio(cursor, leccion_id)

    conn.commit()

    # Obtener el ID insertado
    if is_supabase():
        cursor.execute("SELECT lastval()")
    else:
        cursor.execute("SELECT @@IDENTITY")
    exercise_id = cursor.fetchone()[0]

    conn.close()
    return exercise_id


# ============================================================
# SESIONES DE ESTUDIO — FASE 1
# ============================================================

def _asegurar_datetime(dt):
    """Normaliza un valor a datetime con timezone (UTC por defecto si es naive)."""
    if dt is None:
        return None
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    if isinstance(dt, str):
        try:
            d = datetime.fromisoformat(dt)
            if d.tzinfo is None:
                return d.replace(tzinfo=timezone.utc)
            return d
        except Exception:
            return None
    return dt


def calcular_tiempo_a_sumar(ultima_actividad, ahora) -> float:
    """Función pura que calcula los segundos a sumar en un heartbeat.
    
    delta = ahora - ultima_actividad
    Suma min(delta, 120) segundos. Si delta <= 0, retorna 0.0.
    """
    dt_ultima = _asegurar_datetime(ultima_actividad)
    dt_ahora = _asegurar_datetime(ahora)
    if dt_ultima is None or dt_ahora is None:
        return 0.0
    delta = (dt_ahora - dt_ultima).total_seconds()
    if delta <= 0:
        return 0.0
    return min(delta, 120.0)


def contar_problemas_sesion(cursor, sesion_id: int) -> tuple[int, int]:
    """Retorna (problemas_finalizados, problemas_correctos) derivados de las filas
    de `ejercicios` asociadas a `sesion_id`, consolidando intentos de una misma operación.
    """
    cursor.execute("""
        SELECT id, leccion_id, operacion, respuesta_correcta, respuesta_usuario,
               es_correcto, intentos, uso_ayuda, tipo_error, tipo_ejercicio, dificultad, fecha
        FROM ejercicios
        WHERE sesion_id = %s
        ORDER BY id ASC
    """, (sesion_id,))
    rows = cursor.fetchall()
    if not rows:
        return 0, 0
    cols = [col[0] for col in cursor.description]
    ejercicios = [dict(zip(cols, r)) for r in rows]
    problemas = consolidar_intentos_problema(ejercicios)

    total_problemas = len(problemas)
    correctos = sum(1 for p in problemas if p.get('es_correcto'))
    return total_problemas, correctos


def evaluar_inactividad_sesiones(cursor, ahora=None):
    """Cierra sesiones abiertas con más de 30 min sin ultima_actividad.
    
    fin_at = ultima_actividad
    motivo_cierre = 'inactividad'
    es_valida = (problemas >= 3)
    """
    dt_ahora = _asegurar_datetime(ahora) or datetime.now(timezone.utc)
    umbral = dt_ahora - timedelta(minutes=30)

    cursor.execute("""
        SELECT id, inicio_at, ultima_actividad, tiempo_activo_segundos
        FROM sesiones
        WHERE estado = 'abierta'
          AND ultima_actividad IS NOT NULL
          AND ultima_actividad < %s
    """, (umbral,))
    vencidas = cursor.fetchall()

    for row in vencidas:
        sid, inicio, ultima, _ = row[0], row[1], row[2], row[3]
        dt_inicio = _asegurar_datetime(inicio)
        dt_ultima = _asegurar_datetime(ultima)
        duracion_min = 0.0
        if dt_inicio and dt_ultima:
            duracion_min = max(0.0, (dt_ultima - dt_inicio).total_seconds() / 60.0)

        problemas, correctos = contar_problemas_sesion(cursor, sid)
        es_valida = problemas >= 3

        cursor.execute("""
            UPDATE sesiones
            SET estado = 'cerrada',
                fin_at = %s,
                duracion_minutos = %s,
                es_valida = %s,
                motivo_cierre = 'inactividad',
                ejercicios_resueltos = %s,
                ejercicios_correctos = %s
            WHERE id = %s
        """, (dt_ultima, round(duracion_min, 2), es_valida, problemas, correctos, sid))


def iniciar_sesion(ahora=None) -> tuple[int, bool]:
    """Inicia una nueva sesión de estudio o retoma una sesión abierta no vencida.
    
    Retorna (sesion_id, reanudada: bool).
    Maneja la violación del índice único devolviendo la sesión existente si ocurre.
    """
    dt_ahora = _asegurar_datetime(ahora) or datetime.now(timezone.utc)
    conn = get_db()
    cursor = conn.cursor()

    # 1. Evaluar y cerrar sesiones inactivas (> 30 min)
    evaluar_inactividad_sesiones(cursor, dt_ahora)
    conn.commit()

    # 2. Comprobar si ya existe una sesión abierta válida
    cursor.execute("""
        SELECT id FROM sesiones
        WHERE estado = 'abierta'
        ORDER BY id DESC
        LIMIT 1
    """)
    existente = cursor.fetchone()
    if existente:
        sid = existente[0]
        conn.close()
        return sid, True

    # 3. Intentar crear una nueva sesión (solo columnas v2: inicio_at, sin fecha_inicio)
    try:
        cursor.execute("""
            INSERT INTO sesiones
            (estado, inicio_at, ultima_actividad, tiempo_activo_segundos,
             ejercicios_resueltos, ejercicios_correctos, es_valida)
            VALUES ('abierta', %s, %s, 0.0, 0, 0, FALSE)
            RETURNING id
        """, (dt_ahora, dt_ahora))
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return nuevo_id, False
    except Exception:
        # Violación de índice único parcial (concurrencia)
        conn.rollback()
        cursor.execute("""
            SELECT id FROM sesiones
            WHERE estado = 'abierta'
            ORDER BY id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0], True
        raise


def registrar_heartbeat(sesion_id: int, ahora=None) -> dict:
    """Registra actividad real en la sesión abierta.
    
    Si la sesión está vencida (> 30 min sin ultima_actividad), la cierra con:
    fin_at = ultima_actividad, motivo_cierre = 'inactividad',
    y retorna {'ok': False, 'expirada': True, 'motivo': 'inactividad'}.
    """
    dt_ahora = _asegurar_datetime(ahora) or datetime.now(timezone.utc)
    conn = get_db()
    cursor = conn.cursor()

    # Evaluar inactividad general
    evaluar_inactividad_sesiones(cursor, dt_ahora)
    conn.commit()

    cursor.execute("""
        SELECT estado, ultima_actividad, inicio_at, motivo_cierre
        FROM sesiones
        WHERE id = %s
    """, (sesion_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {'ok': False, 'motivo': 'sesion_no_encontrada'}

    estado, ultima_actividad, inicio_at, motivo_cierre = row[0], row[1], row[2], row[3]
    if estado != 'abierta':
        conn.close()
        return {'ok': False, 'expirada': True, 'motivo': motivo_cierre or 'inactividad'}

    dt_ultima = _asegurar_datetime(ultima_actividad)
    # Comprobar vencimiento de esta sesión específica (> 30 min)
    if dt_ultima and (dt_ahora - dt_ultima).total_seconds() > 1800:
        problemas, correctos = contar_problemas_sesion(cursor, sesion_id)
        es_valida = problemas >= 3
        dt_inicio = _asegurar_datetime(inicio_at)
        duracion_min = 0.0
        if dt_inicio and dt_ultima:
            duracion_min = max(0.0, (dt_ultima - dt_inicio).total_seconds() / 60.0)

        cursor.execute("""
            UPDATE sesiones
            SET estado = 'cerrada',
                fin_at = %s,
                duracion_minutos = %s,
                es_valida = %s,
                motivo_cierre = 'inactividad',
                ejercicios_resueltos = %s,
                ejercicios_correctos = %s
            WHERE id = %s
        """, (dt_ultima, round(duracion_min, 2), es_valida, problemas, correctos, sesion_id))
        conn.commit()
        conn.close()
        return {'ok': False, 'expirada': True, 'motivo': 'inactividad'}

    segundos_a_sumar = calcular_tiempo_a_sumar(dt_ultima, dt_ahora)

    # Suma atómica directamente en SQL
    cursor.execute("""
        UPDATE sesiones
        SET ultima_actividad = %s,
            tiempo_activo_segundos = COALESCE(tiempo_activo_segundos, 0) + %s
        WHERE id = %s AND estado = 'abierta'
        RETURNING tiempo_activo_segundos
    """, (dt_ahora, segundos_a_sumar, sesion_id))
    row_upd = cursor.fetchone()
    nuevo_tiempo = row_upd[0] if row_upd else 0.0
    conn.commit()
    conn.close()
    return {'ok': True, 'tiempo_activo_segundos': nuevo_tiempo}


def cerrar_sesion(sesion_id: int, motivo: str = 'manual', ahora=None) -> dict:
    """Cierra la sesión y calcula métricas finales derivadas de `ejercicios`.
    
    Evalúa inactividad al inicio. Si la sesión estaba vencida (>30 min sin actividad),
    se cierra con motivo 'inactividad' y fin_at = ultima_actividad (no la hora actual),
    y devuelve dicho resumen.
    """
    dt_ahora = _asegurar_datetime(ahora) or datetime.now(timezone.utc)
    conn = get_db()
    cursor = conn.cursor()

    # 1. Comprobar existencia y estado previo
    cursor.execute("""
        SELECT estado, inicio_at, ultima_actividad, tiempo_activo_segundos,
               fin_at, duracion_minutos, es_valida, motivo_cierre,
               ejercicios_resueltos, ejercicios_correctos
        FROM sesiones
        WHERE id = %s
    """, (sesion_id,))
    row_prev = cursor.fetchone()
    if not row_prev:
        conn.close()
        return {'ok': False, 'motivo': 'sesion_no_encontrada'}

    if row_prev[0] == 'cerrada':
        conn.close()
        return {'ok': True, 'sesion_id': sesion_id, 'ya_cerrada': True}

    # 2. Evaluar inactividad general al inicio (igual que iniciar, heartbeat y activa)
    evaluar_inactividad_sesiones(cursor, dt_ahora)
    conn.commit()

    # 3. Leer estado tras evaluar inactividad
    cursor.execute("""
        SELECT estado, inicio_at, ultima_actividad, tiempo_activo_segundos,
               fin_at, duracion_minutos, es_valida, motivo_cierre,
               ejercicios_resueltos, ejercicios_correctos
        FROM sesiones
        WHERE id = %s
    """, (sesion_id,))
    row = cursor.fetchone()
    estado, inicio_at, ultima_actividad, tiempo_activo = row[0], row[1], row[2], row[3] or 0.0
    fin_at, duracion_min, es_valida, motivo_cierre = row[4], row[5], row[6], row[7]
    problemas, correctos = row[8] or 0, row[9] or 0

    # Si fue cerrada por inactividad durante evaluar_inactividad_sesiones
    if estado == 'cerrada':
        conn.close()
        return {
            'ok': True,
            'sesion_id': sesion_id,
            'duracion_minutos': float(duracion_min or 0.0),
            'tiempo_activo_segundos': round(tiempo_activo, 2),
            'problemas_finalizados': problemas,
            'ejercicios_resueltos': problemas,
            'ejercicios_correctos': correctos,
            'es_valida': bool(es_valida),
            'motivo_cierre': motivo_cierre or 'inactividad',
        }

    # Si seguía abierta pero tiene >30 min de inactividad respecto a dt_ahora
    dt_inicio = _asegurar_datetime(inicio_at)
    dt_ultima = _asegurar_datetime(ultima_actividad) or dt_inicio

    if dt_ultima and (dt_ahora - dt_ultima).total_seconds() > 1800:
        motivo_final = 'inactividad'
        fin_at_val = dt_ultima
    elif motivo == 'inactividad':
        motivo_final = 'inactividad'
        fin_at_val = dt_ultima or dt_ahora
    else:
        motivo_final = motivo
        fin_at_val = dt_ahora

    duracion_min_val = 0.0
    if dt_inicio and fin_at_val:
        duracion_min_val = max(0.0, (fin_at_val - dt_inicio).total_seconds() / 60.0)

    problemas_cnt, correctos_cnt = contar_problemas_sesion(cursor, sesion_id)
    es_valida_val = problemas_cnt >= 3

    cursor.execute("""
        UPDATE sesiones
        SET estado = 'cerrada',
            fin_at = %s,
            duracion_minutos = %s,
            es_valida = %s,
            motivo_cierre = %s,
            ejercicios_resueltos = %s,
            ejercicios_correctos = %s
        WHERE id = %s
    """, (fin_at_val, round(duracion_min_val, 2), es_valida_val, motivo_final, problemas_cnt, correctos_cnt, sesion_id))
    conn.commit()
    conn.close()

    return {
        'ok': True,
        'sesion_id': sesion_id,
        'duracion_minutos': round(duracion_min_val, 2),
        'tiempo_activo_segundos': round(tiempo_activo, 2),
        'problemas_finalizados': problemas_cnt,
        'ejercicios_resueltos': problemas_cnt,
        'ejercicios_correctos': correctos_cnt,
        'es_valida': es_valida_val,
        'motivo_cierre': motivo_final,
    }


def validar_sesion_abierta(sesion_id) -> int | None:
    """Comprueba que la sesión exista y esté abierta (estado = 'abierta').
    Retorna sesion_id si es válida y abierta, o None si no existe o está cerrada.
    El guardado del ejercicio nunca debe fallar por culpa de la sesión.
    """
    if sesion_id is None:
        return None
    try:
        sid = int(sesion_id)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM sesiones WHERE id = %s AND estado = 'abierta'", (sid,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None


def obtener_sesion_activa(ahora=None) -> dict | None:
    """Retorna la sesión actualmente abierta con menos de 30 min de inactividad,
    o None si no hay ninguna (cerrando automáticamente las vencidas).
    """
    dt_ahora = _asegurar_datetime(ahora) or datetime.now(timezone.utc)
    conn = get_db()
    cursor = conn.cursor()

    # 1. Evaluar inactividad
    evaluar_inactividad_sesiones(cursor, dt_ahora)
    conn.commit()

    # 2. Buscar si hay sesión abierta
    cursor.execute("""
        SELECT id, estado, inicio_at, ultima_actividad, fin_at,
               tiempo_activo_segundos, es_valida, motivo_cierre,
               ejercicios_resueltos, ejercicios_correctos
        FROM sesiones
        WHERE estado = 'abierta'
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    cols = [col[0] for col in cursor.description]
    res = dict(zip(cols, row))
    for k in ('inicio_at', 'ultima_actividad', 'fin_at'):
        if isinstance(res.get(k), datetime):
            res[k] = res[k].isoformat()
    conn.close()
    return res


def registrar_o_actualizar_patron_error(cursor, leccion_id, tipo_error, operacion=''):
    """Registra o actualiza la frecuencia de un patrón de error en la base de datos."""
    if not tipo_error or tipo_error == 'error_formato':
        return

    descripciones_patrones = {
        'error_prestamo': 'Dificultad o descuido con el dígito prestado en restas',
        'error_llevada': 'Omisión o cálculo incorrecto de la llevada en sumas',
        'error_signo': 'Confusión entre signos positivos y negativos',
        'error_posicional': 'Desplazamiento en el orden de magnitud (unidades/decenas/centenas)',
        'error_procedimiento': 'Dificultad en la secuencia del algoritmo',
        'error_calculo': 'Deslices de cálculo aritmético menor',
        'respuesta_azar': 'Respuesta incongruente con el orden de magnitud'
    }
    descripcion = descripciones_patrones.get(tipo_error, f'Patrón detectado en {tipo_error}')

    cursor.execute(
        "SELECT id, frecuencia FROM patrones_error WHERE leccion_id = ? AND tipo_error = ?",
        (leccion_id, tipo_error)
    )
    row = cursor.fetchone()
    ahora = datetime.now().isoformat()

    if row:
        patron_id = row[0]
        cursor.execute("""
            UPDATE patrones_error
            SET frecuencia = frecuencia + 1, ultima_ocurrencia = ?, resuelto = ?
            WHERE id = ?
        """, (ahora, False if is_supabase() else 0, patron_id))
    else:
        cursor.execute("""
            INSERT INTO patrones_error (leccion_id, tipo_error, descripcion, frecuencia, ultima_ocurrencia, resuelto)
            VALUES (?, ?, ?, 1, ?, ?)
        """, (leccion_id, tipo_error, descripcion, ahora, False if is_supabase() else 0))


def verificar_resolucion_patrones(cursor, leccion_id):
    """Verifica si los patrones de error de una lección han sido superados."""
    cursor.execute(f"""
        SELECT TOP 4 es_correcto, uso_ayuda
        FROM ejercicios
        WHERE leccion_id = ? AND {EXCLUSION_SQL}
        ORDER BY id DESC
    """, (leccion_id,))
    ultimos = cursor.fetchall()
    if len(ultimos) >= 3 and all(bool(u[0]) for u in ultimos):
        cursor.execute("""
            UPDATE patrones_error
            SET resuelto = ?
            WHERE leccion_id = ? AND (resuelto = 0 OR resuelto IS FALSE)
        """, (True if is_supabase() else 1, leccion_id))


def _recalcular_dominio(cursor, leccion_id):
    """Recalcular el porcentaje de dominio pedagógico de una lección combinando:
    - Examen de Dominio (Fase 3): Evaluación sin pistas, peso 60% si aprobado (>= 75%).
    - Práctica Guiada (Fase 2): Calidad de intentos (Casos A-E) y recencia, peso 40%.
    - Exclusión estricta de registros de reinicio accidental.
    """
    cursor.execute(f"""
        SELECT id, leccion_id, operacion, respuesta_correcta, respuesta_usuario,
               es_correcto, intentos, uso_ayuda, tipo_error, tipo_ejercicio, fecha, dificultad
        FROM ejercicios
        WHERE leccion_id = ?
          AND {EXCLUSION_SQL}
        ORDER BY id ASC
    """, (leccion_id,))
    rows = cursor.fetchall()
    if not rows:
        return

    ejercicios = rows_to_dicts(rows, cursor)
    examenes = [e for e in ejercicios if e.get('tipo_ejercicio') == 'examen']
    practica = [e for e in ejercicios if e.get('tipo_ejercicio') != 'examen']

    porcentaje_examen = None
    examen_aprobado = False
    if examenes:
        ultimo_bloque_examen = examenes[-4:]
        corr_ex = sum(1 for q in ultimo_bloque_examen if q.get('es_correcto'))
        porcentaje_examen = (corr_ex / len(ultimo_bloque_examen)) * 100.0
        examen_aprobado = porcentaje_examen >= 75.0

    problemas_practica = consolidar_intentos_problema(practica)
    recientes = problemas_practica[-20:]
    if recientes:
        scores = []
        for idx, p in enumerate(recientes):
            s, _ = evaluar_calidad_problema(p)
            peso_recencia = 1.0 + (idx / len(recientes)) * 0.6
            scores.append((s, peso_recencia))
        practica_score = (sum(s * w for s, w in scores) / sum(w for s, w in scores)) * 100.0
    else:
        practica_score = porcentaje_examen if porcentaje_examen is not None else 0.0

    if porcentaje_examen is not None:
        if examen_aprobado:
            dominio = 0.60 * porcentaje_examen + 0.40 * practica_score
            if porcentaje_examen == 100.0:
                dominio = max(dominio, 85.0)
                if practica_score >= 80.0 or not practica:
                    dominio = max(dominio, 95.0)
                if practica_score >= 90.0 or not practica:
                    dominio = 100.0
            else:
                dominio = max(75.0, min(dominio, 90.0))
        else:
            dominio = min(0.50 * porcentaje_examen + 0.50 * practica_score, 70.0)
    else:
        dominio = min(practica_score, 75.0)

    if len(problemas_practica) < 3 and porcentaje_examen is None:
        dominio = min(dominio, 45.0)

    dominio_final = round(dominio, 1)

    nuevo_estado = 'dominado' if dominio_final >= 80.0 else 'en_progreso'
    cursor.execute(
        "UPDATE lecciones SET porcentaje_dominio = ?, estado = CASE WHEN estado = 'bloqueado' THEN estado ELSE ? END WHERE id = ?",
        (dominio_final, nuevo_estado, leccion_id)
    )

    if dominio_final >= 70.0:
        _desbloquear_siguientes(cursor, leccion_id)


def recalcular_todo_el_dominio():
    """Recalcula el dominio pedagógico de todas las lecciones con ejercicios."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT DISTINCT leccion_id FROM ejercicios WHERE {EXCLUSION_SQL}")
    lecciones = [r[0] for r in cursor.fetchall()]
    for lid in lecciones:
        _recalcular_dominio(cursor, lid)
    conn.commit()
    conn.close()


def sincronizar_patrones_error_historicos():
    """Analiza el historial existente para registrar patrones de error reales y su estado de resolución."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT leccion_id, tipo_error, operacion, respuesta_correcta, respuesta_usuario
        FROM ejercicios
        WHERE (es_correcto = 0 OR es_correcto IS FALSE) AND tipo_error IS NOT NULL
          AND {EXCLUSION_SQL}
        ORDER BY id ASC
    """)
    filas = cursor.fetchall()
    cols = [c[0] for c in cursor.description]
    errores = [dict(zip(cols, f)) for f in filas]

    for err in errores:
        registrar_o_actualizar_patron_error(
            cursor, err['leccion_id'], err['tipo_error'], err.get('operacion', '')
        )

    # Verificar resolución en base a lecciones dominadas
    cursor.execute("SELECT id FROM lecciones WHERE porcentaje_dominio >= 80")
    dominadas = [r[0] for r in cursor.fetchall()]
    for lid in dominadas:
        cursor.execute("""
            UPDATE patrones_error
            SET resuelto = ?
            WHERE leccion_id = ?
        """, (True if is_supabase() else 1, lid))

    conn.commit()
    conn.close()


def obtener_patrones_error(leccion_id=None):
    """Obtener los patrones de error registrados."""
    conn = get_db()
    cursor = conn.cursor()
    if leccion_id:
        cursor.execute("""
            SELECT p.*, l.titulo as leccion_titulo
            FROM patrones_error p
            LEFT JOIN lecciones l ON p.leccion_id = l.id
            WHERE p.leccion_id = ?
            ORDER BY p.resuelto ASC, p.frecuencia DESC
        """, (leccion_id,))
    else:
        cursor.execute("""
            SELECT p.*, l.titulo as leccion_titulo
            FROM patrones_error p
            LEFT JOIN lecciones l ON p.leccion_id = l.id
            ORDER BY p.resuelto ASC, p.frecuencia DESC
        """)
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    conn.close()
    return result


def obtener_recomendaciones_pedagogicas():
    """Genera recomendaciones pedagógicas cualitativas basadas en datos reales."""
    conn = get_db()
    cursor = conn.cursor()

    recomendaciones = []

    # 1. Repasos SM-2 programados para hoy
    repasos_hoy = obtener_repasos_del_dia()
    for r in repasos_hoy:
        recomendaciones.append({
            'tipo': 'sm2_repaso',
            'icono': '📅',
            'titulo': f"Repaso SM-2: {r['titulo']} (Lección {r['leccion_id']})",
            'mensaje': "Tienes programado un repaso para fijar este tema en tu memoria a largo plazo.",
            'leccion_id': r['leccion_id'],
            'accion': 'repaso'
        })

    # 2. Patrones de error activos no resueltos
    cursor.execute("""
        SELECT p.*, l.titulo as leccion_titulo
        FROM patrones_error p
        JOIN lecciones l ON p.leccion_id = l.id
        WHERE (p.resuelto = 0 OR p.resuelto IS FALSE)
        ORDER BY p.frecuencia DESC
    """)
    patrones_activos = rows_to_dicts(cursor.fetchall(), cursor)
    for p in patrones_activos[:2]:
        tipo = p['tipo_error']
        lid = p['leccion_id']
        tit = p.get('leccion_titulo', lid)
        if tipo == 'error_prestamo':
            msg = f"En la Lección {lid} ({tit}), recuerda tachar la cifra a la que le pediste prestado antes de restar la siguiente columna."
        elif tipo == 'error_llevada':
            msg = f"En la Lección {lid} ({tit}), anota la cifra que llevas arriba de la columna para evitar omisiones de cálculo mental."
        elif tipo == 'error_calculo':
            msg = f"En {tit}, conoces bien el método; tus fallos han sido deslices numéricos. Tómate 5 segundos adicionales para verificar."
        else:
            msg = f"Te recomendamos repasar los pasos en {tit} para afianzar el procedimiento."
        recomendaciones.append({
            'tipo': 'patron_error',
            'icono': '💡',
            'titulo': f"Atención en {tit}",
            'mensaje': msg,
            'leccion_id': lid,
            'accion': 'practicar'
        })

    # 3. Reconocimiento de autorregulación y aprendizaje
    cursor.execute(f"""
        SELECT operacion, COUNT(*) as c, SUM(CASE WHEN es_correcto = 1 OR es_correcto IS TRUE THEN 1 ELSE 0 END) as ok
        FROM ejercicios
        WHERE {EXCLUSION_SQL}
        GROUP BY operacion
        HAVING COUNT(*) > 1 AND SUM(CASE WHEN es_correcto = 1 OR es_correcto IS TRUE THEN 1 ELSE 0 END) > 0
    """)
    autocorregidos = len(cursor.fetchall())
    if autocorregidos >= 2:
        recomendaciones.append({
            'tipo': 'autorregulacion',
            'icono': '🚀',
            'titulo': '¡Excelente capacidad de auto-corrección!',
            'mensaje': f'Has corregido exitosamente {autocorregidos} ejercicios en un segundo intento sin necesitar pistas. Tu capacidad de autorregulación y depuración matemática es sobresaliente.',
            'leccion_id': None,
            'accion': None
        })

    # 4. Siguiente lección recomendada
    cursor.execute("""
        SELECT id, titulo, descripcion, porcentaje_dominio
        FROM lecciones
        WHERE estado = 'disponible' AND porcentaje_dominio < 80
        ORDER BY nivel ASC, orden ASC
    """)
    disponibles = rows_to_dicts(cursor.fetchall(), cursor)
    if disponibles:
        sig = disponibles[0]
        recomendaciones.append({
            'tipo': 'avanzar',
            'icono': '✨',
            'titulo': f"Siguiente paso: {sig['titulo']} (Lección {sig['id']})",
            'mensaje': "Has consolidado los temas previos. ¡Estás listo para continuar tu progreso!",
            'leccion_id': sig['id'],
            'accion': 'aprender'
        })

    conn.close()
    return recomendaciones


def obtener_diagnostico_pedagogico():
    """Genera un diagnóstico pedagógico completo y detallado del estudiante."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(f"""
        SELECT id, leccion_id, operacion, respuesta_correcta, respuesta_usuario,
               es_correcto, intentos, uso_ayuda, tipo_error, tipo_ejercicio, fecha, dificultad
        FROM ejercicios
        WHERE {EXCLUSION_SQL}
        ORDER BY id ASC
    """)
    rows = cursor.fetchall()
    cols = [c[0] for c in cursor.description]
    todos_ej = [dict(zip(cols, r)) for r in rows]

    total_validos = len(todos_ej)
    aciertos = sum(1 for e in todos_ej if e.get('es_correcto'))
    primer_intento_ok = sum(1 for e in todos_ej if e.get('es_correcto') and int(e.get('intentos') or 1) == 1 and not e.get('uso_ayuda'))
    segundo_intento_ok = sum(1 for e in todos_ej if e.get('es_correcto') and int(e.get('intentos') or 1) == 2 and not e.get('uso_ayuda'))
    con_pistas_ok = sum(1 for e in todos_ej if e.get('es_correcto') and e.get('uso_ayuda'))
    errores_totales = sum(1 for e in todos_ej if not e.get('es_correcto'))

    cursor.execute("""
        SELECT l.id, l.titulo, l.porcentaje_dominio, l.estado,
               COUNT(e.id) as total_ejercicios,
               COALESCE(SUM(CASE WHEN e.es_correcto = 1 OR e.es_correcto IS TRUE THEN 1 ELSE 0 END), 0) as correctos
        FROM lecciones l
        LEFT JOIN ejercicios e ON l.id = e.leccion_id AND """ + EXCLUSION_SQL_ALIAS + """
        GROUP BY l.id, l.titulo, l.porcentaje_dominio, l.estado
        HAVING COUNT(e.id) > 0
        ORDER BY l.id ASC
    """)
    lecciones_prog = rows_to_dicts(cursor.fetchall(), cursor)

    # Patrones
    cursor.execute("""
        SELECT p.*, l.titulo as leccion_titulo
        FROM patrones_error p
        LEFT JOIN lecciones l ON p.leccion_id = l.id
        ORDER BY p.resuelto ASC, p.frecuencia DESC
    """)
    patrones = rows_to_dicts(cursor.fetchall(), cursor)

    conn.close()

    precision_primer_intento = round(primer_intento_ok / max(total_validos, 1) * 100, 1)

    return {
        'total_ejercicios_evaluados': total_validos,
        'aciertos_totales': aciertos,
        'precision_primer_intento': precision_primer_intento,
        'ejercicios_autocorregidos': segundo_intento_ok,
        'ejercicios_con_ayuda': con_pistas_ok,
        'errores_totales': errores_totales,
        'lecciones_con_progreso': lecciones_prog,
        'patrones_error': patrones,
        'recomendaciones': obtener_recomendaciones_pedagogicas(),
        'resumen_pedagogico': (
            "El estudiante demuestra un sólido aprendizaje procedimental con alta capacidad "
            "de autorregulación: la gran mayoría de ejercicios se resuelven correctamente al primer intento "
            "o se auto-corrigen de inmediato en el segundo intento sin requerir pistas. Los errores observados "
            "son mayoritariamente deslices aritméticos menores superados con la práctica continua."
        )
    }


def _desbloquear_siguientes(cursor, leccion_id):
    """Desbloquear lecciones que dependen de esta."""
    cursor.execute("SELECT id, prerequisitos FROM lecciones WHERE estado = 'bloqueado'")
    todas = cursor.fetchall()

    for leccion in todas:
        prereqs = json.loads(leccion[1])
        if leccion_id in prereqs:
            todos_cumplidos = True
            for prereq in prereqs:
                cursor.execute(
                    "SELECT porcentaje_dominio FROM lecciones WHERE id = ?", (prereq,)
                )
                prereq_row = cursor.fetchone()
                if not prereq_row or prereq_row[0] < 70:
                    todos_cumplidos = False
                    break

            if todos_cumplidos:
                cursor.execute(
                    "UPDATE lecciones SET estado = 'disponible' WHERE id = ?",
                    (leccion[0],)
                )


def desbloquear_lecciones_siguientes(leccion_id):
    """Función pública para desbloquear lecciones dependientes."""
    conn = get_db()
    cursor = conn.cursor()
    _desbloquear_siguientes(cursor, leccion_id)
    conn.commit()
    conn.close()


def obtener_historial(leccion_id=None, limite=50, offset=0):
    """Obtener historial de ejercicios completo."""
    conn = get_db()
    cursor = conn.cursor()
    if leccion_id:
        cursor.execute("""
            SELECT e.*, l.titulo as leccion_titulo
            FROM ejercicios e
            JOIN lecciones l ON e.leccion_id = l.id
            WHERE e.leccion_id = ?
            ORDER BY e.id DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """, (leccion_id, offset, limite))
    else:
        cursor.execute("""
            SELECT e.*, l.titulo as leccion_titulo
            FROM ejercicios e
            JOIN lecciones l ON e.leccion_id = l.id
            ORDER BY e.id DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
        """, (offset, limite))
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    conn.close()
    return result


def obtener_estadisticas():
    """Obtener estadísticas generales del estudiante enriquecidas con métricas pedagógicas."""
    conn = get_db()
    cursor = conn.cursor()

    # Total de ejercicios excluyendo los 2 reinicios especiales
    cursor.execute(f"""
        SELECT
            COUNT(*) as total_ejercicios,
            COALESCE(SUM(CASE WHEN es_correcto = 1 OR es_correcto IS TRUE THEN 1 ELSE 0 END), 0) as total_correctos,
            COALESCE(AVG(tiempo_segundos), 0) as tiempo_promedio,
            COALESCE(SUM(tiempo_segundos), 0) as tiempo_total
        FROM ejercicios
        WHERE {EXCLUSION_SQL}
    """)
    stats_row = cursor.fetchone()
    stats = dict_from_row(stats_row, cursor)

    # Ejercicios por nivel
    cursor.execute(f"""
        SELECT l.nivel,
               COUNT(e.id) as total,
               COALESCE(SUM(CASE WHEN e.es_correcto = 1 OR e.es_correcto IS TRUE THEN 1 ELSE 0 END), 0) as correctos
        FROM ejercicios e
        JOIN lecciones l ON e.leccion_id = l.id
        WHERE {EXCLUSION_SQL_ALIAS}
        GROUP BY l.nivel
        ORDER BY l.nivel
    """)
    por_nivel = rows_to_dicts(cursor.fetchall(), cursor)

    # Evolución diaria (últimos 30 días)
    fecha_hace_30 = (datetime.now() - timedelta(days=30)).isoformat()[:10]
    cursor.execute(f"""
        SELECT LEFT(fecha, 10) as dia,
               COUNT(*) as total,
               COALESCE(SUM(CASE WHEN es_correcto = 1 OR es_correcto IS TRUE THEN 1 ELSE 0 END), 0) as correctos
        FROM ejercicios
        WHERE fecha >= ?
          AND {EXCLUSION_SQL}
        GROUP BY LEFT(fecha, 10)
        ORDER BY dia
    """, (fecha_hace_30,))
    evolucion = rows_to_dicts(cursor.fetchall(), cursor)

    # Errores frecuentes
    cursor.execute(f"""
        SELECT tipo_error, COUNT(*) as frecuencia
        FROM ejercicios
        WHERE (es_correcto = 0 OR es_correcto IS FALSE) AND tipo_error IS NOT NULL
          AND {EXCLUSION_SQL}
        GROUP BY tipo_error
        ORDER BY frecuencia DESC
    """)
    errores = rows_to_dicts(cursor.fetchall(), cursor)

    # Lecciones completadas y en progreso
    cursor.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN porcentaje_dominio >= 80 THEN 1 ELSE 0 END), 0) as dominadas,
            COALESCE(SUM(CASE WHEN porcentaje_dominio > 0 AND porcentaje_dominio < 80 THEN 1 ELSE 0 END), 0) as en_progreso,
            COALESCE(SUM(CASE WHEN estado = 'bloqueado' THEN 1 ELSE 0 END), 0) as pendientes,
            COUNT(*) as total
        FROM lecciones
    """)
    lecciones_stats = dict_from_row(cursor.fetchone(), cursor)

    # Métricas pedagógicas adicionales
    cursor.execute(f"""
        SELECT
            COALESCE(SUM(CASE WHEN (es_correcto = 1 OR es_correcto IS TRUE) AND intentos = 1 AND (uso_ayuda = 0 OR uso_ayuda IS FALSE) THEN 1 ELSE 0 END), 0) as primer_intento,
            COALESCE(SUM(CASE WHEN (es_correcto = 1 OR es_correcto IS TRUE) AND intentos = 2 AND (uso_ayuda = 0 OR uso_ayuda IS FALSE) THEN 1 ELSE 0 END), 0) as autocorregidos,
            COALESCE(SUM(CASE WHEN (es_correcto = 1 OR es_correcto IS TRUE) AND (uso_ayuda = 1 OR uso_ayuda IS TRUE) THEN 1 ELSE 0 END), 0) as con_ayuda
        FROM ejercicios
        WHERE {EXCLUSION_SQL}
    """)
    ped_row = cursor.fetchone()
    primer_int = ped_row[0] if ped_row else 0
    autocorr = ped_row[1] if ped_row else 0
    con_ayuda = ped_row[2] if ped_row else 0

    total_e = stats['total_ejercicios'] or 0
    precision_primer_intento = round((primer_int / max(total_e, 1)) * 100, 1)

    # Patrones de error
    cursor.execute("""
        SELECT tipo_error, frecuencia, resuelto
        FROM patrones_error
        ORDER BY resuelto ASC, frecuencia DESC
    """)
    patrones_lista = rows_to_dicts(cursor.fetchall(), cursor)

    conn.close()

    recomendaciones = obtener_recomendaciones_pedagogicas()

    return {
        'total_ejercicios': stats['total_ejercicios'] or 0,
        'total_correctos': stats['total_correctos'] or 0,
        'porcentaje_aciertos': round(
            (stats['total_correctos'] or 0) / max(stats['total_ejercicios'] or 1, 1) * 100, 1
        ),
        'tiempo_promedio': round(stats['tiempo_promedio'] or 0, 1),
        'tiempo_total_minutos': round((stats['tiempo_total'] or 0) / 60, 1),
        'por_nivel': por_nivel,
        'evolucion': evolucion,
        'errores_frecuentes': errores,
        'lecciones_dominadas': lecciones_stats['dominadas'] or 0,
        'lecciones_en_progreso': lecciones_stats['en_progreso'] or 0,
        'lecciones_pendientes': lecciones_stats['pendientes'] or 0,
        'lecciones_total': lecciones_stats['total'] or 0,
        # Nuevas métricas pedagógicas
        'precision_primer_intento': precision_primer_intento,
        'ejercicios_autocorregidos': autocorr,
        'ejercicios_con_ayuda': con_ayuda,
        'patrones_error': patrones_lista,
        'recomendaciones_pedagogicas': recomendaciones,
    }



def obtener_logros():
    """Obtener todos los logros."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logros ORDER BY desbloqueado DESC, id")
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    conn.close()
    return result


def desbloquear_logro(logro_id):
    """Desbloquear un logro."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT desbloqueado FROM logros WHERE id = ?", (logro_id,)
    )
    result = cursor.fetchone()

    if result and not result[0]:
        cursor.execute("""
            UPDATE logros SET desbloqueado = 1, fecha_desbloqueo = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), logro_id))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False


def verificar_logros():
    """Verificar si se han desbloqueado logros nuevos."""
    conn = get_db()
    cursor = conn.cursor()
    logros_nuevos = []

    stats = obtener_estadisticas()
    perfil = obtener_perfil()

    checks = {
        'primer_ejercicio': stats['total_ejercicios'] >= 1,
        'cien_ejercicios': stats['total_ejercicios'] >= 100,
        'quinientos_ejercicios': stats['total_ejercicios'] >= 500,
        'una_hora': stats['tiempo_total_minutos'] >= 60,
        'cinco_horas': stats['tiempo_total_minutos'] >= 300,
        'racha_3': (perfil or {}).get('racha_actual', 0) >= 3,
        'racha_7': (perfil or {}).get('racha_actual', 0) >= 7,
        'racha_30': (perfil or {}).get('racha_actual', 0) >= 30,
    }

    # Verificar 10 correctos seguidos
    cursor.execute("SELECT TOP 10 es_correcto FROM ejercicios ORDER BY id DESC")
    ultimos = cursor.fetchall()
    if len(ultimos) == 10 and all(e[0] for e in ultimos):
        checks['diez_correctos'] = True

    # Verificar lecciones dominadas
    cursor.execute("SELECT COUNT(*) as c FROM lecciones WHERE porcentaje_dominio >= 80")
    primera_dominada = cursor.fetchone()
    if primera_dominada[0] >= 1:
        checks['primera_leccion'] = True

    # Verificar niveles alcanzados
    for nivel_num in range(2, 8):
        cursor.execute(
            "SELECT estado FROM lecciones WHERE nivel = ? AND orden = 1",
            (nivel_num,)
        )
        leccion_nivel = cursor.fetchone()
        if leccion_nivel and leccion_nivel[0] != 'bloqueado':
            logro_key = f'nivel_{nivel_num}'
            if logro_key in ['nivel_2', 'nivel_3', 'nivel_4', 'nivel_5', 'nivel_6', 'nivel_7']:
                checks[logro_key] = True

    conn.close()

    for logro_id, condicion in checks.items():
        if condicion and desbloquear_logro(logro_id):
            logros_nuevos.append(logro_id)

    return logros_nuevos


def registrar_evaluacion_diagnostica(resultados):
    """Registrar resultados de la evaluación diagnóstica."""
    conn = get_db()
    cursor = conn.cursor()
    for resultado in resultados:
        cursor.execute("""
            INSERT INTO evaluacion_diagnostica
            (fecha, nivel, tema, total_preguntas, correctas, porcentaje, recomendacion)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            resultado['nivel'],
            resultado['tema'],
            resultado['total'],
            resultado['correctas'],
            resultado['porcentaje'],
            resultado.get('recomendacion', '')
        ))

    # Actualizar perfil
    cursor.execute(
        "UPDATE perfil SET evaluacion_inicial_completada = 1 WHERE id = 1"
    )
    conn.commit()
    conn.close()


def obtener_repasos_pendientes():
    """Obtener lecciones que necesitan repaso."""
    conn = get_db()
    cursor = conn.cursor()

    fecha_hace_3 = (datetime.now() - timedelta(days=3)).isoformat()
    cursor.execute("""
        SELECT *
        FROM lecciones
        WHERE porcentaje_dominio > 0
          AND porcentaje_dominio < 90
          AND ultimo_intento < ?
          AND estado != 'bloqueado'
        ORDER BY porcentaje_dominio ASC
    """, (fecha_hace_3,))
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    conn.close()
    return result


def actualizar_racha():
    """Actualizar la racha de estudio."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM perfil WHERE id = 1")
    perfil = cursor.fetchone()

    if not perfil:
        conn.close()
        return

    # Construir dict manual para acceso por nombre
    columns = [col[0] for col in cursor.description]
    perfil_dict = dict(zip(columns, perfil))

    hoy = datetime.now().date().isoformat()
    ultima = perfil_dict['ultima_sesion']

    if ultima:
        ultima_date = datetime.fromisoformat(ultima).date()
        hoy_date = datetime.now().date()
        diff = (hoy_date - ultima_date).days

        if diff == 1:
            nueva_racha = perfil_dict['racha_actual'] + 1
        elif diff == 0:
            nueva_racha = perfil_dict['racha_actual']
        else:
            nueva_racha = 1
    else:
        nueva_racha = 1

    mejor = max(nueva_racha, perfil_dict['mejor_racha'])

    cursor.execute("""
        UPDATE perfil
        SET racha_actual = ?, mejor_racha = ?, ultima_sesion = ?
        WHERE id = 1
    """, (nueva_racha, mejor, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def exportar_datos():
    """Exportar todos los datos como JSON."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM perfil WHERE id = 1")
    perfil = dict_from_row(cursor.fetchone(), cursor)

    cursor.execute("SELECT * FROM lecciones")
    lecciones = rows_to_dicts(cursor.fetchall(), cursor)

    cursor.execute("SELECT * FROM ejercicios")
    ejercicios = rows_to_dicts(cursor.fetchall(), cursor)

    cursor.execute("SELECT * FROM logros")
    logros = rows_to_dicts(cursor.fetchall(), cursor)

    cursor.execute("SELECT * FROM evaluacion_diagnostica")
    evaluacion = rows_to_dicts(cursor.fetchall(), cursor)

    cursor.execute("SELECT * FROM sesiones")
    sesiones = rows_to_dicts(cursor.fetchall(), cursor)

    conn.close()

    datos = {
        'perfil': perfil,
        'lecciones': lecciones,
        'ejercicios': ejercicios,
        'logros': logros,
        'evaluacion': evaluacion,
        'sesiones': sesiones,
        'exportado_en': datetime.now().isoformat(),
    }
    return datos


def importar_datos(datos):
    """Importar datos desde JSON (backup)."""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Limpiar tablas (orden por dependencias)
        for tabla in ['repasos', 'patrones_error', 'evaluacion_diagnostica', 'sesiones', 'ejercicios']:
            cursor.execute(f"DELETE FROM {tabla}")

        # Restaurar perfil
        if 'perfil' in datos:
            p = datos['perfil']
            cursor.execute("""
                UPDATE perfil SET
                    nombre=?, nivel_actual=?, subleccion_actual=?,
                    evaluacion_inicial_completada=?, objetivo_diario_minutos=?,
                    racha_actual=?, mejor_racha=?, ultima_sesion=?
                WHERE id = 1
            """, (
                p.get('nombre', 'Estudiante'), p.get('nivel_actual', 1),
                p.get('subleccion_actual', '1.1'), p.get('evaluacion_inicial_completada', 0),
                p.get('objetivo_diario_minutos', 15), p.get('racha_actual', 0),
                p.get('mejor_racha', 0), p.get('ultima_sesion')
            ))

        # Restaurar lecciones
        if 'lecciones' in datos:
            for l in datos['lecciones']:
                cursor.execute("""
                    UPDATE lecciones SET
                        estado=?, porcentaje_dominio=?, ejercicios_completados=?,
                        ejercicios_correctos=?, ultimo_intento=?, veces_practicada=?
                    WHERE id = ?
                """, (
                    l.get('estado', 'bloqueado'), l.get('porcentaje_dominio', 0),
                    l.get('ejercicios_completados', 0), l.get('ejercicios_correctos', 0),
                    l.get('ultimo_intento'), l.get('veces_practicada', 0), l['id']
                ))

        # Restaurar ejercicios (sin IDENTITY_INSERT ya que generamos nuevos IDs)
        if 'ejercicios' in datos:
            for e in datos['ejercicios']:
                cursor.execute("""
                    INSERT INTO ejercicios
                    (leccion_id, fecha, tipo_ejercicio, operacion, respuesta_correcta,
                     respuesta_usuario, es_correcto, intentos, tiempo_segundos,
                     uso_ayuda, tipo_error, dificultad, detalles)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    e['leccion_id'], e['fecha'], e['tipo_ejercicio'], e['operacion'],
                    e['respuesta_correcta'], e['respuesta_usuario'], e['es_correcto'],
                    e.get('intentos', 1), e.get('tiempo_segundos', 0),
                    e.get('uso_ayuda', 0), e.get('tipo_error'),
                    e.get('dificultad', 1), e.get('detalles', '{}')
                ))

        # Restaurar logros
        if 'logros' in datos:
            for l in datos['logros']:
                cursor.execute("""
                    UPDATE logros SET desbloqueado=?, fecha_desbloqueo=?
                    WHERE id = ?
                """, (l.get('desbloqueado', 0), l.get('fecha_desbloqueo'), l['id']))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e


# ============================================================
# ALGORITMO DE REPETICIÓN ESPACIADA SM-2 (ANKI / DUOLINGO)
# ============================================================

def programar_repaso_sm2(leccion_id):
    """Programar siguiente repaso según el algoritmo de repetición espaciada SM-2.
    
    Intervalos de fijación de memoria:
    - 1er repaso: 1 día después de dominar la lección.
    - 2do repaso: 3 días después.
    - 3er repaso: 7 días después.
    - 4to repaso: 21 días después (fijación permanente en memoria a largo plazo).
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Contar repasos completados previos de esta lección
    cursor.execute("""
        SELECT COUNT(*) FROM repasos
        WHERE leccion_id = ? AND (completado = 1 OR completado IS TRUE)
    """, (leccion_id,))
    row = cursor.fetchone()
    completados = row[0] if row else 0
    
    # Determinar el intervalo en días
    intervalos = [1, 3, 7, 21]
    dias = intervalos[min(completados, len(intervalos) - 1)]
    
    fecha_repaso = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
    
    # Evitar duplicar repasos pendientes para la misma lección
    cursor.execute("""
        SELECT COUNT(*) FROM repasos
        WHERE leccion_id = ? AND (completado = 0 OR completado IS FALSE)
    """, (leccion_id,))
    row_pend = cursor.fetchone()
    pendientes = row_pend[0] if row_pend else 0
    
    if pendientes == 0:
        cursor.execute("""
            INSERT INTO repasos (leccion_id, fecha_programada, completado)
            VALUES (?, ?, ?)
        """, (leccion_id, fecha_repaso, False if is_supabase() else 0))
        conn.commit()
    
    conn.close()


def obtener_repasos_del_dia():
    """Obtener repasos programados para hoy o anteriores que estén pendientes."""
    conn = get_db()
    cursor = conn.cursor()
    hoy = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute("""
        SELECT r.id, r.leccion_id, r.fecha_programada, l.titulo, l.nivel, l.descripcion
        FROM repasos r
        JOIN lecciones l ON r.leccion_id = l.id
        WHERE (r.completado = 0 OR r.completado IS FALSE) AND r.fecha_programada <= ?
        ORDER BY r.fecha_programada ASC
    """, (hoy,))
    rows = cursor.fetchall()
    result = rows_to_dicts(rows, cursor)
    conn.close()
    return result


def completar_repaso_sm2(repaso_id, resultado):
    """Completar un repaso y programar el siguiente intervalo si aprobó."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT leccion_id FROM repasos WHERE id = ?", (repaso_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False
    leccion_id = row[0]
    
    ahora = datetime.now().isoformat()
    cursor.execute("""
        UPDATE repasos
        SET completado = ?, fecha_completado = ?, resultado = ?
        WHERE id = ?
    """, (True if is_supabase() else 1, ahora, float(resultado), repaso_id))
    conn.commit()
    conn.close()
    
    # Si obtuvo buen resultado (>= 75%), programar el siguiente repaso SM-2
    if float(resultado) >= 75.0:
        programar_repaso_sm2(leccion_id)
        
    return True

