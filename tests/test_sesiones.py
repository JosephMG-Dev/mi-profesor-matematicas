"""
Tests - Fase 1 v2: Sistema de Sesiones de Estudio (PostgreSQL)
Usa exclusivamente TEST_DATABASE_URL y reloj inyectable (sin datetime.now() ni rangos aproximados).
"""
import os
import pytest
from datetime import datetime, timedelta, timezone

import database
from app import app


# ============================================================
# CONFIGURACIÓN Y FIXTURES
# ============================================================

TEST_DB_URL = os.environ.get('TEST_DATABASE_URL')

@pytest.fixture(autouse=True)
def verificar_test_db(monkeypatch):
    """Garantiza que los tests de BD usen SOLO TEST_DATABASE_URL y NUNCA lean SUPABASE_DB_URL."""
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL no configurada en .env")
    # Forzar a database.get_db a usar TEST_DB_URL
    monkeypatch.setenv('SUPABASE_DB_URL', TEST_DB_URL)
    monkeypatch.setenv('DATABASE_URL', TEST_DB_URL)


@pytest.fixture
def limpiar_sesiones():
    """Limpia sesiones y ejercicios creados durante la prueba."""
    ids_sesiones = []
    ids_ejercicios = []

    conn = database.get_db()
    cur = conn.cursor()
    # Asegurar que no haya sesiones abiertas previas colgadas
    cur.execute("UPDATE sesiones SET estado = 'cerrada' WHERE estado = 'abierta'")
    conn.commit()
    conn.close()

    yield {
        'sesiones': ids_sesiones,
        'ejercicios': ids_ejercicios,
    }

    # Cleanup
    conn = database.get_db()
    cur = conn.cursor()
    if ids_ejercicios:
        cur.execute("DELETE FROM ejercicios WHERE id = ANY(%s)", (ids_ejercicios,))
    if ids_sesiones:
        cur.execute("DELETE FROM ejercicios WHERE sesion_id = ANY(%s)", (ids_sesiones,))
        cur.execute("DELETE FROM sesiones WHERE id = ANY(%s)", (ids_sesiones,))
    cur.execute("UPDATE sesiones SET estado = 'cerrada' WHERE estado = 'abierta'")
    conn.commit()
    conn.close()


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


# ============================================================
# 1. FUNCIÓN PURA DE TIEMPO
# ============================================================

def test_calcular_tiempo_a_sumar_intervalos_exactos():
    """Prueba obligatoria con intervalos literales:
    10:00 -> 10:01 (60 s)
    10:01 -> 10:03 (120 s)
    10:03 -> 10:10 (120 s)
    10:10 -> 10:15 (120 s)
    """
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_01 = datetime(2026, 10, 4, 10, 1, 0, tzinfo=timezone.utc)
    t10_03 = datetime(2026, 10, 4, 10, 3, 0, tzinfo=timezone.utc)
    t10_10 = datetime(2026, 10, 4, 10, 10, 0, tzinfo=timezone.utc)
    t10_15 = datetime(2026, 10, 4, 10, 15, 0, tzinfo=timezone.utc)

    # 10:00 -> 10:01 = 60s
    assert database.calcular_tiempo_a_sumar(t10_00, t10_01) == 60.0

    # 10:01 -> 10:03 = 120s
    assert database.calcular_tiempo_a_sumar(t10_01, t10_03) == 120.0

    # 10:03 -> 10:10 = 420s -> min(420, 120) = 120s
    assert database.calcular_tiempo_a_sumar(t10_03, t10_10) == 120.0

    # 10:10 -> 10:15 = 300s -> min(300, 120) = 120s
    assert database.calcular_tiempo_a_sumar(t10_10, t10_15) == 120.0

    # Delta negativo o cero debe dar 0.0
    assert database.calcular_tiempo_a_sumar(t10_01, t10_00) == 0.0
    assert database.calcular_tiempo_a_sumar(t10_01, t10_01) == 0.0


