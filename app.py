"""
Mi Profesor de Matemáticas Personal
Servidor principal Flask
"""
import os
import json
import time
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

from database import init_db, obtener_perfil, actualizar_perfil, obtener_lecciones, \
    obtener_leccion, registrar_ejercicio, obtener_historial, obtener_estadisticas, \
    obtener_logros, verificar_logros, actualizar_racha, exportar_datos, importar_datos, \
    registrar_evaluacion_diagnostica, obtener_repasos_pendientes, actualizar_leccion, \
    desbloquear_lecciones_siguientes, programar_repaso_sm2, obtener_repasos_del_dia, \
    completar_repaso_sm2, obtener_diagnostico_pedagogico, obtener_recomendaciones_pedagogicas, \
    obtener_patrones_error, iniciar_sesion, registrar_heartbeat, cerrar_sesion, obtener_sesion_activa, \
    validar_sesion_abierta, obtener_operaciones_recientes_leccion, obtener_preguntas_ultimo_examen
from ejercicios import generar_ejercicio, generar_ejercicio_variado, verificar_respuesta, clasificar_error, \
    obtener_explicacion, generar_evaluacion_diagnostica, analizar_diagnostico
from teoria import obtener_teoria_leccion

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['JSON_AS_ASCII'] = False


def obtener_umbral_examen():
    """Obtener el umbral de aprobación configurado en perfil.configuracion (80, 90 o 100)."""
    try:
        perf = obtener_perfil()
        cfg_raw = perf.get('configuracion') or '{}'
        cfg = json.loads(cfg_raw) if isinstance(cfg_raw, str) else dict(cfg_raw)
        u = int(cfg.get('umbral_examen', 80))
        return u if u in (80, 90, 100) else 80
    except Exception:
        return 80


# ============================================================
# RUTAS DE PÁGINAS
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


# ============================================================
# API - PERFIL
# ============================================================

@app.route('/api/perfil', methods=['GET'])
def api_perfil():
    perfil = obtener_perfil()
    return jsonify(perfil)


@app.route('/api/perfil', methods=['PUT'])
def api_actualizar_perfil():
    datos = request.get_json() or {}
    if 'configuracion' in datos:
        cfg_in = datos['configuracion']
        if isinstance(cfg_in, str):
            try:
                cfg_in = json.loads(cfg_in)
            except Exception:
                cfg_in = {}
        elif not isinstance(cfg_in, dict):
            cfg_in = {}

        perf_actual = obtener_perfil()
        cfg_actual_raw = perf_actual.get('configuracion') or '{}'
        try:
            cfg_actual = json.loads(cfg_actual_raw) if isinstance(cfg_actual_raw, str) else dict(cfg_actual_raw or {})
        except Exception:
            cfg_actual = {}

        # Validar umbral_examen (solo 80, 90, 100; cualquier otro -> 80)
        if 'umbral_examen' in cfg_in:
            try:
                u = int(cfg_in['umbral_examen'])
                cfg_actual['umbral_examen'] = u if u in (80, 90, 100) else 80
            except (ValueError, TypeError):
                cfg_actual['umbral_examen'] = 80

        # Conservar otras claves existentes y añadir nuevas sin romper
        for k, v in cfg_in.items():
            if k != 'umbral_examen':
                cfg_actual[k] = v

        datos['configuracion'] = json.dumps(cfg_actual)

    actualizar_perfil(**datos)
    return jsonify({'ok': True})


# ============================================================
# API - LECCIONES
# ============================================================

@app.route('/api/lecciones', methods=['GET'])
def api_lecciones():
    nivel = request.args.get('nivel', type=int)
    lecciones = obtener_lecciones(nivel)
    return jsonify(lecciones)


@app.route('/api/lecciones/<leccion_id>', methods=['GET'])
def api_leccion(leccion_id):
    leccion = obtener_leccion(leccion_id)
    if not leccion:
        return jsonify({'error': 'Lección no encontrada'}), 404
    return jsonify(leccion)


@app.route('/api/lecciones/<leccion_id>/teoria', methods=['GET'])
def api_leccion_teoria(leccion_id):
    teoria = obtener_teoria_leccion(leccion_id)
    leccion = obtener_leccion(leccion_id)
    return jsonify({
        'leccion_id': leccion_id,
        'titulo': leccion['titulo'] if leccion else f'Lección {leccion_id}',
        'nivel': leccion['nivel'] if leccion else 1,
        'teoria': teoria
    })


