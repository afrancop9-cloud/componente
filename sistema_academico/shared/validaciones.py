import re


def es_email_valido(email):
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", str(email).strip()))


def texto_obligatorio(valor):
    return bool(str(valor or "").strip())


def convertir_entero(valor, minimo=None, maximo=None):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        return None
    if minimo is not None and numero < minimo:
        return None
    if maximo is not None and numero > maximo:
        return None
    return numero