# ============================================================
# 2. DOBLE SESIÓN E ÍNDICE ÚNICO PARCIAL
# ============================================================

def test_doble_sesion_e_indice_unico(limpiar_sesiones):
    """Comprueba que no se permitan dos sesiones abiertas y maneja la violación del índice único."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_05 = datetime(2026, 10, 4, 10, 5, 0, tzinfo=timezone.utc)

    sid1, rean1 = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid1)
    assert sid1 > 0
    assert rean1 is False

    # Intentar abrir una segunda sesión retorna la existente sin error 500
    sid2, rean2 = database.iniciar_sesion(ahora=t10_05)
    assert sid2 == sid1
    assert rean2 is True

    # Verificar que el índice único parcial realmente impida dos sesiones 'abierta'
    conn = database.get_db()
    cur = conn.cursor()
    with pytest.raises(Exception):
        cur.execute("""
            INSERT INTO sesiones (estado, inicio_at, ultima_actividad)
            VALUES ('abierta', %s, %s)
        """, (t10_05, t10_05))
        conn.commit()
    conn.rollback()
    conn.close()


# ============================================================
# 3. HEARTBEAT QUE ACUMULA TIEMPO
# ============================================================

def test_heartbeat_acumula_tiempo(limpiar_sesiones):
    """El heartbeat acumula tiempo_activo_segundos de manera determinista."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_01 = datetime(2026, 10, 4, 10, 1, 0, tzinfo=timezone.utc)
    t10_03 = datetime(2026, 10, 4, 10, 3, 0, tzinfo=timezone.utc)

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    # 10:00 -> 10:01 = 60s
    res1 = database.registrar_heartbeat(sid, ahora=t10_01)
    assert res1['ok'] is True
    assert res1['tiempo_activo_segundos'] == 60.0

    # 10:01 -> 10:03 = 120s acumulando a 180s
    res2 = database.registrar_heartbeat(sid, ahora=t10_03)
    assert res2['ok'] is True
    assert res2['tiempo_activo_segundos'] == 180.0


# ============================================================
# 4. HEARTBEAT SOBRE SESIÓN VENCIDA
# ============================================================

def test_heartbeat_sesion_vencida_no_revive(limpiar_sesiones):
    """Un heartbeat sobre una sesión con >30 min de inactividad no la revive:
    la cierra y fin_at queda igual a ultima_actividad (no la hora actual).
    """
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_05 = datetime(2026, 10, 4, 10, 5, 0, tzinfo=timezone.utc)
    t10_45 = datetime(2026, 10, 4, 10, 45, 0, tzinfo=timezone.utc)  # 40 min después de 10:05

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    database.registrar_heartbeat(sid, ahora=t10_05)

    # A las 10:45 (han pasado 40 min desde la última actividad 10:05)
    res = database.registrar_heartbeat(sid, ahora=t10_45)
    assert res['ok'] is False
    assert res.get('expirada') is True
    assert res.get('motivo') == 'inactividad'

    # Verificar estado en la base de datos
    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT estado, fin_at, motivo_cierre FROM sesiones WHERE id = %s", (sid,))
    row = cur.fetchone()
    conn.close()

    assert row[0] == 'cerrada'
    assert row[2] == 'inactividad'
    # fin_at debe ser exactamente 10:05 (la última actividad), NO 10:45
    assert row[1] == t10_05


# ============================================================
# 5. CIERRE POR INACTIVIDAD
# ============================================================