@app.route('/api/lecciones/<leccion_id>/examen/generar', methods=['POST'])
def api_generar_examen(leccion_id):
    """Generar examen de dominio: 10 preguntas sin pistas, todas distintas entre sí.
    Evita preguntas del examen anterior de esa lección si es posible.
    En lecciones con espacio reducido, genera el máximo posible de distintas.
    """
    ultimas_examen = obtener_preguntas_ultimo_examen(leccion_id)
    excluir_previas = set(ultimas_examen)

    # Mezcla equilibrada: 5 de dificultad 1 y 5 de dificultad 2
    dificultades_objetivo = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
    preguntas = []
    operaciones_examen = set()

    for d in dificultades_objetivo:
        ej = None
        # Intento 1: distinta en este examen Y no en el examen anterior
        for _ in range(35):
            cand = generar_ejercicio(leccion_id, d)
            op = cand.get('operacion')
            if op and op not in operaciones_examen and op not in excluir_previas:
                ej = cand
                break

        # Intento 2 (relajando el examen anterior si la lección no tiene suficientes distintas):
        if not ej:
            for _ in range(35):
                cand = generar_ejercicio(leccion_id, d)
                op = cand.get('operacion')
                if op and op not in operaciones_examen:
                    ej = cand
                    break

        if ej:
            operaciones_examen.add(ej['operacion'])
            preguntas.append({
                'operacion': ej['operacion'],
                'respuesta_correcta': ej['respuesta_correcta'],
                'tipo': ej.get('tipo', 'examen'),
                'dificultad': d,
                'explicacion_previa': ej.get('explicacion_previa', ''),
                'pistas': []
            })
        else:
            # Si se agotaron las operaciones distintas posibles para esta lección, detener
            break

    return jsonify({
        'leccion_id': leccion_id,
        'preguntas': preguntas,
        'total': len(preguntas)
    })


@app.route('/api/lecciones/<leccion_id>/examen/evaluar', methods=['POST'])
def api_evaluar_examen(leccion_id):
    """Evaluar respuestas del examen final de la lección con umbral configurable."""
    datos = request.get_json() or {}
    respuestas = datos.get('respuestas', [])
    sesion_id = datos.get('sesion_id')
    try:
        sesion_id = int(sesion_id) if sesion_id is not None else None
    except (ValueError, TypeError):
        sesion_id = None

    # Comprueba que la sesión exista y esté abierta; si no, usa None
    if sesion_id is not None:
        sesion_id = validar_sesion_abierta(sesion_id)

    total = len(respuestas)
    correctas = 0
    detalles = []

    # Validar respuestas primero para calcular porcentaje y aprobado
    for r in respuestas:
        rc = str(r.get('respuesta_correcta', '')).strip()
        ru = str(r.get('respuesta_usuario', '')).strip()
        if verificar_respuesta(ru, rc):
            correctas += 1

    porcentaje = (correctas / total * 100) if total > 0 else 0
    umbral = obtener_umbral_examen()
    aprobado = porcentaje >= umbral

    examen_id = f"ex_{leccion_id}_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
    detalles_meta_examen = {
        'examen_id': examen_id,
        'total': total,
        'umbral': umbral,
        'aprobado': aprobado
    }

    for r in respuestas:
        op = r.get('operacion', '')
        rc = str(r.get('respuesta_correcta', '')).strip()
        ru = str(r.get('respuesta_usuario', '')).strip()
        t = r.get('tiempo_segundos', 0)
        d = r.get('dificultad', 1)

        es_ok = verificar_respuesta(ru, rc)
        tipo_error = None if es_ok else clasificar_error(leccion_id, op, ru, rc)

        # Registrar de forma silenciosa en la base de datos con metadatos del examen
        registrar_ejercicio(
            leccion_id=leccion_id,
            tipo_ejercicio='examen',
            operacion=op,
            respuesta_correcta=rc,
            respuesta_usuario=ru,
            es_correcto=es_ok,
            intentos=1,
            tiempo_segundos=t,
            uso_ayuda=0,
            tipo_error=tipo_error,
            dificultad=d,
            detalles=detalles_meta_examen,
            sesion_id=sesion_id
        )

        detalles.append({
            'operacion': op,
            'respuesta_correcta': rc,
            'respuesta_usuario': ru,
            'es_correcto': es_ok,
            'explicacion': None if es_ok else obtener_explicacion(leccion_id, op, rc, ru)
        })

    logros_nuevos = []
    if aprobado:
        actualizar_leccion(leccion_id, porcentaje_dominio=100.0, estado='dominado')
        desbloquear_lecciones_siguientes(leccion_id)
        actualizar_racha()
        programar_repaso_sm2(leccion_id)  # Programa repetición espaciada SM-2 (Día 1, 3, 7, 21)
        logros_nuevos = verificar_logros()

    return jsonify({
        'aprobado': aprobado,
        'porcentaje': round(porcentaje, 1),
        'correctas': correctas,
        'total': total,
        'umbral_requerido': umbral,
        'detalles': detalles,
        'logros_nuevos': logros_nuevos,
        'mensaje': '¡Felicitaciones! Has demostrado dominio completo del tema.' if aprobado else 'Estuviste cerca. Te sugiero repasar la teoría y practicar un poco más antes de intentar el examen.'
    })


