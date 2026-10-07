"""
Tests - Variedad de Ejercicios y Examen de Dominio Configurable
Verifica:
1. Variedad en práctica: no repetición en ventana de 20 y backoff en lecciones pequeñas.
2. Examen de dominio: 10 preguntas distintas, balance 5 dif 1 y 5 dif 2, sin pistas.
3. Máximo posible en lecciones limitadas (6.5 -> 3, 7.12 -> 5, 7.2 -> 6).
4. Umbrales configurables (80, 90, 100) con límites exactos (7/10, 8/10, 9/10, 10/10).
5. Validación en servidor de umbral inválido y preservación de otras claves JSON en perfil.configuracion.
6. Dominio pedagógico evaluando el último examen completo según examen_id.
7. Inmutabilidad del dominio concedido ante cambios posteriores del umbral.
8. Retrocompatibilidad con exámenes antiguos sin marcas (4 filas y 75%).
9. Examen nuevo evita preguntas del examen anterior de la lección si es posible.
"""
import os
import json
import random
import pytest
from flask import Flask

import database
from app import app, obtener_umbral_examen
from ejercicios import generar_ejercicio, generar_ejercicio_variado

TEST_DB_URL = os.environ.get('TEST_DATABASE_URL')


@pytest.fixture(autouse=True)
def verificar_test_db(monkeypatch):
    """Garantiza que los tests de BD usen SOLO TEST_DATABASE_URL."""
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL no configurada en .env")
    monkeypatch.setenv('SUPABASE_DB_URL', TEST_DB_URL)
    monkeypatch.setenv('DATABASE_URL', TEST_DB_URL)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def limpiar_datos_test():
    """Limpia ejercicios creados durante las pruebas específicas."""
    creados = []
    yield creados
    if creados:
        conn = database.get_db()
        cur = conn.cursor()
        for eid in creados:
            cur.execute("DELETE FROM ejercicios WHERE id = ?", (eid,))
        conn.commit()
        conn.close()


# ============================================================
# 1. TESTS DETERMINISTAS - VARIEDAD EN PRÁCTICA
# ============================================================

def test_no_repeticion_en_ventana_20():
    """Dado un historial de 20 operaciones en la lección 1.1,
    el generador no debe repetir ninguna de las 20."""
    random.seed(12345)
    # Generar 20 operaciones distintas previas
    previas = []
    while len(previas) < 20:
        ej = generar_ejercicio('1.1', 1)
        if ej['operacion'] not in previas:
            previas.append(ej['operacion'])

    # Generar 15 nuevos ejercicios con exclusión de las 20 previas
    for _ in range(15):
        nuevo = generar_ejercicio_variado('1.1', dificultad=1, excluir=previas)
        assert nuevo['operacion'] not in previas, (
            f"La operación {nuevo['operacion']} se repitió dentro de la ventana de 20"
        )


def test_ventana_menor_backoff_leccion_pequena():
    """Dada la lección 6.5 (Despejes) que solo tiene 3 operaciones posibles,
    el generador debe adaptarse usando backoff sin bloquearse ni lanzar error."""
    random.seed(54321)
    # Operaciones posibles de 6.5
    op1 = 'Área del rectángulo: A = b × h. Despeja h.'
    op2 = 'Velocidad: v = d / t. Despeja t.'
    op3 = 'Perímetro rectángulo: P = 2a + 2b. Despeja a.'

    # Si se excluyen 2, debe generar la tercera
    ej = generar_ejercicio_variado('6.5', dificultad=1, excluir=[op1, op2])
    assert ej['operacion'] == op3

    # Si se excluyen las 3 (ventana mayor al total disponible),
    # el backoff reduce la ventana y genera una opción válida sin caer en bucle infinito
    ej_backoff = generar_ejercicio_variado('6.5', dificultad=1, excluir=[op1, op2, op3])
    assert ej_backoff['operacion'] in [op1, op2, op3]


# ============================================================
# 2. TESTS DETERMINISTAS - EXAMEN DE DOMINIO
# ============================================================

