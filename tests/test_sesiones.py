"""
Tests - Fase 1: Sistema de Sesiones de Estudio
Verifica: iniciar, heartbeat, cierre, validez, auto-cierre y vinculacion con ejercicios.

Estrategia de mock: se parchean las funciones de database directamente
en lugar de simular SQL, evitando fragilidad ante cambios de queries.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import database


# ============================================================
# HELPERS
# ============================================================

def _make_sesion(sid, estado='abierta', ej_res=0, ej_cor=0,
                 ultima_actividad=None, tiempo_activo=0.0):
    """Crea un dict de sesion con los campos minimos necesarios."""
    ua = ultima_actividad or datetime.now().isoformat()
    return {
        'id': sid,
        'fecha_inicio': datetime.now().isoformat(),
        'estado': estado,
        'ultima_actividad': ua,
        'tiempo_activo_segundos': tiempo_activo,
        'ejercicios_resueltos': ej_res,
        'ejercicios_correctos': ej_cor,
        'es_valida': False,
        'fecha_fin': None,
        'duracion_minutos': 0,
    }


# ============================================================
# TESTS
# ============================================================

def test_iniciar_sesion_nueva(monkeypatch):
    """Una sesion nueva retorna un ID entero positivo cuando no hay ninguna abierta."""
    estado_db = {}  # almacen compartido

    def fake_get_db():
        sesiones = estado_db.setdefault('sesiones', {})
        next_id = estado_db.setdefault('next_id', [1])

        class Cur:
            description = None
            _result = None

            def execute(self, q, p=None):
                qu = ' '.join(q.split()).upper()
                if 'SELECT ID FROM SESIONES WHERE ESTADO' in qu:
                    abierta = [s['id'] for s in sesiones.values() if s['estado'] == 'abierta']
                    self._result = [(abierta[0],)] if abierta else []
                elif 'INSERT INTO SESIONES' in qu:
                    sid = next_id[0]
                    next_id[0] += 1
                    sesiones[sid] = _make_sesion(sid)
                    self._result = [(sid,)]
                elif 'SELECT LASTVAL' in qu or '@@IDENTITY' in qu:
                    pass  # _result ya tiene el sid del INSERT
                elif 'UPDATE SESIONES' in qu:
                    pass  # auto-cierre (no hay sesiones abiertas en este test)

            def fetchone(self):
                return self._result[0] if self._result else None
            def close(self): pass

        class Conn:
            def cursor(self): return Cur()
            def commit(self): pass
            def rollback(self): pass
            def close(self): pass

        return Conn()

    monkeypatch.setattr(database, 'get_db', fake_get_db)
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    sid = database.iniciar_sesion()
    assert sid is not None, "Debe retornar un ID"
    assert isinstance(sid, int)
    assert sid > 0


def test_no_doble_sesion(monkeypatch):
    """No se puede abrir una segunda sesion mientras hay una abierta."""
    sesiones = {1: _make_sesion(1, estado='abierta')}
    next_id = [2]

    class Cur:
        description = None
        _result = None

        def execute(self, q, p=None):
            qu = ' '.join(q.split()).upper()
            if 'SELECT ID FROM SESIONES WHERE ESTADO' in qu:
                abierta = [s['id'] for s in sesiones.values() if s['estado'] == 'abierta']
                self._result = [(abierta[0],)] if abierta else []
            elif 'UPDATE SESIONES' in qu:
                pass  # auto-cierre (la sesion existente no es antigua)

        def fetchone(self):
            return self._result[0] if self._result else None
        def close(self): pass

    class Conn:
        def cursor(self): return Cur()
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass

    monkeypatch.setattr(database, 'get_db', lambda: Conn())
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    sid = database.iniciar_sesion()
    assert sid is None, "Debe rechazar una segunda sesion abierta"


def test_heartbeat_acumula_tiempo(monkeypatch):
    """El heartbeat acumula tiempo_activo_segundos correctamente."""
    hace_20s = (datetime.now() - timedelta(seconds=20)).isoformat()
    sesiones = {1: _make_sesion(1, ultima_actividad=hace_20s, tiempo_activo=0.0)}

    class Cur:
        description = None
        _result = None

        def execute(self, q, p=None):
            qu = ' '.join(q.split()).upper()
            if 'SELECT ULTIMA_ACTIVIDAD' in qu:
                s = sesiones.get(p[0])
                if s and s['estado'] == 'abierta':
                    self._result = [(s['ultima_actividad'], s['tiempo_activo_segundos'])]
                else:
                    self._result = []
            elif 'UPDATE SESIONES' in qu and 'ULTIMA_ACTIVIDAD' in qu:
                ahora_str, nuevo_tiempo, sid = p[0], p[1], p[2]
                if sid in sesiones:
                    sesiones[sid]['ultima_actividad'] = ahora_str
                    sesiones[sid]['tiempo_activo_segundos'] = nuevo_tiempo

        def fetchone(self):
            return self._result[0] if self._result else None
        def close(self): pass

    class Conn:
        def cursor(self): return Cur()
        def commit(self): pass
        def close(self): pass

    monkeypatch.setattr(database, 'get_db', lambda: Conn())
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    ok = database.registrar_heartbeat(1)
    assert ok is True
    tiempo = sesiones[1]['tiempo_activo_segundos']
    assert 15 <= tiempo <= 25, f"Se esperaba ~20s, se obtuvo {tiempo}"


def test_heartbeat_tope_60s(monkeypatch):
    """Una pausa larga (>60s) solo suma maximo 60s."""
    hace_10min = (datetime.now() - timedelta(minutes=10)).isoformat()
    sesiones = {1: _make_sesion(1, ultima_actividad=hace_10min, tiempo_activo=0.0)}

    class Cur:
        description = None
        _result = None

        def execute(self, q, p=None):
            qu = ' '.join(q.split()).upper()
            if 'SELECT ULTIMA_ACTIVIDAD' in qu:
                s = sesiones.get(p[0])
                if s and s['estado'] == 'abierta':
                    self._result = [(s['ultima_actividad'], s['tiempo_activo_segundos'])]
                else:
                    self._result = []
            elif 'UPDATE SESIONES' in qu and 'ULTIMA_ACTIVIDAD' in qu:
                sesiones[p[2]]['tiempo_activo_segundos'] = p[1]

        def fetchone(self):
            return self._result[0] if self._result else None
        def close(self): pass

    class Conn:
        def cursor(self): return Cur()
        def commit(self): pass
        def close(self): pass

    monkeypatch.setattr(database, 'get_db', lambda: Conn())
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    ok = database.registrar_heartbeat(1)
    assert ok is True
    tiempo = sesiones[1]['tiempo_activo_segundos']
    assert tiempo <= 60.0, f"El tope de 60s no se respeto: {tiempo}"


def test_cerrar_sesion_valida(monkeypatch):
    """Una sesion con >= 3 ejercicios se marca como valida al cerrar."""
    sesiones = {1: _make_sesion(1, ej_res=4, ej_cor=3)}

    class Cur:
        description = None
        _result = None

        def execute(self, q, p=None):
            qu = ' '.join(q.split()).upper()
            if 'SELECT FECHA_INICIO' in qu and 'EJERCICIOS_RESUELTOS' in qu:
                s = sesiones.get(p[0])
                if s and s['estado'] == 'abierta':
                    self._result = [(s['fecha_inicio'], s['ejercicios_resueltos'], s['ejercicios_correctos'])]
                else:
                    self._result = []
            elif 'UPDATE SESIONES' in qu and 'FECHA_FIN' in qu:
                ahora_str, dur, es_val, sid = p
                sesiones[sid]['estado'] = 'cerrada'
                sesiones[sid]['duracion_minutos'] = dur
                sesiones[sid]['es_valida'] = es_val

        def fetchone(self):
            return self._result[0] if self._result else None
        def close(self): pass

    class Conn:
        def cursor(self): return Cur()
        def commit(self): pass
        def close(self): pass

    monkeypatch.setattr(database, 'get_db', lambda: Conn())
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    resultado = database.cerrar_sesion(1)
    assert resultado['ok'] is True
    assert resultado['es_valida'] is True
    assert resultado['ejercicios_resueltos'] == 4


def test_cerrar_sesion_invalida(monkeypatch):
    """Una sesion con < 3 ejercicios NO se marca como valida."""
    sesiones = {1: _make_sesion(1, ej_res=2, ej_cor=1)}

    class Cur:
        description = None
        _result = None

        def execute(self, q, p=None):
            qu = ' '.join(q.split()).upper()
            if 'SELECT FECHA_INICIO' in qu and 'EJERCICIOS_RESUELTOS' in qu:
                s = sesiones.get(p[0])
                if s and s['estado'] == 'abierta':
                    self._result = [(s['fecha_inicio'], s['ejercicios_resueltos'], s['ejercicios_correctos'])]
                else:
                    self._result = []
            elif 'UPDATE SESIONES' in qu and 'FECHA_FIN' in qu:
                sesiones[p[3]]['estado'] = 'cerrada'
                sesiones[p[3]]['es_valida'] = p[2]

        def fetchone(self):
            return self._result[0] if self._result else None
        def close(self): pass

    class Conn:
        def cursor(self): return Cur()
        def commit(self): pass
        def close(self): pass

    monkeypatch.setattr(database, 'get_db', lambda: Conn())
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    resultado = database.cerrar_sesion(1)
    assert resultado['ok'] is True
    assert resultado['es_valida'] is False


def test_auto_cierre_abandono(monkeypatch):
    """Sesiones sin actividad >30 min deben cerrarse solas al llamar iniciar_sesion."""
    hace_40min = (datetime.now() - timedelta(minutes=40)).isoformat()
    sesiones = {
        99: _make_sesion(99, estado='abierta', ultima_actividad=hace_40min)
    }
    next_id = [100]

    class Cur:
        description = None
        _result = None

        def execute(self, q, p=None):
            qu = ' '.join(q.split()).upper()
            if 'SELECT ID FROM SESIONES WHERE ESTADO' in qu:
                abierta = [s['id'] for s in sesiones.values() if s['estado'] == 'abierta']
                self._result = [(abierta[0],)] if abierta else []
            elif 'INSERT INTO SESIONES' in qu:
                sid = next_id[0]
                next_id[0] += 1
                sesiones[sid] = _make_sesion(sid)
                self._result = [(sid,)]
            elif 'SELECT LASTVAL' in qu or '@@IDENTITY' in qu:
                pass
            elif 'UPDATE SESIONES' in qu and 'ESTADO' in qu and 'ES_VALIDA' in qu and 'FECHA_FIN' in qu:
                # auto-cierre: UPDATE sesiones SET estado='cerrada', fecha_fin=?, es_valida=? WHERE ... ultima_actividad < ?
                fecha_fin, es_val, umbral = p
                for s in sesiones.values():
                    if (s['estado'] == 'abierta'
                            and s['ultima_actividad']
                            and s['ultima_actividad'] < umbral):
                        s['estado'] = 'cerrada'
                        s['fecha_fin'] = fecha_fin
                        s['es_valida'] = es_val

        def fetchone(self):
            return self._result[0] if self._result else None
        def close(self): pass

    class Conn:
        def cursor(self): return Cur()
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass

    monkeypatch.setattr(database, 'get_db', lambda: Conn())
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    sid_nuevo = database.iniciar_sesion()
    assert sid_nuevo is not None, "Debe poder iniciar sesion nueva"
    assert sesiones[99]['estado'] == 'cerrada', \
        "La sesion abandonada deberia haberse cerrado"


def test_cerrar_sesion_inexistente(monkeypatch):
    """Cerrar una sesion inexistente devuelve ok=False."""
    class Cur:
        description = None
        _result = None

        def execute(self, q, p=None):
            qu = ' '.join(q.split()).upper()
            if 'SELECT FECHA_INICIO' in qu:
                self._result = []  # no existe

        def fetchone(self):
            return self._result[0] if self._result else None
        def close(self): pass

    class Conn:
        def cursor(self): return Cur()
        def commit(self): pass
        def close(self): pass

    monkeypatch.setattr(database, 'get_db', lambda: Conn())
    monkeypatch.setattr(database, 'is_supabase', lambda: True)

    resultado = database.cerrar_sesion(9999)
    assert resultado['ok'] is False
    assert 'motivo' in resultado