# ============================================================
# API - EJERCICIOS
# ============================================================

@app.route('/api/ejercicio/generar', methods=['POST'])
def api_generar_ejercicio():
    datos = request.get_json() or {}
    leccion_id = datos.get('leccion_id', '1.1')
    dificultad = datos.get('dificultad', 1)
    operacion_actual = datos.get('operacion_actual')

    recientes = obtener_operaciones_recientes_leccion(leccion_id, limite=20)
    if operacion_actual and operacion_actual not in recientes:
        recientes.insert(0, operacion_actual)

    ejercicio = generar_ejercicio_variado(leccion_id, dificultad, excluir=recientes)
    return jsonify(ejercicio)


@app.route('/api/ejercicio/verificar', methods=['POST'])
def api_verificar_ejercicio():
    datos = request.get_json() or {}
    respuesta_usuario = datos.get('respuesta_usuario', '')
    respuesta_correcta = datos.get('respuesta_correcta', '')
    leccion_id = datos.get('leccion_id', '1.1')
    operacion = datos.get('operacion', '')
    tipo_ejercicio = datos.get('tipo_ejercicio', '')
    tiempo_segundos = datos.get('tiempo_segundos', 0)
    intentos = datos.get('intentos', 1)
    uso_ayuda = datos.get('uso_ayuda', False)
    dificultad = datos.get('dificultad', 1)
    sesion_id = datos.get('sesion_id')
    try:
        sesion_id = int(sesion_id) if sesion_id is not None else None
    except (ValueError, TypeError):
        sesion_id = None

    # Comprueba que la sesión exista y esté abierta; si no, usa None
    if sesion_id is not None:
        sesion_id = validar_sesion_abierta(sesion_id)

    # Verificación matemática directa
    es_correcto = verificar_respuesta(respuesta_usuario, respuesta_correcta)

    # Clasificar error si es incorrecto
    tipo_error = None
    if not es_correcto:
        tipo_error = clasificar_error(leccion_id, operacion, respuesta_usuario, respuesta_correcta)

    # Registrar en la base de datos
    ejercicio_id = registrar_ejercicio(
        leccion_id=leccion_id,
        tipo_ejercicio=tipo_ejercicio,
        operacion=operacion,
        respuesta_correcta=respuesta_correcta,
        respuesta_usuario=respuesta_usuario,
        es_correcto=es_correcto,
        intentos=intentos,
        tiempo_segundos=tiempo_segundos,
        uso_ayuda=int(uso_ayuda),
        tipo_error=tipo_error,
        dificultad=dificultad,
        sesion_id=sesion_id,
    )

    # Actualizar racha
    actualizar_racha()

    # Verificar logros
    logros_nuevos = verificar_logros()

    # Obtener explicación si es incorrecto
    explicacion = None
    if not es_correcto:
        explicacion = obtener_explicacion(leccion_id, operacion, respuesta_correcta, respuesta_usuario)

    # Obtener lección actualizada (para dominio)
    leccion = obtener_leccion(leccion_id)

    # Mensajes motivadores
    mensaje = _mensaje_motivador(es_correcto, intentos)

    return jsonify({
        'es_correcto': es_correcto,
        'respuesta_correcta': respuesta_correcta,
        'tipo_error': tipo_error,
        'explicacion': explicacion,
        'logros_nuevos': logros_nuevos,
        'mensaje': mensaje,
        'dominio_actual': leccion['porcentaje_dominio'] if leccion else 0,
    })