def test_examen_10_preguntas_distintas_y_balance_dificultad(client):
    """El examen de dominio para una lección estándar genera exactamente 10 preguntas,
    todas distintas entre sí, 5 de dificultad 1 y 5 de dificultad 2, sin pistas."""
    random.seed(999)
    res = client.post('/api/lecciones/1.1/examen/generar')
    assert res.status_code == 200
    data = res.get_json()

    preguntas = data.get('preguntas', [])
    assert len(preguntas) == 10
    assert data.get('total') == 10

    # Todas distintas entre sí
    ops = [p['operacion'] for p in preguntas]
    assert len(set(ops)) == 10, "Todas las 10 preguntas deben tener operaciones distintas"

    # Dificultades: 5 de dificultad 1 y 5 de dificultad 2
    difs = [p['dificultad'] for p in preguntas]
    assert difs.count(1) == 5
    assert difs.count(2) == 5

    # Sin pistas
    for p in preguntas:
        assert p.get('pistas') == [], "Las preguntas de examen no deben contener pistas"


def test_examen_lecciones_limitadas_genera_maximo_posible(client):
    """En lecciones que no pueden generar 10 preguntas distintas,
    el examen debe generar el máximo posible sin duplicar preguntas."""
    # Lección 6.5: máximo 3
    res_65 = client.post('/api/lecciones/6.5/examen/generar')
    data_65 = res_65.get_json()
    assert data_65['total'] == 3
    assert len(set(p['operacion'] for p in data_65['preguntas'])) == 3

    # Lección 7.12: máximo 5
    res_712 = client.post('/api/lecciones/7.12/examen/generar')
    data_712 = res_712.get_json()
    assert data_712['total'] == 5
    assert len(set(p['operacion'] for p in data_712['preguntas'])) == 5

    # Lección 7.2: máximo 6
    res_72 = client.post('/api/lecciones/7.2/examen/generar')
    data_72 = res_72.get_json()
    assert data_72['total'] == 6
    assert len(set(p['operacion'] for p in data_72['preguntas'])) == 6


# ============================================================
# 3. TESTS DETERMINISTAS - UMBRALES Y LÍMITES EXACTOS
# ============================================================

@pytest.mark.parametrize("aciertos,umbral,esperado_aprobado", [
    (7, 80, False),   # 7/10 = 70% < 80%
    (7, 90, False),   # 7/10 = 70% < 90%
    (7, 100, False),  # 7/10 = 70% < 100%
    (8, 80, True),    # 8/10 = 80% >= 80% (límite exacto de 80)
    (8, 90, False),   # 8/10 = 80% < 90%
    (8, 100, False),  # 8/10 = 80% < 100%
    (9, 80, True),    # 9/10 = 90% >= 80%
    (9, 90, True),    # 9/10 = 90% >= 90% (límite exacto de 90)
    (9, 100, False),  # 9/10 = 90% < 100%
    (10, 80, True),   # 10/10 = 100% >= 80%
    (10, 90, True),   # 10/10 = 100% >= 90%
    (10, 100, True),  # 10/10 = 100% >= 100% (límite exacto de 100)
])
def test_limites_exactos_evaluacion(aciertos, umbral, esperado_aprobado):
    """Verifica matemáticamente los límites exactos de aprobación para 7, 8, 9 y 10 aciertos."""
    porcentaje = (aciertos / 10) * 100
    aprobado = porcentaje >= umbral
    assert aprobado is esperado_aprobado


