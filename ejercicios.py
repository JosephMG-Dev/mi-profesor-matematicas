"""
Mi Profesor de Matemáticas Personal
Generador de ejercicios y motor de explicaciones paso a paso.

Todas las validaciones matemáticas se hacen con cálculo directo,
NO dependen de IA para decidir si una respuesta es correcta.
"""
import random
import math
from fractions import Fraction
import sympy as sp


# ============================================================
# GENERADOR DE EJERCICIOS POR LECCIÓN
# ============================================================

def generar_ejercicio(leccion_id, dificultad=1):
    """Generar un ejercicio según la lección y dificultad.

    Returns:
        dict con: operacion (str), respuesta_correcta, tipo, dificultad,
                  explicacion_previa (str), pistas (list)
    """
    generadores = {
        '1.1': _sumas_sencillas,
        '1.2': _restas_sencillas,
        '1.3': _sumas_con_llevadas,
        '1.4': _restas_con_prestamos,
        '1.5': _operaciones_numeros_grandes,
        '1.6': _calculo_mental,
        '1.7': _problemas_suma_resta,
        '2.1': _tablas_1_5,
        '2.2': _tablas_6_9,
        '2.3': _tablas_10_12,
        '2.4': _trucos_multiplicacion,
        '2.5': _multiplicaciones_dos_cifras,
        '2.6': _multiplicaciones_varias_cifras,
        '2.7': _problemas_multiplicacion,
        '3.1': _concepto_division,
        '3.2': _divisiones_exactas,
        '3.3': _divisiones_con_residuo,
        '3.4': _divisiones_numeros_grandes,
        '3.5': _division_decimales,
        '3.6': _problemas_division,
        '4.1': _concepto_fracciones,
        '4.2': _suma_resta_fracciones,
        '4.3': _mult_div_fracciones,
        '4.4': _fracciones_decimales,
        '4.5': _porcentajes,
        '5.1': _potencias,
        '5.2': _cuadrados_perfectos,
        '5.3': _raices_cuadradas,
        '5.4': _propiedades_potencias,
        '5.5': _logaritmos,
        '6.1': _numeros_enteros,
        '6.2': _uso_letras,
        '6.3': _expresiones_algebraicas,
        '6.4': _ecuaciones_primer_grado,
        '6.5': _despejes,
        '6.6': _factorizacion_basica,
        '6.7': _productos_notables,
        '6.8': _ecuaciones_cuadraticas,
        '6.9': _sistemas_numericos,
        '6.10': _logica_proposicional,
        '7.1': _reales_desigualdades,
        '7.2': _expresiones_racionales,
        '7.3': _matrices_operaciones,
        '7.4': _determinantes_inversa,
        '7.5': _sistemas_cramer,
        '7.6': _funciones_modelos,
        '7.7': _composicion_inversa,
        '7.8': _funciones_seccionadas,
        '7.9': _examen_parcial_ing,
        '7.10': _coordenadas_polares,
        '7.11': _limites_laterales,
        '7.12': _limites_indeterminados,
        '7.13': _continuidad,
        '7.14': _derivadas_optimizacion,
        '7.15': _examen_final_ing,
    }

    generador = generadores.get(leccion_id, _sumas_sencillas)
    return generador(dificultad)