@app.route('/api/ejercicio/explicacion', methods=['POST'])
def api_explicacion():
    datos = request.get_json()
    leccion_id = datos.get('leccion_id', '1.1')
    operacion = datos.get('operacion', '')
    respuesta_correcta = datos.get('respuesta_correcta', '')
    respuesta_usuario = datos.get('respuesta_usuario')

    explicacion = obtener_explicacion(leccion_id, operacion, respuesta_correcta, respuesta_usuario)
    return jsonify(explicacion)


# ============================================================
# API - EVALUACIÓN DIAGNÓSTICA
# ============================================================

@app.route('/api/diagnostico/generar', methods=['GET'])
def api_generar_diagnostico():
    preguntas = generar_evaluacion_diagnostica()
    # Serializar los ejercicios
    resultado = []
    for p in preguntas:
        resultado.append({
            'nivel': p['nivel'],
            'tema': p['tema'],
            'operacion': p['ejercicio']['operacion'],
            'respuesta_correcta': p['ejercicio']['respuesta_correcta'],
            'tipo': p['ejercicio']['tipo'],
            'dificultad': p['ejercicio']['dificultad'],
        })
    return jsonify(resultado)


@app.route('/api/diagnostico/evaluar', methods=['POST'])
def api_evaluar_diagnostico():
    datos = request.get_json()
    resultados = datos.get('resultados', [])

    # Analizar resultados
    analisis = analizar_diagnostico(resultados)

    # Registrar en la base de datos
    registrar_evaluacion_diagnostica(analisis['resultados'])

    # Actualizar el nivel del perfil
    actualizar_perfil(
        nivel_actual=analisis['nivel_recomendado'],
        evaluacion_inicial_completada=1
    )

    # Desbloquear lecciones hasta el nivel recomendado
    nivel_rec = analisis['nivel_recomendado']
    lecciones = obtener_lecciones()
    for leccion in lecciones:
        if leccion['nivel'] < nivel_rec:
            actualizar_leccion(leccion['id'], estado='dominado', porcentaje_dominio=100)
        elif leccion['nivel'] == nivel_rec and leccion['orden'] == 1:
            actualizar_leccion(leccion['id'], estado='disponible')

    return jsonify(analisis)


# ============================================================
# API - HISTORIAL Y ESTADÍSTICAS
# ============================================================

@app.route('/api/historial', methods=['GET'])
def api_historial():
    leccion_id = request.args.get('leccion_id')
    limite = request.args.get('limite', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    historial = obtener_historial(leccion_id, limite, offset)
    return jsonify(historial)


@app.route('/api/estadisticas', methods=['GET'])
def api_estadisticas():
    stats = obtener_estadisticas()
    return jsonify(stats)


@app.route('/api/pedagogia/diagnostico', methods=['GET'])
def api_pedagogia_diagnostico():
    diag = obtener_diagnostico_pedagogico()
    return jsonify(diag)


@app.route('/api/pedagogia/recomendaciones', methods=['GET'])
def api_pedagogia_recomendaciones():
    recs = obtener_recomendaciones_pedagogicas()
    return jsonify(recs)


@app.route('/api/pedagogia/patrones', methods=['GET'])
def api_pedagogia_patrones():
    leccion_id = request.args.get('leccion_id')
    patrones = obtener_patrones_error(leccion_id)
    return jsonify(patrones)



@app.route('/api/repasos', methods=['GET'])
def api_repasos():
    repasos = obtener_repasos_pendientes()
    return jsonify(repasos)


@app.route('/api/repasos/hoy', methods=['GET'])
def api_repasos_hoy():
    """Obtener temas programados para repasar hoy según SM-2."""
    repasos = obtener_repasos_del_dia()
    return jsonify({
        'total': len(repasos),
        'repasos': repasos
    })


@app.route('/api/repasos/<int:repaso_id>/completar', methods=['POST'])
def api_completar_repaso(repaso_id):
    """Completar un repaso y reprogramar el siguiente intervalo SM-2."""
    datos = request.get_json() or {}
    resultado = datos.get('resultado', 100)
    ok = completar_repaso_sm2(repaso_id, resultado)
    actualizar_racha()
    return jsonify({'ok': ok})


# ============================================================
# API - SESIONES DE ESTUDIO
# ============================================================

@app.route('/api/sesion/iniciar', methods=['POST'])
def api_sesion_iniciar():
    """Inicia una sesión de estudio o retoma la abierta existente."""
    sesion_id, reanudada = iniciar_sesion()
    return jsonify({'ok': True, 'sesion_id': sesion_id, 'reanudada': reanudada})


@app.route('/api/sesion/heartbeat', methods=['POST'])
def api_sesion_heartbeat():
    """Registra actividad real en la sesión activa."""
    datos = request.get_json() or {}
    raw_sesion_id = datos.get('sesion_id')
    if raw_sesion_id is None:
        return jsonify({'ok': False, 'motivo': 'falta_sesion_id'}), 400
    try:
        sesion_id = int(raw_sesion_id)
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'motivo': 'sesion_id_invalido'}), 400
    resultado = registrar_heartbeat(sesion_id)
    return jsonify(resultado)