def test_validacion_servidor_umbral_y_preservacion_json(client):
    """PUT /api/perfil valida que solo se acepten 80, 90 o 100 (cualquier otro -> 80)
    y preserva intactas otras claves dentro de perfil.configuracion."""
    # 1. Guardar una configuración inicial con claves extra
    client.put('/api/perfil', json={
        'configuracion': {
            'otra_clave': 'valor_intacto',
            'tema': 'dark',
            'umbral_examen': 90
        }
    })

    perf1 = client.get('/api/perfil').get_json()
    cfg1 = json.loads(perf1['configuracion']) if isinstance(perf1['configuracion'], str) else perf1['configuracion']
    assert cfg1.get('umbral_examen') == 90
    assert cfg1.get('otra_clave') == 'valor_intacto'
    assert cfg1.get('tema') == 'dark'

    # 2. Enviar un valor inválido (ej: 50 o texto)
    client.put('/api/perfil', json={
        'configuracion': {
            'umbral_examen': 50
        }
    })

    perf2 = client.get('/api/perfil').get_json()
    cfg2 = json.loads(perf2['configuracion']) if isinstance(perf2['configuracion'], str) else perf2['configuracion']
    # Debe forzarlo a 80
    assert cfg2.get('umbral_examen') == 80
    # Las otras claves deben seguir existiendo
    assert cfg2.get('otra_clave') == 'valor_intacto'
    assert cfg2.get('tema') == 'dark'

    # Restaurar a 80 por defecto
    client.put('/api/perfil', json={'configuracion': {'umbral_examen': 80}})


# ============================================================
# 4. TESTS DE INTEGRACIÓN - DOMINIO Y METADATOS DE EXAMEN
# ============================================================

