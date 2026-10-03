"""
Mi Profesor de Matemáticas Personal
Servidor principal Flask
"""
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

from database import init_db, obtener_perfil, actualizar_perfil, obtener_lecciones, \
    obtener_leccion, registrar_ejercicio, obtener_historial, obtener_estadisticas, \
    obtener_logros, verificar_logros, actualizar_racha, exportar_datos, importar_datos, \
    registrar_evaluacion_diagnostica, obtener_repasos_pendientes, actualizar_leccion, \
    desbloquear_lecciones_siguientes
from ejercicios import generar_ejercicio, verificar_respuesta, clasificar_error, \
    obtener_explicacion, generar_evaluacion_diagnostica, analizar_diagnostico
from teoria import obtener_teoria_leccion

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['JSON_AS_ASCII'] = False


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
    datos = request.get_json()
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
    """Generar examen corto de 4 preguntas sin pistas (estilo Khan Academy)."""
    preguntas = []
    dificultades = [1, 1, 2, 2]
    for d in dificultades:
        ej = generar_ejercicio(leccion_id, d)
        preguntas.append({
            'operacion': ej['operacion'],
            'respuesta_correcta': ej['respuesta_correcta'],
            'tipo': ej.get('tipo', 'examen'),
            'dificultad': d,
            'explicacion_previa': ej.get('explicacion_previa', '')
        })
    return jsonify({
        'leccion_id': leccion_id,
        'preguntas': preguntas,
        'total': len(preguntas)
    })


@app.route('/api/lecciones/<leccion_id>/examen/evaluar', methods=['POST'])
def api_evaluar_examen(leccion_id):
    """Evaluar respuestas del examen final de la lección."""
    datos = request.get_json()
    respuestas = datos.get('respuestas', [])
    total = len(respuestas)
    correctas = 0
    detalles = []

    for r in respuestas:
        op = r.get('operacion', '')
        rc = str(r.get('respuesta_correcta', '')).strip()
        ru = str(r.get('respuesta_usuario', '')).strip()
        t = r.get('tiempo_segundos', 0)
        d = r.get('dificultad', 1)

        es_ok = verificar_respuesta(ru, rc)
        if es_ok:
            correctas += 1

        tipo_error = None if es_ok else clasificar_error(leccion_id, op, ru, rc)

        # Registrar de forma silenciosa en la base de datos
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
            dificultad=d
        )

        detalles.append({
            'operacion': op,
            'respuesta_correcta': rc,
            'respuesta_usuario': ru,
            'es_correcto': es_ok,
            'explicacion': None if es_ok else obtener_explicacion(leccion_id, op, rc, ru)
        })

    porcentaje = (correctas / total * 100) if total > 0 else 0
    aprobado = porcentaje >= 75  # 3 de 4 preguntas mínimo

    logros_nuevos = []
    if aprobado:
        actualizar_leccion(leccion_id, porcentaje_dominio=100.0, estado='dominado')
        desbloquear_lecciones_siguientes(leccion_id)
        actualizar_racha()
        logros_nuevos = verificar_logros()

    return jsonify({
        'aprobado': aprobado,
        'porcentaje': round(porcentaje, 1),
        'correctas': correctas,
        'total': total,
        'detalles': detalles,
        'logros_nuevos': logros_nuevos,
        'mensaje': '¡Felicitaciones! Has demostrado dominio completo del tema.' if aprobado else 'Estuviste cerca. Te sugiero repasar la teoría y practicar un poco más antes de intentar el examen.'
    })


# ============================================================
# API - EJERCICIOS
# ============================================================

@app.route('/api/ejercicio/generar', methods=['POST'])
def api_generar_ejercicio():
    datos = request.get_json()
    leccion_id = datos.get('leccion_id', '1.1')
    dificultad = datos.get('dificultad', 1)

    ejercicio = generar_ejercicio(leccion_id, dificultad)
    return jsonify(ejercicio)


@app.route('/api/ejercicio/verificar', methods=['POST'])
def api_verificar_ejercicio():
    datos = request.get_json()
    respuesta_usuario = datos.get('respuesta_usuario', '')
    respuesta_correcta = datos.get('respuesta_correcta', '')
    leccion_id = datos.get('leccion_id', '1.1')
    operacion = datos.get('operacion', '')
    tipo_ejercicio = datos.get('tipo_ejercicio', '')
    tiempo_segundos = datos.get('tiempo_segundos', 0)
    intentos = datos.get('intentos', 1)
    uso_ayuda = datos.get('uso_ayuda', False)
    dificultad = datos.get('dificultad', 1)

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


@app.route('/api/repasos', methods=['GET'])
def api_repasos():
    repasos = obtener_repasos_pendientes()
    return jsonify(repasos)


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