def test_cierre_por_inactividad(limpiar_sesiones):
    """Sesión abandonada >30 min se cierra en el servidor al consultar sesión activa."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_35 = datetime(2026, 10, 4, 10, 35, 0, tzinfo=timezone.utc)  # 35 min después

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    # A las 10:35 se consulta la sesión activa
    activa = database.obtener_sesion_activa(ahora=t10_35)
    assert activa is None, "Una sesión inactiva por más de 30 min no debe figurar activa"

    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT estado, fin_at, motivo_cierre FROM sesiones WHERE id = %s", (sid,))
    row = cur.fetchone()
    conn.close()

    assert row[0] == 'cerrada'
    assert row[1] == t10_00  # fin_at = ultima_actividad
    assert row[2] == 'inactividad'


# ============================================================
# 6. PROBLEMAS FINALIZADOS: 0, 1, 2 Y 3 (VALIDEZ)
# ============================================================

@pytest.mark.parametrize("num_problemas,espera_valida", [
    (0, False),
    (1, False),
    (2, False),
    (3, True),
])
def test_validez_segun_problemas_finalizados(limpiar_sesiones, num_problemas, espera_valida):
    """Una sesión es válida si y solo si problemas_finalizados >= 3."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_10 = datetime(2026, 10, 4, 10, 10, 0, tzinfo=timezone.utc)

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    # Insertar problemas distintos
    for i in range(num_problemas):
        eid = database.registrar_ejercicio(
            leccion_id='1.1',
            tipo_ejercicio='practica',
            operacion=f'{i+1} + {i+1}',
            respuesta_correcta=str((i+1)*2),
            respuesta_usuario=str((i+1)*2),
            es_correcto=True,
            intentos=1,
            sesion_id=sid
        )
        limpiar_sesiones['ejercicios'].append(eid)

    res = database.cerrar_sesion(sid, motivo='manual', ahora=t10_10)
    assert res['ok'] is True
    assert res['problemas_finalizados'] == num_problemas
    assert res['es_valida'] is espera_valida


# ============================================================
# 7. VARIOS INTENTOS DEL MISMO PROBLEMA CUENTAN 1
# ============================================================

def test_varios_intentos_mismo_problema_cuentan_uno(limpiar_sesiones):
    """Reutiliza la consolidación de intentos: múltiples intentos de la misma operación cuentan como 1 problema."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_08 = datetime(2026, 10, 4, 10, 8, 0, tzinfo=timezone.utc)

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    # Intento 1: falla
    e1 = database.registrar_ejercicio(
        leccion_id='1.1',
        tipo_ejercicio='practica',
        operacion='45 + 55',
        respuesta_correcta='100',
        respuesta_usuario='90',
        es_correcto=False,
        intentos=1,
        sesion_id=sid
    )
    limpiar_sesiones['ejercicios'].append(e1)

    # Intento 2: acierta
    e2 = database.registrar_ejercicio(
        leccion_id='1.1',
        tipo_ejercicio='practica',
        operacion='45 + 55',
        respuesta_correcta='100',
        respuesta_usuario='100',
        es_correcto=True,
        intentos=2,
        sesion_id=sid
    )
    limpiar_sesiones['ejercicios'].append(e2)

    res = database.cerrar_sesion(sid, motivo='manual', ahora=t10_08)
    assert res['ok'] is True
    assert res['problemas_finalizados'] == 1, "Dos intentos de '45 + 55' deben consolidar en 1 solo problema"
    assert res['ejercicios_correctos'] == 1
    assert res['es_valida'] is False, "1 problema no alcanza el mínimo de 3"


# ============================================================
# 8. SESION_ID GUARDADO EN PRÁCTICA Y EN EXAMEN
# ============================================================

def test_sesion_id_guardado_en_practica_y_examen(client, limpiar_sesiones):
    """Los endpoints /api/ejercicio/verificar y /api/lecciones/.../examen/evaluar guardan sesion_id."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    # 1. Práctica
    res_pr = client.post('/api/ejercicio/verificar', json={
        'leccion_id': '1.1',
        'tipo_ejercicio': 'practica',
        'operacion': '10 + 20',
        'respuesta_correcta': '30',
        'respuesta_usuario': '30',
        'tiempo_segundos': 15,
        'intentos': 1,
        'sesion_id': sid
    })
    assert res_pr.status_code == 200

    # 2. Examen
    res_ex = client.post('/api/lecciones/1.1/examen/evaluar', json={
        'respuestas': [
            {'operacion': '5 + 5', 'respuesta_correcta': '10', 'respuesta_usuario': '10', 'tiempo_segundos': 5, 'dificultad': 1},
            {'operacion': '8 + 8', 'respuesta_correcta': '16', 'respuesta_usuario': '16', 'tiempo_segundos': 6, 'dificultad': 1},
        ],
        'sesion_id': sid
    })
    assert res_ex.status_code == 200

    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, operacion, sesion_id FROM ejercicios WHERE sesion_id = %s ORDER BY id ASC", (sid,))
    filas = cur.fetchall()
    conn.close()

    for f in filas:
        limpiar_sesiones['ejercicios'].append(f[0])

    assert len(filas) == 3, "Debe haber 1 de práctica y 2 de examen vinculados"
    assert all(f[2] == sid for f in filas)