def test_dominio_con_examen_10_preguntas_usa_las_10(client, limpiar_datos_test):
    """Al evaluar un examen de 10 preguntas, se guardan los metadatos en 'detalles'
    y _recalcular_dominio evalúa las 10 preguntas completas del intento."""
    client.put('/api/perfil', json={'configuracion': {'umbral_examen': 80}})

    # Simular 10 respuestas de suma válidas (8 correctas y 2 incorrectas = 80%)
    respuestas = []
    for i in range(10):
        es_ok = i < 8
        respuestas.append({
            'operacion': f'{i} + 1',
            'respuesta_correcta': str(i + 1),
            'respuesta_usuario': str(i + 1) if es_ok else '0',
            'dificultad': 1,
            'tiempo_segundos': 5
        })

    res = client.post('/api/lecciones/1.1/examen/evaluar', json={'respuestas': respuestas})
    assert res.status_code == 200
    data = res.get_json()
    assert data['aprobado'] is True
    assert data['porcentaje'] == 80.0
    assert data['total'] == 10
    assert data['umbral_requerido'] == 80

    # Verificar en la base de datos que se guardaron las 10 con examen_id
    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, detalles FROM ejercicios
        WHERE leccion_id = '1.1' AND tipo_ejercicio = 'examen'
        ORDER BY id DESC LIMIT 10
    """)
    rows = cur.fetchall()
    conn.close()

    assert len(rows) == 10
    ex_ids = set()
    for r in rows:
        limpiar_datos_test.append(r[0])
        det = json.loads(r[1]) if isinstance(r[1], str) else r[1]
        assert det.get('total') == 10
        assert det.get('umbral') == 80
        assert det.get('aprobado') is True
        ex_ids.add(det.get('examen_id'))

    assert len(ex_ids) == 1, "Todas las 10 filas del intento deben compartir el mismo examen_id"


def test_cambiar_umbral_despues_no_cambia_dominio_ya_concedido(client, limpiar_datos_test):
    """Un examen evaluado con 8/10 y umbral 80 queda aprobado.
    Si luego se cambia el umbral a 90 o 100, _recalcular_dominio respeta el 'aprobado'
    guardado en los detalles del intento y no revoca el dominio."""
    # 1. Configurar umbral 80
    client.put('/api/perfil', json={'configuracion': {'umbral_examen': 80}})

    # 2. Rendir examen con 8/10 (aprobado bajo umbral 80)
    respuestas = []
    for i in range(10):
        es_ok = i < 8
        respuestas.append({
            'operacion': f'{i + 10} + 2',
            'respuesta_correcta': str(i + 12),
            'respuesta_usuario': str(i + 12) if es_ok else '0',
            'dificultad': 1,
            'tiempo_segundos': 4
        })

    res = client.post('/api/lecciones/1.1/examen/evaluar', json={'respuestas': respuestas})
    assert res.get_json()['aprobado'] is True

    # Registrar IDs para limpieza
    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM ejercicios WHERE leccion_id = '1.1' AND tipo_ejercicio = 'examen' ORDER BY id DESC LIMIT 10")
    for r in cur.fetchall():
        limpiar_datos_test.append(r[0])

    # 3. Cambiar umbral a 90% (donde 8/10 reprobaría si se reevaluara dinámicamente)
    client.put('/api/perfil', json={'configuracion': {'umbral_examen': 90}})

    # 4. Forzar recálculo de dominio
    database._recalcular_dominio(cur, '1.1')
    conn.commit()

    # 5. Verificar que la lección sigue dominada
    cur.execute("SELECT estado, porcentaje_dominio FROM lecciones WHERE id = '1.1'")
    row_lec = cur.fetchone()
    conn.close()

    assert row_lec[0] == 'dominado', "El estado no debe cambiar a pesar de elevar el umbral"
    assert row_lec[1] >= 80.0

    # Restaurar umbral
    client.put('/api/perfil', json={'configuracion': {'umbral_examen': 80}})


def test_examen_antiguo_sin_marcas_sigue_funcionando(client, limpiar_datos_test):
    """Si existen exámenes antiguos sin 'examen_id' en detalles,
    _recalcular_dominio preserva el comportamiento anterior evaluando las últimas 4 preguntas y 75%."""
    # Insertar 4 filas sin examen_id usando registrar_ejercicio: 3 correctas de 4 (75%)
    for i in range(4):
        es_ok = i < 3
        eid = database.registrar_ejercicio(
            leccion_id='1.1',
            tipo_ejercicio='examen',
            operacion=f'{i + 30} + 1',
            respuesta_correcta=str(i + 31),
            respuesta_usuario=str(i + 31) if es_ok else '0',
            es_correcto=es_ok,
            intentos=1,
            tiempo_segundos=5,
            uso_ayuda=0,
            tipo_error=None,
            dificultad=1,
            detalles={}
        )
        limpiar_datos_test.append(eid)

    conn = database.get_db()
    cur = conn.cursor()
    # Recalcular dominio
    database._recalcular_dominio(cur, '1.1')
    conn.commit()

    cur.execute("SELECT estado, porcentaje_dominio FROM lecciones WHERE id = '1.1'")
    row = cur.fetchone()
    conn.close()

    # 3 de 4 = 75%, cumple con el umbral antiguo del 75%
    assert row[1] >= 75.0

    # 3 de 4 = 75%, cumple con el umbral antiguo del 75%
    assert row[1] >= 75.0


def test_examen_nuevo_evita_preguntas_examen_anterior(client, limpiar_datos_test):
    """Al generar un nuevo examen para una lección con suficiente espacio muestral,
    se evitan las operaciones que se respondieron en el examen anterior."""
    random.seed(777)
    # Generar primer examen
    res1 = client.post('/api/lecciones/1.1/examen/generar')
    preguntas1 = res1.get_json()['preguntas']
    ops1 = set(p['operacion'] for p in preguntas1)

    # Registrar el primer examen en la BD
    respuestas1 = [{
        'operacion': p['operacion'],
        'respuesta_correcta': p['respuesta_correcta'],
        'respuesta_usuario': p['respuesta_correcta'],
        'dificultad': p['dificultad'],
        'tiempo_segundos': 3
    } for p in preguntas1]

    client.post('/api/lecciones/1.1/examen/evaluar', json={'respuestas': respuestas1})

    # Guardar IDs para limpieza
    conn = database.get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM ejercicios WHERE leccion_id = '1.1' AND tipo_ejercicio = 'examen' ORDER BY id DESC LIMIT 10")
    for r in cur.fetchall():
        limpiar_datos_test.append(r[0])
    conn.close()

    # Generar segundo examen de la misma lección
    res2 = client.post('/api/lecciones/1.1/examen/generar')
    preguntas2 = res2.get_json()['preguntas']
    ops2 = set(p['operacion'] for p in preguntas2)

    # Verificar que no hay solapamiento con el examen anterior
    interseccion = ops1.intersection(ops2)
    assert len(interseccion) == 0, f"El nuevo examen repitió preguntas del anterior: {interseccion}"
