"""
Pruebas Unitarias - Motor de Aprendizaje Adaptativo y Evaluación Pedagógica
Verifica:
1. Exclusión precisa de los 2 registros de reinicio rápido (sin afectar otros 'No sé').
2. Diferenciación rigurosa de Casos A, B, C, D, E y F.
3. Consolidación de reintentos para no penalizar doblemente la auto-corrección.
4. Detección específica de patrones de error (préstamos, llevadas, signos, cálculo).
5. Generación de recomendaciones y diagnósticos pedagógicos basados en datos reales.
"""
import pytest
from database import (
    es_registro_excluido,
    consolidar_intentos_problema,
    evaluar_calidad_problema,
    obtener_estadisticas,
    obtener_diagnostico_pedagogico,
    obtener_recomendaciones_pedagogicas,
)
from ejercicios import clasificar_error


def test_exclusion_estricta_dos_registros_especiales():
    """Verifica que EXACTAMENTE los 2 registros históricos de reinicio rápido se excluyan,
    y que NINGÚN otro 'No sé' u otra resta quede excluida.
    """
    # 1. Los 2 registros específicos con respuesta 'No sé' (o variaciones de encoding)
    assert es_registro_excluido('6312 - 4916', '1396', '(No sé)') is True
    assert es_registro_excluido('6312 - 4916', '1396', '(No s)') is True
    assert es_registro_excluido('6312 - 4916', '1396', 'no se') is True
    assert es_registro_excluido('9825 - 7761', '2064', '(No sé)') is True
    assert es_registro_excluido('9825 - 7761', '2064', '(No s)') is True

    # 2. Otros ejercicios con respuesta 'No sé' NO deben excluirse
    assert es_registro_excluido('782 - 428', '354', '(No sé)') is False
    assert es_registro_excluido('544 - 157', '387', '(No sé)') is False
    assert es_registro_excluido('100 - 52', '48', '(No sé)') is False

    # 3. Mismas operaciones con respuestas matemáticas reales NO deben excluirse
    assert es_registro_excluido('6312 - 4916', '1396', '1396') is False
    assert es_registro_excluido('9825 - 7761', '2064', '2064') is False
    assert es_registro_excluido('6312 - 4916', '1396', '1400') is False


def test_diferenciacion_casos_pedagogicos():
    """Verifica la asignación de puntajes según el tipo de resolución (Casos A, B, C, D, E)."""
    # Caso A: 1er intento correcto sin ayuda
    p_a = {'es_correcto': True, 'intentos': 1, 'uso_ayuda': False, 'auto_corregido': False}
    score_a, caso_a = evaluar_calidad_problema(p_a)
    assert caso_a == 'A'
    assert score_a == 1.0

    # Caso B: Auto-corregido en 2do intento sin ayuda
    p_b = {'es_correcto': True, 'intentos': 2, 'uso_ayuda': False, 'auto_corregido': True}
    score_b, caso_b = evaluar_calidad_problema(p_b)
    assert caso_b == 'B'
    assert score_b == 0.85

    # Caso C: Múltiples intentos (3+) sin ayuda
    p_c = {'es_correcto': True, 'intentos': 3, 'uso_ayuda': False, 'auto_corregido': False}
    score_c, caso_c = evaluar_calidad_problema(p_c)
    assert caso_c == 'C'
    assert score_c == 0.65

    # Caso D: Error no corregido / dificultad real
    p_d = {'es_correcto': False, 'intentos': 1, 'uso_ayuda': False, 'auto_corregido': False}
    score_d, caso_d = evaluar_calidad_problema(p_d)
    assert caso_d == 'D'
    assert score_d == 0.0

    # Caso E: Correcto pero utilizando pistas (1 intento vs varios)
    p_e1 = {'es_correcto': True, 'intentos': 1, 'uso_ayuda': True, 'auto_corregido': False}
    score_e1, caso_e1 = evaluar_calidad_problema(p_e1)
    assert caso_e1 == 'E'
    assert score_e1 == 0.60

    p_e2 = {'es_correcto': True, 'intentos': 2, 'uso_ayuda': True, 'auto_corregido': False}
    score_e2, caso_e2 = evaluar_calidad_problema(p_e2)
    assert caso_e2 == 'E'
    assert score_e2 == 0.50


def test_consolidacion_intentos_autocorreccion():
    """Verifica que un reintento exitoso consolide el problema como auto-corrección
    en lugar de contar como un fallo permanente y penalizar al estudiante.
    """
    intentos_historial = [
        # Caso real del estudiante: 782 - 428 primero 364 (fallo), luego 354 (correcto)
        {
            'id': 58, 'leccion_id': '1.4', 'operacion': '782 - 428',
            'respuesta_correcta': '354', 'respuesta_usuario': '364',
            'es_correcto': False, 'intentos': 1, 'uso_ayuda': False, 'tipo_error': 'error_prestamo'
        },
        {
            'id': 59, 'leccion_id': '1.4', 'operacion': '782 - 428',
            'respuesta_correcta': '354', 'respuesta_usuario': '354',
            'es_correcto': True, 'intentos': 2, 'uso_ayuda': False, 'tipo_error': None
        }
    ]

    problemas = consolidar_intentos_problema(intentos_historial)
    assert len(problemas) == 1, "Debe consolidarse en exactamente 1 problema"
    p = problemas[0]
    assert p['es_correcto'] is True
    assert p['intentos'] == 2
    assert p['auto_corregido'] is True

    score, caso = evaluar_calidad_problema(p)
    assert caso == 'B'
    assert score == 0.85


def test_clasificacion_errores_prestamo_y_llevada():
    """Verifica la detección pedagógica de dificultades específicas."""
    # Descuido en resta con préstamo (diferencia de 10)
    # Ej: 782 - 428 = 354, usuario responde 364
    err_prestamo = clasificar_error('1.4', '782 - 428', '364', '354')
    assert err_prestamo == 'error_prestamo'

    # Descuido en suma con llevadas (diferencia de 10)
    # Ej: 39 + 42 = 81, usuario responde 71
    err_llevada = clasificar_error('1.3', '39 + 42', '71', '81')
    assert err_llevada == 'error_llevada'

    # Error aritmético menor
    err_calc = clasificar_error('1.1', '36 + 44', '81', '80')
    assert err_calc == 'error_calculo'

    # Error de signo
    err_signo = clasificar_error('6.1', '3 - 8', '5', '-5')
    assert err_signo == 'error_signo'


def test_diagnostico_y_recomendaciones_pedagogicas():
    """Verifica que las recomendaciones y el diagnóstico retornen datos estructurados y reales."""
    recs = obtener_recomendaciones_pedagogicas()
    assert isinstance(recs, list)
    for r in recs:
        assert 'tipo' in r
        assert 'icono' in r
        assert 'titulo' in r
        assert 'mensaje' in r

    diag = obtener_diagnostico_pedagogico()
    assert isinstance(diag, dict)
    assert 'total_ejercicios_evaluados' in diag
    assert 'precision_primer_intento' in diag
    assert 'ejercicios_autocorregidos' in diag
    assert 'resumen_pedagogico' in diag
    assert diag['total_ejercicios_evaluados'] > 0