# ============================================================
# 9. EJERCICIO SIN SESIÓN (NULL) FUNCIONA
# ============================================================

def test_ejercicio_sin_sesion_null(client, limpiar_sesiones):
    """Un ejercicio enviado sin sesion_id se registra con sesion_id = NULL."""
    res = client.post('/api/ejercicio/verificar', json={
        'leccion_id': '1.1',
        'tipo_ejercicio': 'practica',
        'operacion': '7 + 8',
        'respuesta_correcta': '15',
        'respuesta_usuario': '15',
        'tiempo_segundos': 10,
        'intentos': 1,
        # sin sesion_id
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['es_correcto'] is True

    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, sesion_id FROM ejercicios WHERE operacion = '7 + 8' ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()

    if row:
        limpiar_sesiones['ejercicios'].append(row[0])
        assert row[1] is None, "sesion_id debe ser NULL"


# ============================================================
# 10. RECUPERACIÓN DE SESIÓN ABIERTA
# ============================================================

def test_recuperacion_sesion_abierta(client, limpiar_sesiones):
    """GET /api/sesion/activa retorna la sesión abierta no vencida."""
    # 1. Verificación interna con reloj inyectable
    t1 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 10, 4, 10, 15, 0, tzinfo=timezone.utc)
    sid, _ = database.iniciar_sesion(ahora=t1)
    limpiar_sesiones['sesiones'].append(sid)

    activa = database.obtener_sesion_activa(ahora=t2)
    assert activa is not None
    assert activa['id'] == sid
    assert activa['estado'] == 'abierta'

    # 2. Verificación del ciclo HTTP completo en tiempo actual
    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("UPDATE sesiones SET estado = 'cerrada' WHERE estado = 'abierta'")
    conn.commit()
    conn.close()

    res_post = client.post('/api/sesion/iniciar')
    assert res_post.status_code == 200
    data_post = res_post.get_json()
    assert data_post['ok'] is True
    sid_http = data_post['sesion_id']
    limpiar_sesiones['sesiones'].append(sid_http)

    res_get = client.get('/api/sesion/activa')
    assert res_get.status_code == 200
    data_get = res_get.get_json()
    assert data_get is not None
    assert data_get['id'] == sid_http
    assert data_get['estado'] == 'abierta'


# ============================================================
# 11. GET ACTIVA CON SESIÓN VENCIDA
# ============================================================

def test_get_activa_con_sesion_vencida(limpiar_sesiones):
    """GET activa cuando la sesión superó 30 min de inactividad retorna None y la cierra."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_31 = datetime(2026, 10, 4, 10, 31, 0, tzinfo=timezone.utc)  # 31 min después

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    activa = database.obtener_sesion_activa(ahora=t10_31)
    assert activa is None

    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT estado, fin_at, motivo_cierre FROM sesiones WHERE id = %s", (sid,))
    row = cur.fetchone()
    conn.close()

    assert row[0] == 'cerrada'
    assert row[1] == t10_00
    assert row[2] == 'inactividad'


# ============================================================
# 12. CERRAR SESIÓN YA CERRADA
# ============================================================

def test_cerrar_sesion_ya_cerrada(limpiar_sesiones):
    """Cerrar una sesión que ya estaba cerrada no falla ni altera datos y retorna ya_cerrada=True."""
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_10 = datetime(2026, 10, 4, 10, 10, 0, tzinfo=timezone.utc)
    t10_15 = datetime(2026, 10, 4, 10, 15, 0, tzinfo=timezone.utc)

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    # Primer cierre
    res1 = database.cerrar_sesion(sid, motivo='manual', ahora=t10_10)
    assert res1['ok'] is True
    assert res1.get('ya_cerrada') is not True

    # Segundo cierre sobre la misma sesión
    res2 = database.cerrar_sesion(sid, motivo='manual', ahora=t10_15)
    assert res2['ok'] is True
    assert res2.get('ya_cerrada') is True
    assert res2['sesion_id'] == sid


# ============================================================
# 13. VALIDACIÓN DE API CERRAR Y MOTIVOS
# ============================================================

def test_api_sesion_cerrar_validacion_y_motivos(client, limpiar_sesiones):
    """Verifica manejo de errores de tipo en sesion_id y restricción de motivos permitidos."""
    # 1. Error 400 si falta sesion_id
    r_falta = client.post('/api/sesion/cerrar', json={})
    assert r_falta.status_code == 400
    assert r_falta.get_json()['motivo'] == 'falta_sesion_id'

    # 2. Error 400 si sesion_id no es entero
    r_inval = client.post('/api/sesion/cerrar', json={'sesion_id': 'no_es_un_numero'})
    assert r_inval.status_code == 400
    assert r_inval.get_json()['motivo'] == 'sesion_id_invalido'

    # 3. Motivo no permitido se convierte a 'manual'
    sid1, _ = database.iniciar_sesion()
    limpiar_sesiones['sesiones'].append(sid1)

    r_motivo = client.post('/api/sesion/cerrar', json={'sesion_id': sid1, 'motivo': 'desconocido_o_inventado'})
    assert r_motivo.status_code == 200
    assert r_motivo.get_json()['motivo_cierre'] == 'manual'

    # 4. Motivo permitido 'cierre_pestana' se respeta
    sid2, _ = database.iniciar_sesion()
    limpiar_sesiones['sesiones'].append(sid2)

    r_pestana = client.post('/api/sesion/cerrar', json={'sesion_id': sid2, 'motivo': 'cierre_pestana'})
    assert r_pestana.status_code == 200
    assert r_pestana.get_json()['motivo_cierre'] == 'cierre_pestana'


# ============================================================
# 14. CIERRE MANUAL DE SESIÓN VENCIDA RETORNA INACTIVIDAD
# ============================================================

def test_cierre_manual_sesion_vencida_motivo_inactividad(limpiar_sesiones):
    """Sesión con 40 min de inactividad + cierre manual:
    debe cerrarse con motivo 'inactividad', fin_at = ultima_actividad,
    y duración calculada hasta ultima_actividad (no hasta la hora actual).
    """
    t10_00 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    t10_10 = datetime(2026, 10, 4, 10, 10, 0, tzinfo=timezone.utc)
    t10_50 = datetime(2026, 10, 4, 10, 50, 0, tzinfo=timezone.utc)  # 40 min después de última actividad

    sid, _ = database.iniciar_sesion(ahora=t10_00)
    limpiar_sesiones['sesiones'].append(sid)

    # Heartbeat a las 10:10 (fija ultima_actividad = 10:10)
    database.registrar_heartbeat(sid, ahora=t10_10)

    # A las 10:50 (40 min después) se invoca cierre manual
    res = database.cerrar_sesion(sid, motivo='manual', ahora=t10_50)

    assert res['ok'] is True
    assert res['motivo_cierre'] == 'inactividad'
    # Duración calculada hasta ultima_actividad (10:10 - 10:00 = 10 min), NO hasta 10:50 (50 min)
    assert res['duracion_minutos'] == 10.0

    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT estado, fin_at, motivo_cierre, duracion_minutos FROM sesiones WHERE id = %s", (sid,))
    row = cur.fetchone()
    conn.close()

    assert row[0] == 'cerrada'
    assert row[1] == t10_10  # fin_at = ultima_actividad
    assert row[2] == 'inactividad'
    assert row[3] == 10.0


# ============================================================
# 15. SESION_ID INEXISTENTE O CERRADA EN EJERCICIOS GUARDA NULL
# ============================================================

def test_ejercicio_sesion_inexistente_o_cerrada_guarda_null(client, limpiar_sesiones):
    """En /api/ejercicio/verificar y examen, sesion_id inexistente o de sesión cerrada
    guarda el ejercicio con sesion_id = NULL sin fallar.
    """
    # 1. sesion_id inexistente (ej. 9999999) en práctica
    res_inex = client.post('/api/ejercicio/verificar', json={
        'leccion_id': '1.1',
        'tipo_ejercicio': 'practica',
        'operacion': '100 + 200',
        'respuesta_correcta': '300',
        'respuesta_usuario': '300',
        'tiempo_segundos': 10,
        'intentos': 1,
        'sesion_id': 9999999
    })
    assert res_inex.status_code == 200
    assert res_inex.get_json()['es_correcto'] is True

    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, sesion_id FROM ejercicios WHERE operacion = '100 + 200' ORDER BY id DESC LIMIT 1")
    row1 = cur.fetchone()
    assert row1 is not None
    limpiar_sesiones['ejercicios'].append(row1[0])
    assert row1[1] is None, "Sesión inexistente debe resultar en sesion_id NULL"

    # 2. sesion_id de sesión ya cerrada en práctica
    t1 = datetime(2026, 10, 4, 10, 0, 0, tzinfo=timezone.utc)
    sid, _ = database.iniciar_sesion(ahora=t1)
    limpiar_sesiones['sesiones'].append(sid)
    database.cerrar_sesion(sid, motivo='manual', ahora=t1)

    res_cerr = client.post('/api/ejercicio/verificar', json={
        'leccion_id': '1.1',
        'tipo_ejercicio': 'practica',
        'operacion': '200 + 300',
        'respuesta_correcta': '500',
        'respuesta_usuario': '500',
        'tiempo_segundos': 12,
        'intentos': 1,
        'sesion_id': sid
    })
    assert res_cerr.status_code == 200
    assert res_cerr.get_json()['es_correcto'] is True

    cur.execute("SELECT id, sesion_id FROM ejercicios WHERE operacion = '200 + 300' ORDER BY id DESC LIMIT 1")
    row2 = cur.fetchone()
    assert row2 is not None
    limpiar_sesiones['ejercicios'].append(row2[0])
    assert row2[1] is None, "Sesión cerrada debe resultar en sesion_id NULL"

    # 3. sesion_id de sesión cerrada en examen
    res_ex = client.post('/api/lecciones/1.1/examen/evaluar', json={
        'respuestas': [
            {'operacion': '400 + 100', 'respuesta_correcta': '500', 'respuesta_usuario': '500', 'tiempo_segundos': 5, 'dificultad': 1}
        ],
        'sesion_id': sid
    })
    assert res_ex.status_code == 200
    cur.execute("SELECT id, sesion_id FROM ejercicios WHERE operacion = '400 + 100' ORDER BY id DESC LIMIT 1")
    row3 = cur.fetchone()
    conn.close()
    assert row3 is not None
    limpiar_sesiones['ejercicios'].append(row3[0])
    assert row3[1] is None, "Sesión cerrada en examen debe resultar en sesion_id NULL"
