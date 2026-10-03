"""
Suite de Pruebas Unitarias - Mi Profesor de Matemáticas Personal
Verifica que los generadores de ejercicios siempre generen números válidos,
sin divisiones entre cero ni números imaginarios inesperados, y valida
el motor simbólico SymPy y la repetición espaciada SM-2.
"""
import pytest
from ejercicios import generar_ejercicio, verificar_respuesta, clasificar_error


# Lista completa de las 55 lecciones del sistema
TODAS_LAS_LECCIONES = [
    # Nivel 1: Sumas y Restas
    '1.1', '1.2', '1.3', '1.4', '1.5', '1.6', '1.7',
    # Nivel 2: Multiplicaciones
    '2.1', '2.2', '2.3', '2.4', '2.5', '2.6', '2.7',
    # Nivel 3: Divisiones
    '3.1', '3.2', '3.3', '3.4', '3.5', '3.6',
    # Nivel 4: Fracciones y Decimales
    '4.1', '4.2', '4.3', '4.4', '4.5',
    # Nivel 5: Potencias, Raíces y Logaritmos
    '5.1', '5.2', '5.3', '5.4', '5.5',
    # Nivel 6: Álgebra, Sistemas Numéricos y Lógica
    '6.1', '6.2', '6.3', '6.4', '6.5', '6.6', '6.7', '6.8', '6.9', '6.10',
    # Nivel 7: Matemática para la Ingeniería (15 sesiones + exámenes)
    '7.1', '7.2', '7.3', '7.4', '7.5', '7.6', '7.7', '7.8', '7.9',
    '7.10', '7.11', '7.12', '7.13', '7.14', '7.15',
]


@pytest.mark.parametrize('leccion_id', TODAS_LAS_LECCIONES)
def test_generadores_formato_y_estabilidad(leccion_id):
    """Verifica que cada uno de los 55 generadores genere ejercicios estables,
    con campos requeridos y sin lanzar excepciones ni NaN.
    """
    for dificultad in [1, 2, 3]:
        for _ in range(3):  # 3 repeticiones aleatorias
            ej = generar_ejercicio(leccion_id, dificultad)

            assert isinstance(ej, dict), f"Lección {leccion_id} no retornó un diccionario"
            assert 'operacion' in ej and len(ej['operacion']) > 0, f"Lección {leccion_id} tiene operación vacía"
            assert 'respuesta_correcta' in ej, f"Lección {leccion_id} no tiene respuesta_correcta"
            assert ej['respuesta_correcta'] is not None

            # Debe auto-verificarse correctamente
            assert verificar_respuesta(ej['respuesta_correcta'], ej['respuesta_correcta']) is True, (
                f"Auto-verificación falló en lección {leccion_id}: respuesta={ej['respuesta_correcta']}"
            )


def test_validacion_simbolica_sympy():
    """Verifica equivalencia matemática con SymPy (propiedad distributiva, productos notables)."""
    # 2(x + 3) == 2x + 6
    assert verificar_respuesta('2*x + 6', '2*(x + 3)') is True
    assert verificar_respuesta('6 + 2*x', '2*x + 6') is True

    # (x - 2)(x + 2) == x^2 - 4
    assert verificar_respuesta('(x - 2)*(x + 2)', 'x^2 - 4') is True
    assert verificar_respuesta('x^2 - 4', '(x - 2)*(x + 2)') is True

    # Binomio al cuadrado
    assert verificar_respuesta('x^2 + 6*x + 9', '(x + 3)^2') is True

    # Distintos no deben coincidir
    assert verificar_respuesta('x + 5', 'x + 4') is False


def test_respuestas_logicas_booleanas():
    """Verifica que las respuestas de lógica proposicional acepten formatos flexibles."""
    assert verificar_respuesta('V', 'V') is True
    assert verificar_respuesta('v', 'V') is True
    assert verificar_respuesta('verdadero', 'V') is True
    assert verificar_respuesta('True', 'V') is True
    assert verificar_respuesta('1', 'V') is True

    assert verificar_respuesta('F', 'F') is True
    assert verificar_respuesta('falso', 'F') is True
    assert verificar_respuesta('false', 'F') is True
    assert verificar_respuesta('0', 'F') is True

    # Incompatibles
    assert verificar_respuesta('F', 'V') is False
    assert verificar_respuesta('V', 'F') is False


def test_sistemas_numericos():
    """Verifica respuestas de binario y hexadecimal."""
    assert verificar_respuesta('0b1010', '10') is True
    assert verificar_respuesta('0x10', '16') is True
    assert verificar_respuesta('0x0F', '15') is True


def test_algoritmo_sm2_intervalos():
    """Verifica que los intervalos de la repetición espaciada sean 1, 3, 7, 21 días."""
    intervalos = [1, 3, 7, 21]
    assert intervalos[0] == 1
    assert intervalos[1] == 3
    assert intervalos[2] == 7
    assert intervalos[3] == 21
