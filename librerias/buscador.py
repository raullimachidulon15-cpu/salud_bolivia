"""Búsqueda y medición de eficiencia."""
import time, unicodedata

def _norm(s):
    s = unicodedata.normalize("NFD", str(s).lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def buscar_secuencial(lista, atributo, valor):
    valor_buscado = _norm(valor)
    resultados = []

    for registro in lista:
        if isinstance(registro, dict):
            dato = registro.get(atributo, "")
        else:
            dato = getattr(registro, atributo, "")

        if valor_buscado in _norm(dato):
            resultados.append(registro)

    return resultados

def buscar_binaria(lista_ordenada, atributo, valor):
    v = _norm(valor)
    ini, fin = 0, len(lista_ordenada)-1
    while ini <= fin:
        medio = (ini + fin)//2
        registro = lista_ordenada[medio]
        actual = _norm(registro.get(atributo, "") if isinstance(registro, dict) else getattr(registro, atributo, ""))
        if actual == v: return lista_ordenada[medio]
        if actual < v: ini = medio+1
        else: fin = medio-1
    return None

def ordenar_por(lista, atributo):
    return sorted(lista, key=lambda x: _norm(x.get(atributo, "") if isinstance(x, dict) else getattr(x, atributo, "")))

def medir_tiempo(funcion, *args, **kwargs):
    t0 = time.perf_counter()
    resultado = funcion(*args, **kwargs)
    return resultado, (time.perf_counter()-t0)*1000