def generar_ejercicio_variado(leccion_id, dificultad=1, excluir=None, max_intentos=40):
    """Generar un ejercicio evitando operaciones en la lista 'excluir'.
    Si la lección tiene pocas operaciones o se agotan las opciones,
    aplica backoff reduciendo progresivamente la ventana de exclusión.
    """
    if not excluir:
        return generar_ejercicio(leccion_id, dificultad)

    excluir_lista = [op for op in excluir if op]
    if not excluir_lista:
        return generar_ejercicio(leccion_id, dificultad)

    ventana = len(excluir_lista)
    intentos_por_ronda = max(5, max_intentos // 3)

    while ventana > 0:
        conjunto_excluir = set(excluir_lista[:ventana])
        for _ in range(intentos_por_ronda):
            ej = generar_ejercicio(leccion_id, dificultad)
            if ej and ej.get('operacion') not in conjunto_excluir:
                return ej
        # Backoff: reducir la ventana para garantizar que siempre haya opciones
        ventana = ventana // 2

    return generar_ejercicio(leccion_id, dificultad)


def verificar_respuesta(respuesta_usuario, respuesta_correcta, tolerancia=0.001):
    """Verificar si la respuesta del usuario es correcta.

    Usa comparación numérica directa y validación simbólica con SymPy.
    """
    if respuesta_usuario is None or respuesta_correcta is None:
        return False

    u_str = str(respuesta_usuario).strip().lower()
    c_str = str(respuesta_correcta).strip().lower()

    if u_str == c_str:
        return True

    # Normalización para respuestas booleanas / de lógica proposicional (V/F, True/False, 1/0)
    truthy = {'v', 'verdadero', 'true', '1', 't'}
    falsy = {'f', 'falso', 'false', '0'}
    if c_str in truthy and u_str in truthy:
        return True
    if c_str in falsy and u_str in falsy:
        return True

    # Quitar posibles prefijos como 'x =' o 'x='
    if '=' in u_str and '=' not in c_str:
        u_str = u_str.split('=')[-1].strip()
    if '=' in c_str and '=' not in u_str:
        c_str = c_str.split('=')[-1].strip()

    # Si es binario o hexadecimal
    try:
        if u_str.startswith('0b') or u_str.endswith('b'):
            clean_u = u_str.replace('0b', '').replace('b', '')
            if int(clean_u, 2) == int(c_str):
                return True
        if u_str.startswith('0x') or u_str.endswith('h'):
            clean_u = u_str.replace('0x', '').replace('h', '')
            if int(clean_u, 16) == int(c_str):
                return True
    except Exception:
        pass

    # Comparación de fracciones o números
    try:
        norm_u = u_str.replace(',', '.')
        norm_c = c_str.replace(',', '.')

        if '/' in norm_c and '/' in norm_u:
            frac_correcta = Fraction(norm_c)
            frac_usuario = Fraction(norm_u)
            return frac_correcta == frac_usuario

        val_usuario = float(norm_u)
        val_correcta = float(norm_c)

        if val_correcta == int(val_correcta) and '.' not in norm_u:
            if int(val_usuario) == int(val_correcta):
                return True

        if abs(val_usuario - val_correcta) < tolerancia:
            return True
    except Exception:
        pass

    # Validación simbólica avanzada con SymPy (ej: 2(x+3) == 2x+6, x^2 - 4 == (x-2)(x+2))
    try:
        expr_u_str = u_str.replace('^', '**')
        expr_c_str = c_str.replace('^', '**')

        expr_u = sp.sympify(expr_u_str)
        expr_c = sp.sympify(expr_c_str)

        if sp.simplify(expr_u - expr_c) == 0:
            return True
    except Exception:
        pass

    # Intervalos normalizados (ej: [ -2, 8 ] vs [-2,8] o (-inf, 4] vs <-inf, 4])
    norm_interval_u = u_str.replace(' ', '').replace('<', '(').replace('>', ')')
    norm_interval_c = c_str.replace(' ', '').replace('<', '(').replace('>', ')')
    if norm_interval_u == norm_interval_c:
        return True

    return False


def clasificar_error(leccion_id, operacion, respuesta_usuario, respuesta_correcta):
    """Clasificar el tipo de error cometido.

    Distingue pedagógicamente entre:
    - error_prestamo: olvido o ajuste incorrecto al pedir prestado (restas)
    - error_llevada: olvido o ajuste incorrecto de la llevada (sumas)
    - error_calculo: error aritmético menor en las cuentas
    - error_procedimiento: error estructural en el método de resolución
    - error_signo: confusión de signos positivo/negativo
    - error_posicional: error en el orden de magnitud (factor 10/100)
    - respuesta_azar: respuesta sin relación con la magnitud de la operación
    - error_formato: formato de respuesta no numérico o inválido
    """
    try:
        usuario = float(str(respuesta_usuario).replace(',', '.'))
        correcta = float(str(respuesta_correcta).replace(',', '.'))
    except (ValueError, TypeError):
        return 'error_formato'

    diff = abs(usuario - correcta)

    # Error de signo
    if abs(usuario + correcta) < 0.001 and correcta != 0:
        return 'error_signo'

    # Error posicional (factor de 10)
    if correcta != 0:
        ratio = usuario / correcta
        if ratio in (10, 0.1, 100, 0.01):
            return 'error_posicional'

    op_str = str(operacion or '')
    lid_str = str(leccion_id or '')

    # Detección específica de error con préstamos en restas (diferencia de 10, 100, 1000)
    if ('-' in op_str or lid_str in ('1.2', '1.4', '1.5')) and diff in (10, 100, 1000):
        return 'error_prestamo'

    # Detección específica de error con llevadas en sumas (diferencia de 10, 100, 1000)
    if ('+' in op_str or lid_str in ('1.1', '1.3', '1.5')) and diff in (10, 100, 1000):
        return 'error_llevada'

    # Error pequeño de cálculo
    if diff <= max(abs(correcta) * 0.1, 5):
        return 'error_calculo'

    # Error grande - posible azar o procedimiento mal
    if diff > abs(correcta) * 0.5:
        # Verificar si parece aleatorio
        if lid_str.startswith('1.') and diff > 50:
            return 'respuesta_azar'
        return 'error_procedimiento'

    return 'error_calculo'



def obtener_explicacion(leccion_id, operacion, respuesta_correcta, respuesta_usuario=None):
    """Generar explicación paso a paso de cómo resolver el ejercicio.

    Returns:
        dict con: pasos (list), consejo (str), ejemplo_similar (str)
    """
    explicadores = {
        '1.1': _explicar_suma,
        '1.2': _explicar_resta,
        '1.3': _explicar_suma_llevadas,
        '1.4': _explicar_resta_prestamos,
        '1.5': _explicar_operacion_grande,
        '1.6': _explicar_calculo_mental,
        '1.7': _explicar_problema,
        '2.1': _explicar_tablas,
        '2.2': _explicar_tablas,
        '2.3': _explicar_tablas,
        '2.5': _explicar_multiplicacion_grande,
        '2.6': _explicar_multiplicacion_grande,
        '3.2': _explicar_division,
        '3.3': _explicar_division_residuo,
        '3.4': _explicar_division,
        '3.5': _explicar_division,
    }

    explicador = explicadores.get(leccion_id, _explicar_generico)
    return explicador(operacion, respuesta_correcta, respuesta_usuario)


# ============================================================
# GENERADORES POR LECCIÓN - Nivel 1: Sumas y Restas
# ============================================================

def _sumas_sencillas(dificultad):
    if dificultad == 1:
        a, b = random.randint(1, 9), random.randint(1, 9)
    elif dificultad == 2:
        a, b = random.randint(5, 20), random.randint(1, 15)
    else:
        a, b = random.randint(10, 50), random.randint(10, 50)

    return {
        'operacion': f'{a} + {b}',
        'respuesta_correcta': str(a + b),
        'tipo': 'suma',
        'dificultad': dificultad,
        'explicacion_previa': 'Suma los dos números. Puedes contar desde el número más grande.',
        'pistas': [
            f'Empieza en {max(a, b)} y cuenta {min(a, b)} más',
            f'Piensa: ¿cuánto es {a} más {b}?',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _restas_sencillas(dificultad):
    if dificultad == 1:
        a = random.randint(2, 9)
        b = random.randint(1, a)
    elif dificultad == 2:
        a = random.randint(10, 30)
        b = random.randint(1, a)
    else:
        a = random.randint(20, 50)
        b = random.randint(1, a)

    return {
        'operacion': f'{a} - {b}',
        'respuesta_correcta': str(a - b),
        'tipo': 'resta',
        'dificultad': dificultad,
        'explicacion_previa': 'Resta: quitar una cantidad de otra. Empieza en el número grande y cuenta hacia atrás.',
        'pistas': [
            f'Empieza en {a} y cuenta {b} hacia atrás',
            f'Piensa: si tienes {a} cosas y quitas {b}, ¿cuántas quedan?',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _sumas_con_llevadas(dificultad):
    # Asegurar que hay acarreo
    if dificultad == 1:
        while True:
            a = random.randint(10, 49)
            b = random.randint(10, 49)
            if (a % 10) + (b % 10) >= 10:
                break
    elif dificultad == 2:
        while True:
            a = random.randint(50, 199)
            b = random.randint(50, 199)
            if (a % 10) + (b % 10) >= 10:
                break
    else:
        while True:
            a = random.randint(100, 999)
            b = random.randint(100, 999)
            if (a % 10) + (b % 10) >= 10:
                break

    return {
        'operacion': f'{a} + {b}',
        'respuesta_correcta': str(a + b),
        'tipo': 'suma_llevadas',
        'dificultad': dificultad,
        'explicacion_previa': 'Cuando la suma de las unidades da 10 o más, "llevamos" una decena a la siguiente columna.',
        'pistas': [
            f'Suma las unidades: {a % 10} + {b % 10} = {(a % 10) + (b % 10)}. Como es ≥ 10, escribe {((a % 10) + (b % 10)) % 10} y lleva 1.',
            'Recuerda sumar la que llevas en la siguiente columna.',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _restas_con_prestamos(dificultad):
    # Asegurar que necesita préstamo
    if dificultad == 1:
        while True:
            a = random.randint(20, 59)
            b = random.randint(10, a - 1)
            if (a % 10) < (b % 10):
                break
    elif dificultad == 2:
        while True:
            a = random.randint(100, 499)
            b = random.randint(50, a - 1)
            if (a % 10) < (b % 10):
                break
    else:
        while True:
            a = random.randint(200, 999)
            b = random.randint(100, a - 1)
            if (a % 10) < (b % 10):
                break

    return {
        'operacion': f'{a} - {b}',
        'respuesta_correcta': str(a - b),
        'tipo': 'resta_prestamos',
        'dificultad': dificultad,
        'explicacion_previa': 'Cuando la cifra de arriba es menor que la de abajo, "pedimos prestado" a la columna siguiente.',
        'pistas': [
            f'Las unidades: {a % 10} - {b % 10}. Como {a % 10} < {b % 10}, pide prestado.',
            f'Al pedir prestado, {a % 10} se convierte en {a % 10 + 10}, y la decena de arriba baja 1.',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _operaciones_numeros_grandes(dificultad):
    es_suma = random.choice([True, False])

    if dificultad == 1:
        a = random.randint(100, 999)
        b = random.randint(100, 999)
    elif dificultad == 2:
        a = random.randint(1000, 9999)
        b = random.randint(1000, 9999)
    else:
        a = random.randint(10000, 99999)
        b = random.randint(10000, 99999)

    if es_suma:
        return {
            'operacion': f'{a} + {b}',
            'respuesta_correcta': str(a + b),
            'tipo': 'suma_grande',
            'dificultad': dificultad,
            'explicacion_previa': 'Con números grandes, suma columna por columna de derecha a izquierda. No olvides las llevadas.',
            'pistas': ['Empieza por las unidades', 'Revisa cada columna con cuidado'],
            'numeros': {'a': a, 'b': b},
        }
    else:
        if b > a:
            a, b = b, a
        return {
            'operacion': f'{a} - {b}',
            'respuesta_correcta': str(a - b),
            'tipo': 'resta_grande',
            'dificultad': dificultad,
            'explicacion_previa': 'Con números grandes, resta columna por columna de derecha a izquierda. Pide prestado cuando necesites.',
            'pistas': ['Empieza por las unidades', 'Revisa si necesitas pedir prestado en cada columna'],
            'numeros': {'a': a, 'b': b},
        }


def _calculo_mental(dificultad):
    tipo = random.choice(['suma', 'resta', 'complemento'])

    if tipo == 'suma':
        if dificultad == 1:
            a = random.choice([10, 20, 30, 40, 50])
            b = random.randint(1, 9)
        elif dificultad == 2:
            a = random.randint(10, 50)
            b = random.randint(10, 50)
        else:
            a = random.randint(50, 200)
            b = random.randint(50, 200)
        return {
            'operacion': f'{a} + {b}',
            'respuesta_correcta': str(a + b),
            'tipo': 'calculo_mental',
            'dificultad': dificultad,
            'explicacion_previa': '¡Intenta resolver esto rápido, sin papel!',
            'pistas': ['Busca números redondos cerca', 'Descompón los números si te ayuda'],
            'numeros': {'a': a, 'b': b},
        }
    elif tipo == 'resta':
        if dificultad == 1:
            a = random.choice([10, 20, 30, 40, 50])
            b = random.randint(1, 9)
        else:
            a = random.randint(30, 100)
            b = random.randint(5, a // 2)
        return {
            'operacion': f'{a} - {b}',
            'respuesta_correcta': str(a - b),
            'tipo': 'calculo_mental',
            'dificultad': dificultad,
            'explicacion_previa': '¡Intenta resolver esto rápido, sin papel!',
            'pistas': ['Piensa cuánto le falta al número pequeño para llegar al grande'],
            'numeros': {'a': a, 'b': b},
        }
    else:
        # Complemento a número redondo
        meta = random.choice([10, 20, 50, 100])
        a = random.randint(1, meta - 1)
        return {
            'operacion': f'¿Cuánto le falta a {a} para llegar a {meta}?',
            'respuesta_correcta': str(meta - a),
            'tipo': 'calculo_mental',
            'dificultad': dificultad,
            'explicacion_previa': 'Piensa: ¿qué número le sumo para llegar a la meta?',
            'pistas': [f'{a} + ¿? = {meta}'],
            'numeros': {'a': a, 'meta': meta},
        }


def _problemas_suma_resta(dificultad):
    problemas = [
        {
            'template': 'En una tienda hay {a} manzanas. Llegan {b} manzanas más. ¿Cuántas manzanas hay en total?',
            'op': '+',
        },
        {
            'template': 'Tienes {a} pesos. Gastas {b} pesos. ¿Cuánto dinero te queda?',
            'op': '-',
        },
        {
            'template': 'En un salón hay {a} sillas. Se sacan {b} sillas. ¿Cuántas sillas quedan?',
            'op': '-',
        },
        {
            'template': 'Un autobús lleva {a} pasajeros. En la siguiente parada suben {b} más. ¿Cuántos pasajeros lleva ahora?',
            'op': '+',
        },
        {
            'template': 'Tienes {a} caramelos y tu amigo te da {b} más. ¿Cuántos caramelos tienes en total?',
            'op': '+',
        },
        {
            'template': 'Una biblioteca tiene {a} libros. Se prestan {b} libros. ¿Cuántos quedan?',
            'op': '-',
        },
    ]

    problema = random.choice(problemas)

    if dificultad == 1:
        a = random.randint(10, 50)
        b = random.randint(5, 30)
    elif dificultad == 2:
        a = random.randint(50, 200)
        b = random.randint(20, 100)
    else:
        a = random.randint(200, 1000)
        b = random.randint(100, 500)

    if problema['op'] == '-' and b > a:
        a, b = b, a

    texto = problema['template'].format(a=a, b=b)
    resultado = a + b if problema['op'] == '+' else a - b

    return {
        'operacion': texto,
        'respuesta_correcta': str(resultado),
        'tipo': 'problema',
        'dificultad': dificultad,
        'explicacion_previa': 'Lee el problema con calma. Identifica qué datos tienes y qué operación necesitas.',
        'pistas': [
            '¿Los datos se juntan (suma) o se quitan (resta)?',
            f'Los datos son: {a} y {b}',
        ],
        'numeros': {'a': a, 'b': b, 'operador': problema['op']},
    }


# ============================================================
# GENERADORES - Nivel 2: Multiplicaciones
# ============================================================

def _tablas_1_5(dificultad):
    tabla = random.randint(1, 5)
    multiplicando = random.randint(1, 12)
    return {
        'operacion': f'{tabla} × {multiplicando}',
        'respuesta_correcta': str(tabla * multiplicando),
        'tipo': 'tabla_multiplicar',
        'dificultad': dificultad,
        'explicacion_previa': f'La tabla del {tabla}: es sumar {tabla} varias veces.',
        'pistas': [
            f'{tabla} × {multiplicando} es lo mismo que sumar {tabla}, {multiplicando} veces',
            f'Recuerda: {tabla} × {max(1, multiplicando-1)} = {tabla * max(1, multiplicando-1)}, ahora suma {tabla} más',
        ],
        'numeros': {'tabla': tabla, 'multiplicando': multiplicando},
    }


def _tablas_6_9(dificultad):
    tabla = random.randint(6, 9)
    multiplicando = random.randint(1, 12)
    return {
        'operacion': f'{tabla} × {multiplicando}',
        'respuesta_correcta': str(tabla * multiplicando),
        'tipo': 'tabla_multiplicar',
        'dificultad': dificultad,
        'explicacion_previa': f'La tabla del {tabla}. Un truco: descompón. Por ejemplo, {tabla} = {tabla-5} + 5.',
        'pistas': [
            f'Puedes pensar: 5 × {multiplicando} = {5 * multiplicando}, más {tabla - 5} × {multiplicando} = {(tabla-5) * multiplicando}',
            f'Resultado: {5 * multiplicando} + {(tabla-5) * multiplicando} = {tabla * multiplicando}',
        ],
        'numeros': {'tabla': tabla, 'multiplicando': multiplicando},
    }


def _tablas_10_12(dificultad):
    tabla = random.randint(10, 12)
    multiplicando = random.randint(1, 12)
    return {
        'operacion': f'{tabla} × {multiplicando}',
        'respuesta_correcta': str(tabla * multiplicando),
        'tipo': 'tabla_multiplicar',
        'dificultad': dificultad,
        'explicacion_previa': f'Para la tabla del 10, agrega un 0. Para el 11, repite el dígito. Para el 12, suma la tabla del 10 más la del 2.',
        'pistas': [
            f'10 × {multiplicando} = {10 * multiplicando}' if tabla >= 10 else '',
            f'Truco: {tabla} × {multiplicando} = 10×{multiplicando} + {tabla-10}×{multiplicando} = {10*multiplicando} + {(tabla-10)*multiplicando}',
        ],
        'numeros': {'tabla': tabla, 'multiplicando': multiplicando},
    }


def _trucos_multiplicacion(dificultad):
    # Ejercicios que aplican trucos
    truco = random.choice(['doble', 'por5', 'por9', 'por11'])

    if truco == 'doble':
        a = random.randint(2, 50)
        return {
            'operacion': f'{a} × 2',
            'respuesta_correcta': str(a * 2),
            'tipo': 'truco_multiplicacion',
            'dificultad': dificultad,
            'explicacion_previa': 'Multiplicar por 2 es lo mismo que sumar el número consigo mismo.',
            'pistas': [f'{a} + {a} = ?'],
            'numeros': {'a': a},
        }
    elif truco == 'por5':
        a = random.randint(2, 30)
        return {
            'operacion': f'{a} × 5',
            'respuesta_correcta': str(a * 5),
            'tipo': 'truco_multiplicacion',
            'dificultad': dificultad,
            'explicacion_previa': 'Truco para ×5: multiplica por 10 y divide entre 2.',
            'pistas': [f'{a} × 10 = {a*10}, divide entre 2: {a*10} ÷ 2 = {a*5}'],
            'numeros': {'a': a},
        }
    elif truco == 'por9':
        a = random.randint(1, 10)
        return {
            'operacion': f'{a} × 9',
            'respuesta_correcta': str(a * 9),
            'tipo': 'truco_multiplicacion',
            'dificultad': dificultad,
            'explicacion_previa': 'Truco para ×9: multiplica por 10 y resta el número.',
            'pistas': [f'{a} × 10 = {a*10}, menos {a} = {a*10 - a}'],
            'numeros': {'a': a},
        }
    else:
        a = random.randint(1, 9)
        return {
            'operacion': f'{a} × 11',
            'respuesta_correcta': str(a * 11),
            'tipo': 'truco_multiplicacion',
            'dificultad': dificultad,
            'explicacion_previa': 'Truco para ×11 con un dígito: repite el dígito.',
            'pistas': [f'{a} × 11 = {a}{a} = {a*11}'],
            'numeros': {'a': a},
        }


def _multiplicaciones_dos_cifras(dificultad):
    if dificultad == 1:
        a = random.randint(10, 30)
        b = random.randint(2, 9)
    elif dificultad == 2:
        a = random.randint(10, 50)
        b = random.randint(10, 30)
    else:
        a = random.randint(20, 99)
        b = random.randint(10, 99)

    return {
        'operacion': f'{a} × {b}',
        'respuesta_correcta': str(a * b),
        'tipo': 'multiplicacion_grande',
        'dificultad': dificultad,
        'explicacion_previa': 'Multiplica cada cifra del segundo número por todo el primero, y luego suma los resultados.',
        'pistas': [
            f'Primero: {a} × {b % 10} = {a * (b % 10)}',
            f'Luego: {a} × {b // 10}0 = {a * (b // 10) * 10}' if b >= 10 else '',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _multiplicaciones_varias_cifras(dificultad):
    if dificultad == 1:
        a = random.randint(100, 500)
        b = random.randint(2, 9)
    elif dificultad == 2:
        a = random.randint(100, 999)
        b = random.randint(10, 50)
    else:
        a = random.randint(100, 999)
        b = random.randint(50, 999)

    return {
        'operacion': f'{a} × {b}',
        'respuesta_correcta': str(a * b),
        'tipo': 'multiplicacion_grande',
        'dificultad': dificultad,
        'explicacion_previa': 'Con números grandes: multiplica cifra por cifra del segundo número, mueve la posición, y suma todo.',
        'pistas': ['Hazlo paso a paso, cifra por cifra', 'Alinea bien los resultados parciales'],
        'numeros': {'a': a, 'b': b},
    }


def _problemas_multiplicacion(dificultad):
    problemas = [
        {'template': 'Si una caja tiene {a} galletas y compras {b} cajas, ¿cuántas galletas tienes?', 'desc': 'galletas'},
        {'template': 'Un paquete tiene {a} hojas. Si necesitas {b} paquetes, ¿cuántas hojas tendrás?', 'desc': 'hojas'},
        {'template': 'Cada fila del cine tiene {a} asientos. Si hay {b} filas, ¿cuántos asientos hay en total?', 'desc': 'asientos'},
    ]

    problema = random.choice(problemas)

    if dificultad == 1:
        a, b = random.randint(2, 10), random.randint(2, 10)
    elif dificultad == 2:
        a, b = random.randint(5, 25), random.randint(3, 12)
    else:
        a, b = random.randint(10, 50), random.randint(5, 20)

    return {
        'operacion': problema['template'].format(a=a, b=b),
        'respuesta_correcta': str(a * b),
        'tipo': 'problema',
        'dificultad': dificultad,
        'explicacion_previa': 'Cuando tienes grupos iguales, multiplica.',
        'pistas': [f'Son {b} grupos de {a}', f'{a} × {b} = ?'],
        'numeros': {'a': a, 'b': b},
    }


# ============================================================
# GENERADORES - Nivel 3: Divisiones
# ============================================================

def _concepto_division(dificultad):
    # Divisiones sencillas conceptuales
    b = random.randint(2, 5)
    resultado = random.randint(2, 10)
    a = b * resultado

    return {
        'operacion': f'Si repartes {a} caramelos entre {b} amigos por igual, ¿cuántos le tocan a cada uno?',
        'respuesta_correcta': str(resultado),
        'tipo': 'concepto_division',
        'dificultad': dificultad,
        'explicacion_previa': 'Dividir es repartir en partes iguales. ¿Cuántas veces cabe el divisor en el dividendo?',
        'pistas': [
            f'Piensa: ¿{b} × cuánto = {a}?',
            f'Reparte de uno en uno hasta que se acaben los {a}',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _divisiones_exactas(dificultad):
    if dificultad == 1:
        b = random.randint(2, 5)
        resultado = random.randint(2, 10)
    elif dificultad == 2:
        b = random.randint(2, 9)
        resultado = random.randint(5, 20)
    else:
        b = random.randint(5, 12)
        resultado = random.randint(10, 50)

    a = b * resultado

    return {
        'operacion': f'{a} ÷ {b}',
        'respuesta_correcta': str(resultado),
        'tipo': 'division_exacta',
        'dificultad': dificultad,
        'explicacion_previa': f'Busca cuántas veces cabe {b} en {a}.',
        'pistas': [
            f'Piensa: ¿{b} × cuánto = {a}?',
            f'Pista: {b} × {resultado - 1} = {b * (resultado - 1)}, ¿y si sumas {b} más?',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _divisiones_con_residuo(dificultad):
    if dificultad == 1:
        b = random.randint(2, 5)
        cociente = random.randint(2, 10)
        residuo = random.randint(1, b - 1)
    elif dificultad == 2:
        b = random.randint(3, 9)
        cociente = random.randint(5, 20)
        residuo = random.randint(1, b - 1)
    else:
        b = random.randint(5, 12)
        cociente = random.randint(10, 50)
        residuo = random.randint(1, b - 1)

    a = b * cociente + residuo

    return {
        'operacion': f'{a} ÷ {b} (escribe solo el cociente entero)',
        'respuesta_correcta': str(cociente),
        'tipo': 'division_residuo',
        'dificultad': dificultad,
        'explicacion_previa': f'Divide {a} entre {b}. Si no es exacta, el residuo es lo que sobra.',
        'pistas': [
            f'¿Cuántas veces cabe {b} en {a} sin pasarse?',
            f'{b} × {cociente} = {b * cociente}, sobran {residuo}',
        ],
        'numeros': {'a': a, 'b': b, 'residuo': residuo},
    }


def _divisiones_numeros_grandes(dificultad):
    if dificultad == 1:
        b = random.randint(2, 9)
        resultado = random.randint(10, 99)
    elif dificultad == 2:
        b = random.randint(5, 15)
        resultado = random.randint(20, 200)
    else:
        b = random.randint(10, 50)
        resultado = random.randint(50, 500)

    a = b * resultado

    return {
        'operacion': f'{a} ÷ {b}',
        'respuesta_correcta': str(resultado),
        'tipo': 'division_grande',
        'dificultad': dificultad,
        'explicacion_previa': 'Con números grandes, divide paso a paso, cifra por cifra.',
        'pistas': ['Empieza por las cifras de la izquierda', f'¿Cuántas veces cabe {b} en las primeras cifras de {a}?'],
        'numeros': {'a': a, 'b': b},
    }


def _division_decimales(dificultad):
    b = random.randint(2, 10)
    parte_entera = random.randint(1, 20)
    # Crear un decimal con 1-2 decimales
    decimal_part = random.randint(1, 9)
    resultado = parte_entera + decimal_part / 10
    a = round(b * resultado, 1)

    return {
        'operacion': f'{a} ÷ {b}',
        'respuesta_correcta': str(resultado),
        'tipo': 'division_decimal',
        'dificultad': dificultad,
        'explicacion_previa': 'Si la división no es exacta con enteros, agrega un punto decimal y sigue dividiendo.',
        'pistas': [
            f'Divide la parte entera: {int(a)} ÷ {b} = {int(a) // b} con residuo {int(a) % b}',
            'Baja el siguiente dígito después del punto decimal',
        ],
        'numeros': {'a': a, 'b': b},
    }


def _problemas_division(dificultad):
    problemas = [
        {'template': 'Tienes {a} lápices y los quieres repartir entre {b} amigos por igual. ¿Cuántos le tocan a cada uno?'},
        {'template': 'Una pizza tiene {a} rebanadas y la comparten {b} personas. ¿Cuántas rebanadas come cada una?'},
        {'template': 'Un camión debe transportar {a} cajas. Si en cada viaje lleva {b} cajas, ¿cuántos viajes necesita?'},
    ]

    problema = random.choice(problemas)
    b = random.randint(2, 8)
    resultado = random.randint(3, 15)
    a = b * resultado

    return {
        'operacion': problema['template'].format(a=a, b=b),
        'respuesta_correcta': str(resultado),
        'tipo': 'problema',
        'dificultad': dificultad,
        'explicacion_previa': 'Cuando repartes o divides en grupos iguales, usa la división.',
        'pistas': [f'Divide: {a} ÷ {b} = ?'],
        'numeros': {'a': a, 'b': b},
    }


# ============================================================
# GENERADORES - Nivel 4: Fracciones y Decimales
# ============================================================

def _concepto_fracciones(dificultad):
    denominador = random.choice([2, 3, 4, 5, 6, 8])
    numerador = random.randint(1, denominador - 1)

    return {
        'operacion': f'Si divides una pizza en {denominador} partes iguales y tomas {numerador}, ¿qué fracción de la pizza tienes? (escribe como a/b)',
        'respuesta_correcta': f'{numerador}/{denominador}',
        'tipo': 'concepto_fraccion',
        'dificultad': dificultad,
        'explicacion_previa': 'Una fracción tiene numerador (partes que tomas) y denominador (partes totales).',
        'pistas': [f'Tienes {numerador} de {denominador} partes', 'Escribe: partes tomadas / partes totales'],
        'numeros': {'numerador': numerador, 'denominador': denominador},
    }


def _suma_resta_fracciones(dificultad):
    if dificultad <= 2:
        # Mismo denominador
        den = random.choice([2, 3, 4, 5, 6, 8])
        a_num = random.randint(1, den - 1)
        b_num = random.randint(1, den - a_num)
        es_suma = random.choice([True, False])

        if es_suma:
            resultado = Fraction(a_num + b_num, den)
            op = f'{a_num}/{den} + {b_num}/{den}'
        else:
            if a_num < b_num:
                a_num, b_num = b_num, a_num
            resultado = Fraction(a_num - b_num, den)
            op = f'{a_num}/{den} - {b_num}/{den}'
    else:
        # Diferente denominador
        den1 = random.choice([2, 3, 4, 5])
        den2 = random.choice([d for d in [2, 3, 4, 5, 6] if d != den1])
        a_num = random.randint(1, den1 - 1)
        b_num = random.randint(1, den2 - 1)
        resultado = Fraction(a_num, den1) + Fraction(b_num, den2)
        op = f'{a_num}/{den1} + {b_num}/{den2}'

    return {
        'operacion': op,
        'respuesta_correcta': f'{resultado.numerator}/{resultado.denominator}' if resultado.denominator != 1 else str(resultado.numerator),
        'tipo': 'fraccion_operacion',
        'dificultad': dificultad,
        'explicacion_previa': 'Para sumar o restar fracciones con el mismo denominador, opera solo los numeradores. Si son distintos, busca un denominador común.',
        'pistas': ['¿Los denominadores son iguales?', 'Si son distintos, multiplica cruzado para encontrar el denominador común'],
        'numeros': {},
    }


def _mult_div_fracciones(dificultad):
    es_mult = random.choice([True, False])
    a_num = random.randint(1, 5)
    a_den = random.randint(2, 6)
    b_num = random.randint(1, 5)
    b_den = random.randint(2, 6)

    if es_mult:
        resultado = Fraction(a_num, a_den) * Fraction(b_num, b_den)
        op = f'{a_num}/{a_den} × {b_num}/{b_den}'
        explicacion = 'Para multiplicar fracciones: multiplica numerador × numerador y denominador × denominador.'
    else:
        resultado = Fraction(a_num, a_den) / Fraction(b_num, b_den)
        op = f'{a_num}/{a_den} ÷ {b_num}/{b_den}'
        explicacion = 'Para dividir fracciones: multiplica por el inverso de la segunda fracción.'

    return {
        'operacion': op,
        'respuesta_correcta': f'{resultado.numerator}/{resultado.denominator}' if resultado.denominator != 1 else str(resultado.numerator),
        'tipo': 'fraccion_operacion',
        'dificultad': dificultad,
        'explicacion_previa': explicacion,
        'pistas': [],
        'numeros': {},
    }


def _fracciones_decimales(dificultad):
    fracciones_comunes = [
        (1, 2, 0.5), (1, 4, 0.25), (3, 4, 0.75), (1, 5, 0.2),
        (2, 5, 0.4), (3, 5, 0.6), (1, 8, 0.125), (3, 8, 0.375),
    ]

    frac = random.choice(fracciones_comunes)
    direccion = random.choice(['a_decimal', 'a_fraccion'])

    if direccion == 'a_decimal':
        return {
            'operacion': f'Convierte {frac[0]}/{frac[1]} a decimal',
            'respuesta_correcta': str(frac[2]),
            'tipo': 'conversion',
            'dificultad': dificultad,
            'explicacion_previa': 'Para convertir una fracción a decimal, divide el numerador entre el denominador.',
            'pistas': [f'{frac[0]} ÷ {frac[1]} = ?'],
            'numeros': {},
        }
    else:
        return {
            'operacion': f'Convierte {frac[2]} a fracción (simplificada)',
            'respuesta_correcta': f'{frac[0]}/{frac[1]}',
            'tipo': 'conversion',
            'dificultad': dificultad,
            'explicacion_previa': 'Para convertir un decimal a fracción, escribe el decimal sobre la potencia de 10 correspondiente y simplifica.',
            'pistas': [f'¿Qué fracción equivale a {frac[2]}?'],
            'numeros': {},
        }


def _porcentajes(dificultad):
    porcentaje = random.choice([10, 20, 25, 50, 75, 15, 30, 5])

    if dificultad == 1:
        base = random.choice([100, 200, 50, 80])
    elif dificultad == 2:
        base = random.randint(50, 500)
    else:
        base = random.randint(100, 2000)

    resultado = base * porcentaje / 100

    return {
        'operacion': f'¿Cuánto es el {porcentaje}% de {base}?',
        'respuesta_correcta': str(resultado),
        'tipo': 'porcentaje',
        'dificultad': dificultad,
        'explicacion_previa': f'El porcentaje es "de cada 100". El {porcentaje}% significa {porcentaje} de cada 100.',
        'pistas': [
            f'Multiplica: {base} × {porcentaje}/100',
            f'O equivalente: {base} × {porcentaje/100}',
        ],
        'numeros': {'base': base, 'porcentaje': porcentaje},
    }


# ============================================================
# GENERADORES - Nivel 5: Potencias y Raíces
# ============================================================

def _potencias(dificultad):
    if dificultad == 1:
        base = random.randint(1, 5)
        exp = 2
    elif dificultad == 2:
        base = random.randint(2, 10)
        exp = random.choice([2, 3])
    else:
        base = random.randint(2, 12)
        exp = random.choice([2, 3, 4])

    resultado = base ** exp

    return {
        'operacion': f'{base}^{exp} (es decir, {base} elevado a la {exp})',
        'respuesta_correcta': str(resultado),
        'tipo': 'potencia',
        'dificultad': dificultad,
        'explicacion_previa': f'{base}^{exp} significa multiplicar {base} por sí mismo {exp} veces.',
        'pistas': [
            ' × '.join([str(base)] * exp) + ' = ?',
        ],
        'numeros': {'base': base, 'exponente': exp},
    }


def _cuadrados_perfectos(dificultad):
    n = random.randint(1, 15 if dificultad <= 2 else 25)
    cuadrado = n * n
    pregunta = random.choice(['calcular', 'identificar'])

    if pregunta == 'calcular':
        return {
            'operacion': f'¿Cuánto es {n}²?',
            'respuesta_correcta': str(cuadrado),
            'tipo': 'cuadrado_perfecto',
            'dificultad': dificultad,
            'explicacion_previa': f'{n}² significa {n} × {n}.',
            'pistas': [f'{n} × {n} = ?'],
            'numeros': {'n': n},
        }
    else:
        return {
            'operacion': f'¿Es {cuadrado} un cuadrado perfecto? Si es así, ¿de qué número? (escribe el número o 0 si no es)',
            'respuesta_correcta': str(n),
            'tipo': 'cuadrado_perfecto',
            'dificultad': dificultad,
            'explicacion_previa': 'Un cuadrado perfecto es un número que resulta de multiplicar un entero por sí mismo.',
            'pistas': [f'¿Existe un número que multiplicado por sí mismo dé {cuadrado}?'],
            'numeros': {'n': n, 'cuadrado': cuadrado},
        }


def _raices_cuadradas(dificultad):
    if dificultad == 1:
        n = random.randint(1, 10)
    elif dificultad == 2:
        n = random.randint(1, 15)
    else:
        n = random.randint(1, 25)

    cuadrado = n * n

    return {
        'operacion': f'√{cuadrado} = ?',
        'respuesta_correcta': str(n),
        'tipo': 'raiz_cuadrada',
        'dificultad': dificultad,
        'explicacion_previa': f'La raíz cuadrada de {cuadrado} es el número que multiplicado por sí mismo da {cuadrado}.',
        'pistas': [f'¿Qué número × sí mismo = {cuadrado}?', f'Prueba con {n-1}: {(n-1)*(n-1)} y con {n+1}: {(n+1)*(n+1)}'],
        'numeros': {'cuadrado': cuadrado, 'raiz': n},
    }


def _propiedades_potencias(dificultad):
    prop = random.choice(['producto', 'cociente', 'potencia_potencia'])

    base = random.randint(2, 5)

    if prop == 'producto':
        exp1 = random.randint(1, 3)
        exp2 = random.randint(1, 3)
        return {
            'operacion': f'{base}^{exp1} × {base}^{exp2} = {base}^? (¿cuál es el exponente?)',
            'respuesta_correcta': str(exp1 + exp2),
            'tipo': 'propiedad_potencia',
            'dificultad': dificultad,
            'explicacion_previa': 'Cuando multiplicas potencias con la misma base, sumas los exponentes.',
            'pistas': [f'a^m × a^n = a^(m+n)', f'{exp1} + {exp2} = ?'],
            'numeros': {},
        }
    elif prop == 'cociente':
        exp1 = random.randint(3, 6)
        exp2 = random.randint(1, exp1 - 1)
        return {
            'operacion': f'{base}^{exp1} ÷ {base}^{exp2} = {base}^? (¿cuál es el exponente?)',
            'respuesta_correcta': str(exp1 - exp2),
            'tipo': 'propiedad_potencia',
            'dificultad': dificultad,
            'explicacion_previa': 'Cuando divides potencias con la misma base, restas los exponentes.',
            'pistas': [f'a^m ÷ a^n = a^(m-n)', f'{exp1} - {exp2} = ?'],
            'numeros': {},
        }
    else:
        exp1 = random.randint(2, 3)
        exp2 = random.randint(2, 3)
        return {
            'operacion': f'({base}^{exp1})^{exp2} = {base}^? (¿cuál es el exponente?)',
            'respuesta_correcta': str(exp1 * exp2),
            'tipo': 'propiedad_potencia',
            'dificultad': dificultad,
            'explicacion_previa': 'Cuando elevas una potencia a otra potencia, multiplicas los exponentes.',
            'pistas': [f'(a^m)^n = a^(m×n)', f'{exp1} × {exp2} = ?'],
            'numeros': {},
        }


def _logaritmos(dificultad):
    if dificultad == 1:
        base = random.choice([2, 10])
        exp = random.randint(1, 4) if base == 2 else random.randint(1, 3)
    elif dificultad == 2:
        base = random.choice([2, 3, 5])
        exp = random.randint(2, 5) if base == 2 else random.randint(2, 3)
    else:
        base = random.choice([2, 3, 4, 10])
        exp = random.randint(2, 6) if base == 2 else random.randint(2, 4)

    val = base ** exp

    return {
        'operacion': f'Calcula el logaritmo: log_{base}({val}) = ?',
        'respuesta_correcta': str(exp),
        'tipo': 'logaritmo',
        'dificultad': dificultad,
        'explicacion_previa': 'El logaritmo busca el exponente al que debes elevar la base para obtener el número.',
        'pistas': [
            f'Pregúntate: ¿{base} elevado a qué potencia es igual a {val}?',
            f'{base}^? = {val}',
            f'{base}^{exp} = {val}, por lo tanto el resultado es {exp}',
        ],
        'numeros': {'base': base, 'val': val, 'exp': exp},
    }


# ============================================================
# GENERADORES - Nivel 6: Álgebra y Computación
# ============================================================

def _numeros_enteros(dificultad):
    op = random.choice(['suma', 'resta', 'mult'])

    if op == 'suma':
        a = random.randint(-20, 20)
        b = random.randint(-20, 20)
        return {
            'operacion': f'({a}) + ({b})',
            'respuesta_correcta': str(a + b),
            'tipo': 'enteros',
            'dificultad': dificultad,
            'explicacion_previa': 'Con signos iguales: suma y mantén el signo. Con signos distintos: resta y quédate con el signo del mayor.',
            'pistas': [],
            'numeros': {'a': a, 'b': b},
        }
    elif op == 'resta':
        a = random.randint(-20, 20)
        b = random.randint(-20, 20)
        return {
            'operacion': f'({a}) - ({b})',
            'respuesta_correcta': str(a - b),
            'tipo': 'enteros',
            'dificultad': dificultad,
            'explicacion_previa': 'Restar un número es lo mismo que sumar su opuesto. ej: 5 - (-3) = 5 + 3.',
            'pistas': [f'Convierte: ({a}) - ({b}) = ({a}) + ({-b})'],
            'numeros': {'a': a, 'b': b},
        }
    else:
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        return {
            'operacion': f'({a}) × ({b})',
            'respuesta_correcta': str(a * b),
            'tipo': 'enteros',
            'dificultad': dificultad,
            'explicacion_previa': 'Signos iguales → resultado positivo. Signos distintos → resultado negativo.',
            'pistas': [f'Multiplica valores: {abs(a)} × {abs(b)} = {abs(a*b)}, luego pon el signo'],
            'numeros': {'a': a, 'b': b},
        }


def _uso_letras(dificultad):
    a = random.randint(2, 10)
    b = random.randint(1, 10)
    x = random.randint(1, 10)

    return {
        'operacion': f'Si x = {x}, ¿cuánto vale {a}x + {b}?',
        'respuesta_correcta': str(a * x + b),
        'tipo': 'evaluacion',
        'dificultad': dificultad,
        'explicacion_previa': 'Cuando ves "3x" significa "3 multiplicado por x". Reemplaza la x por su valor y calcula.',
        'pistas': [f'Reemplaza: {a}×{x} + {b}', f'{a * x} + {b} = ?'],
        'numeros': {'a': a, 'b': b, 'x': x},
    }


def _expresiones_algebraicas(dificultad):
    # Simplificar expresiones
    a = random.randint(1, 8)
    b = random.randint(1, 8)
    c = random.randint(1, 5)
    d = random.randint(1, 5)

    return {
        'operacion': f'Simplifica: {a}x + {c} + {b}x + {d} (escribe como ax + b)',
        'respuesta_correcta': f'{a+b}x + {c+d}',
        'tipo': 'simplificacion',
        'dificultad': dificultad,
        'explicacion_previa': 'Agrupa los términos semejantes: los que tienen x juntos, y los números juntos.',
        'pistas': [f'Términos con x: {a}x + {b}x = {a+b}x', f'Números: {c} + {d} = {c+d}'],
        'numeros': {},
    }


def _ecuaciones_primer_grado(dificultad):
    # Generar ecuación ax + b = c
    x = random.randint(1, 15)

    if dificultad == 1:
        a = random.randint(1, 5)
        b = random.randint(1, 10)
    elif dificultad == 2:
        a = random.randint(2, 8)
        b = random.randint(-10, 10)
    else:
        a = random.randint(2, 12)
        b = random.randint(-20, 20)

    c = a * x + b

    if b >= 0:
        op = f'{a}x + {b} = {c}'
    else:
        op = f'{a}x - {abs(b)} = {c}'

    return {
        'operacion': f'Resuelve: {op} (encuentra x)',
        'respuesta_correcta': str(x),
        'tipo': 'ecuacion',
        'dificultad': dificultad,
        'explicacion_previa': 'Para resolver: pasa los números al otro lado cambiando de signo, luego divide.',
        'pistas': [
            f'Paso 1: pasa {b} al otro lado: {a}x = {c} - {b} = {c - b}' if b >= 0
            else f'Paso 1: pasa {b} al otro lado: {a}x = {c} + {abs(b)} = {c - b}',
            f'Paso 2: divide ambos lados entre {a}: x = {c - b} ÷ {a} = {x}',
        ],
        'numeros': {'a': a, 'b': b, 'c': c, 'x': x},
    }


def _despejes(dificultad):
    formulas = [
        {'formula': 'A = b × h', 'despejar': 'h', 'expresion': 'A/b', 'desc': 'Área del rectángulo'},
        {'formula': 'v = d / t', 'despejar': 't', 'expresion': 'd/v', 'desc': 'Velocidad'},
        {'formula': 'P = 2a + 2b', 'despejar': 'a', 'expresion': '(P - 2b) / 2', 'desc': 'Perímetro rectángulo'},
    ]

    f = random.choice(formulas)
    vals = {'A': random.randint(10, 100), 'b': random.randint(2, 10),
            'h': random.randint(2, 10), 'v': random.randint(10, 60),
            'd': random.randint(50, 500), 't': random.randint(1, 10),
            'P': random.randint(20, 80), 'a': random.randint(2, 15)}

    return {
        'operacion': f'{f["desc"]}: {f["formula"]}. Despeja {f["despejar"]}.',
        'respuesta_correcta': f['expresion'],
        'tipo': 'despeje',
        'dificultad': dificultad,
        'explicacion_previa': 'Para despejar: pasa todo lo que no sea la variable al otro lado de la ecuación.',
        'pistas': [f'Empieza con: {f["formula"]}', f'Aísla {f["despejar"]}'],
        'numeros': {},
    }


def _factorizacion_basica(dificultad):
    # Factor común
    factor = random.randint(2, 6)
    a = random.randint(1, 8)
    b = random.randint(1, 8)

    return {
        'operacion': f'Saca factor común: {factor * a}x + {factor * b} (escribe como a(bx + c))',
        'respuesta_correcta': f'{factor}({a}x + {b})',
        'tipo': 'factorizacion',
        'dificultad': dificultad,
        'explicacion_previa': 'Busca el número más grande que divida a todos los términos.',
        'pistas': [
            f'¿Qué número divide a {factor * a} y a {factor * b}?',
            f'El factor común es {factor}',
        ],
        'numeros': {},
    }


# ============================================================
# GENERADORES - Nivel 6: Álgebra Avanzada y Computación
# ============================================================

def _productos_notables(dificultad):
    b = random.randint(2, 6)
    tipo = random.choice(['cuadrado_suma', 'cuadrado_resta', 'diferencia_cuadrados'])

    if tipo == 'cuadrado_suma':
        return {
            'operacion': f'Desarrolla el producto notable: (x + {b})²',
            'respuesta_correcta': f'x^2 + {2*b}x + {b*b}',
            'tipo': 'producto_notable',
            'dificultad': dificultad,
            'explicacion_previa': '(a + b)² = a² + 2ab + b². Recuerda el doble producto central.',
            'pistas': [f'Cuadrado del primero: x²', f'Doble producto: 2 · x · {b} = {2*b}x', f'Cuadrado del segundo: {b}² = {b*b}'],
            'numeros': {'b': b},
        }
    elif tipo == 'cuadrado_resta':
        return {
            'operacion': f'Desarrolla el producto notable: (x - {b})²',
            'respuesta_correcta': f'x^2 - {2*b}x + {b*b}',
            'tipo': 'producto_notable',
            'dificultad': dificultad,
            'explicacion_previa': '(a - b)² = a² - 2ab + b².',
            'pistas': [f'Cuadrado del primero: x²', f'Doble producto con signo negativo: -{2*b}x', f'Cuadrado del segundo: (-{b})² = {b*b}'],
            'numeros': {'b': b},
        }
    else:
        return {
            'operacion': f'Desarrolla: (x + {b})(x - {b})',
            'respuesta_correcta': f'x^2 - {b*b}',
            'tipo': 'producto_notable',
            'dificultad': dificultad,
            'explicacion_previa': '(a + b)(a - b) = a² - b² (Diferencia de cuadrados).',
            'pistas': [f'x² - ({b})² = x² - {b*b}'],
            'numeros': {'b': b},
        }


def _ecuaciones_cuadraticas(dificultad):
    r1 = random.randint(1, 5)
    r2 = random.randint(r1 + 1, 8)
    c = r1 * r2

    eq = f'x² - {r1 + r2}x + {c} = 0'
    return {
        'operacion': f'Resuelve la ecuación cuadrática: {eq}. Escribe la raíz menor (un solo número entero):',
        'respuesta_correcta': str(r1),
        'tipo': 'ecuacion_cuadratica',
        'dificultad': dificultad,
        'explicacion_previa': 'Busca dos números que multiplicados den el término independiente y sumados den el coeficiente central.',
        'pistas': [f'Busca dos números que multipliquen {c} y sumen -{r1 + r2}', f'Factores: (x - {r1})(x - {r2}) = 0', f'Las raíces son x = {r1} y x = {r2}'],
        'numeros': {'r1': r1, 'r2': r2},
    }


def _sistemas_numericos(dificultad):
    modo = random.choice(['bin_a_dec', 'dec_a_bin', 'hex_a_dec'])
    if modo == 'bin_a_dec':
        n = random.randint(5, 30)
        b_str = bin(n)[2:]
        return {
            'operacion': f'Convierte el número binario {b_str} (base 2) a sistema decimal:',
            'respuesta_correcta': str(n),
            'tipo': 'sistema_numerico',
            'dificultad': dificultad,
            'explicacion_previa': 'Multiplica cada bit por su potencia de 2 de derecha a izquierda (1, 2, 4, 8, 16, 32...).',
            'pistas': [f'Potencias activas en los 1s', f'Suma las potencias de base 2 para obtener {n}'],
            'numeros': {'n': n},
        }
    elif modo == 'dec_a_bin':
        n = random.randint(5, 25)
        b_str = bin(n)[2:]
        return {
            'operacion': f'Convierte el número decimal {n} a sistema binario (unos y ceros):',
            'respuesta_correcta': b_str,
            'tipo': 'sistema_numerico',
            'dificultad': dificultad,
            'explicacion_previa': 'Divide sucesivamente entre 2 y anota los residuos de abajo hacia arriba.',
            'pistas': [f'La mayor potencia de 2 menor o igual a {n} es {2**(n.bit_length()-1)}', f'En binario tiene {n.bit_length()} bits: {b_str}'],
            'numeros': {'n': n},
        }
    else:
        n = random.randint(10, 45)
        h_str = hex(n)[2:].upper()
        return {
            'operacion': f'Convierte el número hexadecimal 0x{h_str} a decimal (A=10, B=11, C=12, D=13, E=14, F=15):',
            'respuesta_correcta': str(n),
            'tipo': 'sistema_numerico',
            'dificultad': dificultad,
            'explicacion_previa': 'En hexadecimal la base es 16: dígito_izq × 16 + dígito_der × 1.',
            'pistas': [f'0x{h_str} = {n}'],
            'numeros': {'n': n},
        }


def _logica_proposicional(dificultad):
    """Generador de ejercicios de Lógica Proposicional y Álgebra de Boole."""
    tipos = ['tablas_verdad', 'implicacion', 'programacion_condicional', 'de_morgan']
    if dificultad == 1:
        tipo = random.choice(['tablas_verdad', 'programacion_condicional'])
    elif dificultad == 2:
        tipo = random.choice(['tablas_verdad', 'implicacion', 'programacion_condicional'])
    else:
        tipo = random.choice(tipos)

    if tipo == 'tablas_verdad':
        op = random.choice(['AND', 'OR', 'XOR', 'NOT_AND'])
        p = random.choice([True, False])
        q = random.choice([True, False])
        p_str = 'V' if p else 'F'
        q_str = 'V' if q else 'F'

        if op == 'AND':
            res = p and q
            texto = f'Dadas las proposiciones p = {p_str} y q = {q_str}, calcula el valor de verdad de (p ∧ q) [p AND q]: (responde V o F)'
            pista = 'La conjunción (AND) solo es Verdadera (V) cuando AMBAS proposiciones son verdaderas.'
        elif op == 'OR':
            res = p or q
            texto = f'Dadas las proposiciones p = {p_str} y q = {q_str}, calcula el valor de verdad de (p ∨ q) [p OR q]: (responde V o F)'
            pista = 'La disyunción (OR) es Verdadera (V) si al menos UNA de las proposiciones es verdadera.'
        elif op == 'XOR':
            res = p != q
            texto = f'Dadas las proposiciones p = {p_str} y q = {q_str}, calcula el valor de verdad de la disyunción exclusiva (p ⊕ q) [p XOR q]: (responde V o F)'
            pista = 'El XOR solo es Verdadero (V) cuando las dos proposiciones tienen valores DISTINTOS.'
        else:
            res = not (p and q)
            texto = f'Dadas p = {p_str} y q = {q_str}, calcula ¬(p ∧ q) [NOT(p AND q)]: (responde V o F)'
            pista = f'Primero evalúa (p ∧ q) = {"V" if (p and q) else "F"}, y luego niégalo (invierte su valor).'

        res_str = 'V' if res else 'F'
        return {
            'operacion': texto,
            'respuesta_correcta': res_str,
            'tipo': 'logica_proposicional',
            'dificultad': dificultad,
            'explicacion_previa': 'Evalúa los valores de verdad paso a paso usando las tablas de verdad fundamentales.',
            'pistas': [pista, f'Resultado final: {res_str}'],
            'numeros': {'p': p_str, 'q': q_str},
        }

    elif tipo == 'implicacion':
        p = random.choice([True, False])
        q = random.choice([True, False])
        p_str = 'V' if p else 'F'
        q_str = 'V' if q else 'F'
        res = (not p) or q
        res_str = 'V' if res else 'F'
        return {
            'operacion': f'En lógica proposicional, evalúa el valor de verdad de la condicional (p → q) [si p entonces q] cuando p = {p_str} y q = {q_str}: (responde V o F)',
            'respuesta_correcta': res_str,
            'tipo': 'logica_proposicional',
            'dificultad': dificultad,
            'explicacion_previa': 'La implicación (p → q) solo es FALSA cuando una premisa Verdadera lleva a una conclusión Falsa (V → F = F). En cualquier otro caso es Verdadera.',
            'pistas': [
                'Recuerda la regla de oro: V → F es Falso. Cualquier otro caso (V → V, F → V, F → F) es Verdadero.',
                f'Aquí tenemos: {p_str} → {q_str} = {res_str}',
            ],
            'numeros': {'p': p_str, 'q': q_str},
        }

    elif tipo == 'programacion_condicional':
        x = random.randint(1, 20)
        corte1 = random.randint(5, 12)
        corte2 = random.randint(13, 18)
        cond = random.choice(['and', 'or', 'not'])

        if cond == 'and':
            res = (x > corte1) and (x < corte2)
            op_text = f'En un programa, se evalúa: if (x > {corte1} and x < {corte2}) con x = {x}. ¿Se ejecutará el bloque if? (responde V o F)'
            pista = f'Evalúa cada condición: ({x} > {corte1}) es {"V" if x > corte1 else "F"} y ({x} < {corte2}) es {"V" if x < corte2 else "F"}.'
        elif cond == 'or':
            res = (x < corte1) or (x > corte2)
            op_text = f'En un programa, se evalúa: if (x < {corte1} or x > {corte2}) con x = {x}. ¿Se ejecutará el bloque if? (responde V o F)'
            pista = f'Como es OR, basta con que una se cumpla: ({x} < {corte1}) = {"V" if x < corte1 else "F"}, ({x} > {corte2}) = {"V" if x > corte2 else "F"}.'
        else:
            res = not (x == corte1)
            op_text = f'En un programa con x = {x}, se evalúa: if not (x == {corte1}). ¿El resultado de la condición es Verdadero (V) o Falso (F)?'
            pista = f'¿Es {x} == {corte1}? {"V" if x == corte1 else "F"}. Al aplicar NOT, se invierte.'

        res_str = 'V' if res else 'F'
        return {
            'operacion': op_text,
            'respuesta_correcta': res_str,
            'tipo': 'logica_booleana',
            'dificultad': dificultad,
            'explicacion_previa': 'En programación (if/else), las condiciones compuestas se resuelven con álgebra de Boole idéntica a la lógica matemática.',
            'pistas': [pista, f'La condición evalúa a: {res_str}'],
            'numeros': {'x': x},
        }

    else:
        a = random.choice([True, False])
        b = random.choice([True, False])
        a_str = 'V' if a else 'F'
        b_str = 'V' if b else 'F'
        res = not (a or b)
        res_str = 'V' if res else 'F'
        return {
            'operacion': f'Aplicando las Leyes de De Morgan, simplifica y evalúa ¬(A ∨ B) [NOT(A OR B)] con A = {a_str} y B = {b_str}: (responde V o F)',
            'respuesta_correcta': res_str,
            'tipo': 'de_morgan',
            'dificultad': dificultad,
            'explicacion_previa': 'Ley de De Morgan: ¬(A ∨ B) ≡ (¬A ∧ ¬B). El NOT exterior entra negando a cada uno y cambia el OR (∨) por AND (∧).',
            'pistas': [
                f'A ∨ B = {a_str} ∨ {b_str} = {"V" if (a or b) else "F"}',
                f'Negando el resultado: ¬({"V" if (a or b) else "F"}) = {res_str}',
            ],
            'numeros': {'A': a_str, 'B': b_str},
        }


# ============================================================
# GENERADORES - Nivel 7: Matemática para la Ingeniería (Sílabo Oficial 2026-2)
# ============================================================

def _reales_desigualdades(dificultad):
    c = random.randint(1, 5)
    r = random.randint(2, 6)
    return {
        'operacion': f'Resuelve la desigualdad con valor absoluto: |x - {c}| <= {r}. ¿Cuál es el valor máximo posible de x?',
        'respuesta_correcta': str(c + r),
        'tipo': 'desigualdad',
        'dificultad': dificultad,
        'explicacion_previa': '|x - c| <= r se descompone en: -r <= x - c <= r.',
        'pistas': [f'-{r} <= x - {c} <= {r}', f'Suma {c} en toda la desigualdad: {c - r} <= x <= {c + r}'],
        'numeros': {'c': c, 'r': r},
    }


def _expresiones_racionales(dificultad):
    a = random.randint(2, 7)
    return {
        'operacion': f'Simplifica la fracción algebraica: (x² - {a*a}) / (x - {a})',
        'respuesta_correcta': f'x + {a}',
        'tipo': 'expresion_racional',
        'dificultad': dificultad,
        'explicacion_previa': 'Factoriza el numerador por diferencia de cuadrados y cancela el factor común.',
        'pistas': [f'x² - {a*a} = (x - {a})(x + {a})', f'Cancela (x - {a}) con el denominador'],
        'numeros': {'a': a},
    }


def _matrices_operaciones(dificultad):
    a11, a12 = random.randint(1, 4), random.randint(0, 3)
    a21, a22 = random.randint(0, 3), random.randint(1, 4)
    b11, b12 = random.randint(1, 3), random.randint(0, 2)
    b21, b22 = random.randint(0, 2), random.randint(1, 3)

    c11 = a11 * b11 + a12 * b21

    return {
        'operacion': f'Dadas las matrices A = [[{a11}, {a12}], [{a21}, {a22}]] y B = [[{b11}, {b12}], [{b21}, {b22}]], calcula el elemento C_11 (fila 1, columna 1) de C = A × B:',
        'respuesta_correcta': str(c11),
        'tipo': 'matriz_producto',
        'dificultad': dificultad,
        'explicacion_previa': 'El elemento C_11 es el producto punto de la Fila 1 de A por la Columna 1 de B: (a11 × b11) + (a12 × b21).',
        'pistas': [
            f'Fila 1 de A: [{a11}, {a12}]',
            f'Columna 1 de B: [{b11}, {b21}]',
            f'({a11} × {b11}) + ({a12} × {b21}) = {a11*b11} + {a12*b21} = {c11}',
        ],
        'numeros': {'c11': c11},
    }


def _determinantes_inversa(dificultad):
    a = random.randint(2, 6)
    b = random.randint(1, 4)
    c = random.randint(1, 4)
    d = random.randint(2, 6)
    det = a * d - b * c

    return {
        'operacion': f'Calcula el determinante de la matriz A = [[{a}, {b}], [{c}, {d}]]:',
        'respuesta_correcta': str(det),
        'tipo': 'determinante',
        'dificultad': dificultad,
        'explicacion_previa': 'det(A) = ad - bc (diagonal principal menos diagonal secundaria).',
        'pistas': [f'Diagonal principal: {a} × {d} = {a * d}', f'Diagonal secundaria: {b} × {c} = {b * c}', f'{a * d} - {b * c} = {det}'],
        'numeros': {'det': det},
    }


def _sistemas_cramer(dificultad):
    x = random.randint(1, 6)
    y = random.randint(1, 6)
    a1, b1 = random.randint(1, 3), random.randint(1, 3)
    a2, b2 = random.randint(1, 3), -random.randint(1, 3)

    while a1 * b2 == a2 * b1:
        b2 = -random.randint(1, 4)

    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y

    return {
        'operacion': f'Resuelve por Cramer: {a1}x + {b1}y = {c1}  y  {a2}x - {abs(b2)}y = {c2}. ¿Cuánto vale x?',
        'respuesta_correcta': str(x),
        'tipo': 'sistema_cramer',
        'dificultad': dificultad,
        'explicacion_previa': 'Por la Regla de Cramer: x = det(Ax) / det(A).',
        'pistas': [
            f'det(A) = ({a1})({b2}) - ({b1})({a2}) = {a1*b2 - b1*a2}',
            f'det(Ax) = ({c1})({b2}) - ({b1})({c2}) = {c1*b2 - b1*c2}',
            f'x = {c1*b2 - b1*c2} / {a1*b2 - b1*a2} = {x}',
        ],
        'numeros': {'x': x, 'y': y},
    }


def _funciones_modelos(dificultad):
    tipo = random.choice(['costo', 'dominio'])
    if tipo == 'costo':
        cf = random.randint(50, 200) * 10
        cu = random.randint(5, 25)
        x = random.randint(10, 50)
        total = cf + cu * x
        return {
            'operacion': f'Un servicio en la nube tiene un costo fijo mensual de ${cf} más ${cu} por cada usuario activo. ¿Cuál es el costo total para {x} usuarios?',
            'respuesta_correcta': str(total),
            'tipo': 'modelo_costo',
            'dificultad': dificultad,
            'explicacion_previa': 'El modelo lineal es C(x) = C_fijo + C_unitario · x.',
            'pistas': [f'C({x}) = {cf} + {cu} × {x}', f'{cf} + {cu * x} = {total}'],
            'numeros': {'total': total},
        }
    else:
        k = random.randint(2, 12)
        return {
            'operacion': f'¿Cuál es el valor mínimo de x para que la función f(x) = √(x - {k}) esté definida en los números reales? (es decir, x >= ?)',
            'respuesta_correcta': str(k),
            'tipo': 'dominio',
            'dificultad': dificultad,
            'explicacion_previa': 'La cantidad dentro de una raíz cuadrada debe ser mayor o igual a cero: x - k >= 0.',
            'pistas': [f'x - {k} >= 0', f'Despeja x: x >= {k}'],
            'numeros': {'k': k},
        }


def _composicion_inversa(dificultad):
    a = random.randint(2, 4)
    b = random.randint(1, 5)
    val = random.randint(1, 4)
    res = a * (val ** 2) + b

    return {
        'operacion': f'Si f(x) = {a}x + {b} y g(x) = x², calcula la composición (f o g)({val}) = f(g({val}))',
        'respuesta_correcta': str(res),
        'tipo': 'composicion',
        'dificultad': dificultad,
        'explicacion_previa': f'Evalúa primero la función interior g({val}), y luego aplica f al resultado.',
        'pistas': [f'g({val}) = {val}² = {val**2}', f'f({val**2}) = {a}({val**2}) + {b} = {res}'],
        'numeros': {'res': res},
    }


def _funciones_seccionadas(dificultad):
    corte = random.randint(2, 5)
    val = random.choice([corte - 1, corte + 2])
    m = random.randint(2, 4)
    k = random.randint(1, 6)

    if val < corte:
        res = m * val
    else:
        res = val + k

    return {
        'operacion': f'Sea f(x) = {m}x si x < {corte}, y f(x) = x + {k} si x >= {corte}. Calcula f({val}):',
        'respuesta_correcta': str(res),
        'tipo': 'seccionada',
        'dificultad': dificultad,
        'explicacion_previa': 'Identifica en qué tramo cae el valor pedido y evalúa únicamente en esa fórmula.',
        'pistas': [
            f'Compara: ¿{val} < {corte} o {val} >= {corte}?',
            f'Como {val} {"<" if val < corte else ">="} {corte}, usamos {"el primer tramo" if val < corte else "el segundo tramo"}',
            f'Resultado: {res}',
        ],
        'numeros': {'res': res},
    }


def _examen_parcial_ing(dificultad):
    gen = random.choice([_matrices_operaciones, _determinantes_inversa, _sistemas_cramer, _funciones_modelos])
    ej = gen(dificultad)
    ej['tipo'] = 'examen_parcial'
    return ej


def _coordenadas_polares(dificultad):
    r = random.randint(2, 8)
    ang = random.choice([0, 90, 180, 270])
    if ang == 0:
        coord = 'x'
        res = r
    elif ang == 90:
        coord = 'y'
        res = r
    elif ang == 180:
        coord = 'x'
        res = -r
    else:
        coord = 'y'
        res = -r

    return {
        'operacion': f'Dado el punto en coordenadas polares (r = {r}, θ = {ang}°), ¿cuánto vale su coordenada {coord} en el plano cartesiano?',
        'respuesta_correcta': str(res),
        'tipo': 'polares',
        'dificultad': dificultad,
        'explicacion_previa': 'Conversión polar a cartesiano: x = r · cos(θ) y y = r · sin(θ).',
        'pistas': [
            f'Fórmula: {coord} = {r} · {"cos" if coord == "x" else "sin"}({ang}°)',
            f'{"cos" if coord == "x" else "sin"}({ang}°) = {1 if res > 0 else -1}',
            f'{coord} = {res}',
        ],
        'numeros': {'res': res},
    }


def _limites_laterales(dificultad):
    m = random.randint(2, 5)
    b = random.randint(-4, 8)
    x0 = random.randint(-2, 4)
    res = m * x0 + b

    return {
        'operacion': f'Calcula el límite por sustitución directa: lím(x → {x0}) ({m}x {"+ " + str(b) if b >= 0 else "- " + str(abs(b))}) = ?',
        'respuesta_correcta': str(res),
        'tipo': 'limite_lateral',
        'dificultad': dificultad,
        'explicacion_previa': 'En funciones polinómicas continuas, el límite se calcula directamente sustituyendo el valor al que tiende x.',
        'pistas': [f'Sustituye x = {x0}', f'{m}({x0}) + ({b}) = {res}'],
        'numeros': {'res': res},
    }


def _limites_indeterminados(dificultad):
    a = random.randint(2, 6)
    res = 2 * a

    return {
        'operacion': f'Calcula el límite indeterminado (forma 0/0): lím(x → {a}) [(x² - {a*a}) / (x - {a})] = ?',
        'respuesta_correcta': str(res),
        'tipo': 'limite_indeterminado',
        'dificultad': dificultad,
        'explicacion_previa': 'Factoriza por diferencia de cuadrados x² - a² = (x - a)(x + a), cancela (x - a) y evalúa x + a.',
        'pistas': [
            f'Sustitución directa da ({a*a}-{a*a})/({a}-{a}) = 0/0 (indeterminación)',
            f'(x² - {a*a}) / (x - {a}) = x + {a}',
            f'Evalúa en {a}: {a} + {a} = {res}',
        ],
        'numeros': {'res': res},
    }


def _continuidad(dificultad):
    x0 = random.randint(1, 4)
    m = random.randint(2, 4)
    b = random.randint(1, 5)
    val = m * x0 + b

    return {
        'operacion': f'Para que la función f(x) = {m}x + {b} (si x < {x0}) y f(x) = k (si x >= {x0}) sea continua en x = {x0}, ¿cuánto debe valer la constante k?',
        'respuesta_correcta': str(val),
        'tipo': 'continuidad',
        'dificultad': dificultad,
        'explicacion_previa': 'Para que sea continua en x = x0, el límite por la izquierda debe ser igual al valor puntual f(x0) = k.',
        'pistas': [f'Calcula lím(x → {x0}^-) de ({m}x + {b})', f'{m}({x0}) + {b} = {val}', f'k debe ser igual a {val}'],
        'numeros': {'val': val},
    }


def _derivadas_optimizacion(dificultad):
    tipo = random.choice(['regla_potencia', 'punto_critico'])
    if tipo == 'regla_potencia':
        a = random.randint(2, 6)
        n = random.randint(2, 4)
        coef = a * n
        return {
            'operacion': f'¿Cuál es el coeficiente de la derivada de f(x) = {a}x^{n}? (regla de la potencia)',
            'respuesta_correcta': str(coef),
            'tipo': 'derivada',
            'dificultad': dificultad,
            'explicacion_previa': 'Regla de la potencia: la derivada de a·x^n es (a·n)·x^(n-1).',
            'pistas': [f'Multiplica el coeficiente por el exponente: {a} × {n} = {coef}', f'Resta 1 al exponente: {n} - 1 = {n-1}'],
            'numeros': {'coef': coef},
        }
    else:
        k = random.randint(2, 8)
        return {
            'operacion': f'Una función de costo en ingeniería es C(x) = x² - {2*k}x + 80. Halla el punto crítico (donde C\'(x) = 0) para minimizar el costo:',
            'respuesta_correcta': str(k),
            'tipo': 'optimizacion',
            'dificultad': dificultad,
            'explicacion_previa': 'Deriva la función C(x), iguala a cero C\'(x) = 0 y despeja x.',
            'pistas': [f'C\'(x) = 2x - {2*k}', f'2x - {2*k} = 0 -> 2x = {2*k}', f'x = {k}'],
            'numeros': {'k': k},
        }


def _examen_final_ing(dificultad):
    gen = random.choice([_limites_indeterminados, _continuidad, _derivadas_optimizacion, _coordenadas_polares])
    ej = gen(dificultad)
    ej['tipo'] = 'examen_final'
    return ej


# ============================================================
# EXPLICACIONES PASO A PASO
# ============================================================

def _explicar_suma(operacion, respuesta_correcta, respuesta_usuario=None):
    partes = operacion.split('+')
    a = int(partes[0].strip())
    b = int(partes[1].strip())
    resultado = a + b

    pasos = [
        f'Tenemos que calcular: {a} + {b}',
        f'Podemos empezar en {a} y contar {b} más:',
    ]

    if b <= 5:
        conteo = ', '.join(str(a + i) for i in range(1, b + 1))
        pasos.append(f'  {a} → {conteo}')
    else:
        pasos.append(f'  {a} + {b} = {resultado}')

    pasos.append(f'✅ El resultado es {resultado}')

    if respuesta_usuario and not verificar_respuesta(respuesta_usuario, respuesta_correcta):
        pasos.append(f'')
        pasos.append(f'Tu respuesta fue {respuesta_usuario}. La diferencia con el resultado correcto es {abs(int(respuesta_usuario) - resultado)}.')

    return {
        'pasos': pasos,
        'consejo': 'Si te cuesta, usa los dedos o dibuja palitos para contar.',
        'ejemplo_similar': f'Intenta ahora: {a + 1} + {b} = ?',
    }


def _explicar_resta(operacion, respuesta_correcta, respuesta_usuario=None):
    partes = operacion.split('-')
    a = int(partes[0].strip())
    b = int(partes[1].strip())
    resultado = a - b

    pasos = [
        f'Tenemos que calcular: {a} - {b}',
        f'Restar es quitar. Empezamos en {a} y quitamos {b}:',
    ]

    if b <= 5:
        conteo = ', '.join(str(a - i) for i in range(1, b + 1))
        pasos.append(f'  {a} → {conteo}')

    pasos.append(f'✅ El resultado es {resultado}')

    return {
        'pasos': pasos,
        'consejo': 'Piensa: si tienes ' + str(a) + ' cosas y quitas ' + str(b) + ', ¿cuántas quedan?',
        'ejemplo_similar': f'Intenta ahora: {a + 2} - {b} = ?',
    }


def _explicar_suma_llevadas(operacion, respuesta_correcta, respuesta_usuario=None):
    partes = operacion.split('+')
    a = int(partes[0].strip())
    b = int(partes[1].strip())
    resultado = a + b

    pasos = [
        f'Vamos a sumar {a} + {b} paso a paso:',
        f'',
        f'Columna de las unidades: {a % 10} + {b % 10} = {(a % 10) + (b % 10)}',
    ]

    if (a % 10) + (b % 10) >= 10:
        pasos.append(f'  Como {(a % 10) + (b % 10)} ≥ 10, escribimos {((a % 10) + (b % 10)) % 10} y llevamos 1')
        lleva = 1
    else:
        pasos.append(f'  Escribimos {(a % 10) + (b % 10)}')
        lleva = 0

    decenas_a = (a // 10) % 10
    decenas_b = (b // 10) % 10
    suma_decenas = decenas_a + decenas_b + lleva
    pasos.append(f'Columna de las decenas: {decenas_a} + {decenas_b} + {lleva} (lo que llevamos) = {suma_decenas}')

    pasos.append(f'')
    pasos.append(f'✅ El resultado es {resultado}')

    return {
        'pasos': pasos,
        'consejo': 'Siempre empieza por la derecha (unidades) y ve hacia la izquierda.',
        'ejemplo_similar': f'Practica con: {a + 10} + {b} = ?',
    }


def _explicar_resta_prestamos(operacion, respuesta_correcta, respuesta_usuario=None):
    partes = operacion.split('-')
    a = int(partes[0].strip())
    b = int(partes[1].strip())
    resultado = a - b

    pasos = [
        f'Vamos a restar {a} - {b} paso a paso:',
        f'',
        f'Columna de las unidades: {a % 10} - {b % 10}',
    ]

    if (a % 10) < (b % 10):
        pasos.append(f'  Como {a % 10} < {b % 10}, pedimos prestado a la decena')
        pasos.append(f'  {a % 10} se convierte en {a % 10 + 10}, y la decena de arriba baja de {(a // 10) % 10} a {(a // 10) % 10 - 1}')
        pasos.append(f'  Ahora: {a % 10 + 10} - {b % 10} = {a % 10 + 10 - b % 10}')

    pasos.append(f'')
    pasos.append(f'✅ El resultado es {resultado}')

    return {
        'pasos': pasos,
        'consejo': 'Pedir prestado es como cambiar un billete por monedas: la decena baja 1, las unidades suben 10.',
        'ejemplo_similar': f'Practica con: {a + 10} - {b} = ?',
    }


def _explicar_operacion_grande(operacion, respuesta_correcta, respuesta_usuario=None):
    if '+' in operacion:
        return _explicar_suma_llevadas(operacion, respuesta_correcta, respuesta_usuario)
    else:
        return _explicar_resta_prestamos(operacion, respuesta_correcta, respuesta_usuario)


def _explicar_calculo_mental(operacion, respuesta_correcta, respuesta_usuario=None):
    return {
        'pasos': [
            f'La operación es: {operacion}',
            f'El resultado correcto es: {respuesta_correcta}',
            'Trucos para cálculo mental:',
            '• Descompón los números en partes fáciles',
            '• Busca números que formen 10 o múltiplos de 10',
            '• Practica poco a poco, la velocidad llega con la práctica',
        ],
        'consejo': 'No te preocupes por la velocidad al principio. La rapidez viene con la práctica.',
        'ejemplo_similar': '',
    }


def _explicar_problema(operacion, respuesta_correcta, respuesta_usuario=None):
    return {
        'pasos': [
            'Para resolver problemas:',
            '1. Lee el problema completo con calma',
            '2. Identifica los datos (números que te dan)',
            '3. Decide qué operación necesitas:',
            '   - ¿Se juntan cosas? → Suma',
            '   - ¿Se quitan cosas? → Resta',
            '   - ¿Hay grupos iguales? → Multiplicación',
            '   - ¿Se reparte? → División',
            '4. Realiza la operación',
            '5. Revisa si tu respuesta tiene sentido',
            f'',
            f'✅ La respuesta correcta es: {respuesta_correcta}',
        ],
        'consejo': 'Subraya los números y las palabras clave del problema.',
        'ejemplo_similar': '',
    }


def _explicar_tablas(operacion, respuesta_correcta, respuesta_usuario=None):
    partes = operacion.split('×')
    a = int(partes[0].strip())
    b = int(partes[1].strip())

    pasos = [
        f'{a} × {b} significa sumar {a}, {b} veces:',
    ]

    if b <= 5:
        suma = ' + '.join([str(a)] * b)
        pasos.append(f'{suma} = {a * b}')
    else:
        pasos.append(f'{a} × {b} = {a * b}')
        pasos.append(f'')
        pasos.append(f'Truco: {a} × {b} = {a} × {b-1} + {a} = {a*(b-1)} + {a} = {a*b}')

    pasos.append(f'✅ Resultado: {a * b}')

    return {
        'pasos': pasos,
        'consejo': f'Practica la tabla del {a} hasta que la sepas de memoria.',
        'ejemplo_similar': f'{a} × {min(b + 1, 12)} = ?',
    }


def _explicar_multiplicacion_grande(operacion, respuesta_correcta, respuesta_usuario=None):
    partes = operacion.split('×')
    a = int(partes[0].strip())
    b = int(partes[1].strip())
    resultado = a * b

    pasos = [f'Multiplicamos {a} × {b} paso a paso:']

    if b < 10:
        pasos.append(f'{a} × {b} = {resultado}')
    else:
        unidades_b = b % 10
        decenas_b = (b // 10) * 10

        if unidades_b > 0:
            pasos.append(f'Paso 1: {a} × {unidades_b} (unidades) = {a * unidades_b}')
        if decenas_b > 0:
            pasos.append(f'Paso 2: {a} × {decenas_b} (decenas) = {a * decenas_b}')
        if unidades_b > 0 and decenas_b > 0:
            pasos.append(f'Paso 3: Sumamos: {a * unidades_b} + {a * decenas_b} = {resultado}')

    pasos.append(f'✅ Resultado: {resultado}')

    return {
        'pasos': pasos,
        'consejo': 'Descomponer el número facilita la multiplicación.',
        'ejemplo_similar': '',
    }


def _explicar_division(operacion, respuesta_correcta, respuesta_usuario=None):
    # Extraer números de la operación
    op_clean = operacion.split('(')[0].strip()
    partes = op_clean.replace('÷', '/').split('/')
    a = int(float(partes[0].strip()))
    b = int(float(partes[1].strip()))
    resultado = a // b

    pasos = [
        f'Dividimos {a} ÷ {b}:',
        f'Pregunta: ¿cuántas veces cabe {b} en {a}?',
        f'{b} × {resultado} = {b * resultado}',
        f'✅ Resultado: {resultado}',
    ]

    return {
        'pasos': pasos,
        'consejo': 'La división es la operación inversa de la multiplicación.',
        'ejemplo_similar': '',
    }


def _explicar_division_residuo(operacion, respuesta_correcta, respuesta_usuario=None):
    op_clean = operacion.split('(')[0].strip()
    partes = op_clean.replace('÷', '/').split('/')
    a = int(float(partes[0].strip()))
    b = int(float(partes[1].strip()))
    cociente = a // b
    residuo = a % b

    pasos = [
        f'Dividimos {a} ÷ {b}:',
        f'¿Cuántas veces cabe {b} en {a} sin pasarse?',
        f'{b} × {cociente} = {b * cociente}',
        f'Sobran: {a} - {b * cociente} = {residuo}',
        f'✅ Cociente: {cociente}, Residuo: {residuo}',
    ]

    return {
        'pasos': pasos,
        'consejo': 'El residuo siempre debe ser menor que el divisor.',
        'ejemplo_similar': '',
    }


def _explicar_generico(operacion, respuesta_correcta, respuesta_usuario=None):
    pasos = [
        f'La operación es: {operacion}',
        f'✅ La respuesta correcta es: {respuesta_correcta}',
    ]

    if respuesta_usuario:
        pasos.append(f'Tu respuesta fue: {respuesta_usuario}')

    return {
        'pasos': pasos,
        'consejo': 'Revisa el procedimiento paso a paso.',
        'ejemplo_similar': '',
    }


# ============================================================
# EVALUACIÓN DIAGNÓSTICA
# ============================================================

def generar_evaluacion_diagnostica():
    """Generar preguntas para la evaluación diagnóstica.

    Returns una lista de preguntas organizadas por nivel,
    comenzando por las más fáciles.
    """
    preguntas = []

    # Nivel 1: Sumas y restas básicas
    preguntas.extend([
        {'nivel': 1, 'tema': 'Sumas sencillas', 'ejercicio': generar_ejercicio('1.1', 1)},
        {'nivel': 1, 'tema': 'Sumas sencillas', 'ejercicio': generar_ejercicio('1.1', 2)},
        {'nivel': 1, 'tema': 'Restas sencillas', 'ejercicio': generar_ejercicio('1.2', 1)},
        {'nivel': 1, 'tema': 'Sumas con llevadas', 'ejercicio': generar_ejercicio('1.3', 1)},
        {'nivel': 1, 'tema': 'Restas con préstamos', 'ejercicio': generar_ejercicio('1.4', 1)},
    ])

    # Nivel 2: Multiplicaciones
    preguntas.extend([
        {'nivel': 2, 'tema': 'Tablas de multiplicar', 'ejercicio': generar_ejercicio('2.1', 1)},
        {'nivel': 2, 'tema': 'Tablas de multiplicar', 'ejercicio': generar_ejercicio('2.2', 1)},
        {'nivel': 2, 'tema': 'Multiplicación de dos cifras', 'ejercicio': generar_ejercicio('2.5', 1)},
    ])

    # Nivel 3: Divisiones
    preguntas.extend([
        {'nivel': 3, 'tema': 'Divisiones exactas', 'ejercicio': generar_ejercicio('3.2', 1)},
        {'nivel': 3, 'tema': 'Divisiones con residuo', 'ejercicio': generar_ejercicio('3.3', 1)},
    ])

    # Nivel 4: Fracciones
    preguntas.extend([
        {'nivel': 4, 'tema': 'Concepto de fracciones', 'ejercicio': generar_ejercicio('4.1', 1)},
        {'nivel': 4, 'tema': 'Porcentajes', 'ejercicio': generar_ejercicio('4.5', 1)},
    ])

    # Nivel 5: Potencias
    preguntas.extend([
        {'nivel': 5, 'tema': 'Potencias', 'ejercicio': generar_ejercicio('5.1', 1)},
        {'nivel': 5, 'tema': 'Raíces cuadradas', 'ejercicio': generar_ejercicio('5.3', 1)},
    ])

    # Nivel 6: Álgebra
    preguntas.extend([
        {'nivel': 6, 'tema': 'Números enteros', 'ejercicio': generar_ejercicio('6.1', 1)},
        {'nivel': 6, 'tema': 'Ecuaciones', 'ejercicio': generar_ejercicio('6.4', 1)},
    ])

    return preguntas


def analizar_diagnostico(resultados):
    """Analizar los resultados de la evaluación diagnóstica.

    Returns: nivel recomendado y lecciones a desbloquear.
    """
    nivel_maximo_dominado = 0
    recomendaciones = []

    # Agrupar por nivel
    por_nivel = {}
    primer_nivel_desconocido = None

    for r in resultados:
        nivel = r['nivel']
        if nivel not in por_nivel:
            por_nivel[nivel] = {'total': 0, 'correctas': 0, 'desconocidas': 0, 'temas': []}
        por_nivel[nivel]['total'] += 1
        if r.get('correcto'):
            por_nivel[nivel]['correctas'] += 1
        if r.get('desconocido'):
            por_nivel[nivel]['desconocidas'] += 1
            if primer_nivel_desconocido is None or nivel < primer_nivel_desconocido:
                primer_nivel_desconocido = nivel
        por_nivel[nivel]['temas'].append(r)

    for nivel in sorted(por_nivel.keys()):
        datos = por_nivel[nivel]
        porcentaje = (datos['correctas'] / datos['total'] * 100) if datos['total'] > 0 else 0

        if datos['desconocidas'] > 0:
            recomendaciones.append({
                'nivel': nivel,
                'tema': f'Nivel {nivel}',
                'total': datos['total'],
                'correctas': datos['correctas'],
                'porcentaje': porcentaje,
                'recomendacion': 'Tema no visto aún. Comenzaremos con la teoría y ejemplos desde cero.'
            })
        elif porcentaje >= 80:
            nivel_maximo_dominado = max(nivel_maximo_dominado, nivel)
            recomendaciones.append({
                'nivel': nivel,
                'tema': f'Nivel {nivel}',
                'total': datos['total'],
                'correctas': datos['correctas'],
                'porcentaje': porcentaje,
                'recomendacion': 'Dominas este nivel. Puedes avanzar directamente.'
            })
        elif porcentaje >= 50:
            recomendaciones.append({
                'nivel': nivel,
                'tema': f'Nivel {nivel}',
                'total': datos['total'],
                'correctas': datos['correctas'],
                'porcentaje': porcentaje,
                'recomendacion': 'Tienes una base, pero repasaremos la teoría y práctica guiada.'
            })
        else:
            recomendaciones.append({
                'nivel': nivel,
                'tema': f'Nivel {nivel}',
                'total': datos['total'],
                'correctas': datos['correctas'],
                'porcentaje': porcentaje,
                'recomendacion': 'Aprenderemos este nivel desde la teoría fundamental.'
            })

    # El nivel inicial recomendado
    if primer_nivel_desconocido is not None:
        nivel_inicio = min(primer_nivel_desconocido, nivel_maximo_dominado + 1)
    else:
        nivel_inicio = min(nivel_maximo_dominado + 1, 7)

    return {
        'nivel_recomendado': max(1, min(nivel_inicio, 7)),
        'resultados': recomendaciones,
    }