@app.route('/api/sesion/cerrar', methods=['POST'])
def api_sesion_cerrar():
    """Cierra la sesión activa y retorna el resumen."""
    datos = request.get_json() or {}
    raw_sesion_id = datos.get('sesion_id')
    if raw_sesion_id is None:
        return jsonify({'ok': False, 'motivo': 'falta_sesion_id'}), 400
    try:
        sesion_id = int(raw_sesion_id)
    except (ValueError, TypeError):
        return jsonify({'ok': False, 'motivo': 'sesion_id_invalido'}), 400

    motivo = datos.get('motivo', 'manual')
    if motivo not in {'manual', 'inactividad', 'cierre_pestana'}:
        motivo = 'manual'

    resultado = cerrar_sesion(sesion_id, motivo=motivo)
    return jsonify(resultado)


@app.route('/api/sesion/activa', methods=['GET'])
def api_sesion_activa():
    """Retorna la sesión abierta no vencida, o null."""
    sesion = obtener_sesion_activa()
    return jsonify(sesion)


# ============================================================
# API - LOGROS
# ============================================================

@app.route('/api/logros', methods=['GET'])
def api_logros():
    logros = obtener_logros()
    return jsonify(logros)


# ============================================================
# API - BACKUP
# ============================================================

@app.route('/api/exportar', methods=['GET'])
def api_exportar():
    datos = exportar_datos()
    return jsonify(datos)


@app.route('/api/importar', methods=['POST'])
def api_importar():
    datos = request.get_json()
    try:
        importar_datos(datos)
        return jsonify({'ok': True, 'mensaje': 'Datos importados correctamente'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400


# ============================================================
# UTILIDADES
# ============================================================

def _mensaje_motivador(es_correcto, intentos):
    """Generar un mensaje motivador según el resultado."""
    if es_correcto:
        if intentos == 1:
            mensajes = [
                '¡Excelente! Lo resolviste a la primera 💪',
                '¡Muy bien! Eso estuvo perfecto ✨',
                '¡Correcto! Vas avanzando con paso firme 🎯',
                '¡Genial! Se nota tu progreso 📈',
                '¡Bien hecho! Cada ejercicio te hace más fuerte 🌟',
            ]
        else:
            mensajes = [
                '¡Lo lograste! La perseverancia da resultados 💪',
                '¡Correcto! No importa cuántos intentos, lo importante es entenderlo ✨',
                '¡Bien! Has demostrado que puedes 🎯',
            ]
    else:
        mensajes = [
            'No te preocupes, veamos cómo se resuelve paso a paso 📖',
            'Es normal equivocarse. Así aprendemos. Veamos juntos la solución 🤝',
            'Cada error es una oportunidad de aprender. Revisemos esto 📝',
            'Tranquilo, vamos a entender este ejercicio juntos 💡',
        ]

    import random
    return random.choice(mensajes)


# ============================================================
# INICIO
# ============================================================

if __name__ == '__main__':
    # Cargar contraseña desde .env si existe
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ.setdefault(key.strip(), val.strip())

    print("Mi Profesor de Matematicas Personal")
    print("=" * 45)
    print("Inicializando base de datos...")
    init_db()
    print("[OK] Base de datos lista")
    print()
    print("Abriendo en: http://localhost:5000")
    print("   (Ctrl+C para detener)")
    print()

    app.run(host='0.0.0.0', port=5000, debug=True)
