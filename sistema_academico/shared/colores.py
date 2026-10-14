"""Funciones sencillas para mostrar mensajes consistentes en consola."""

def titulo(texto):
    return f"\n{'=' * 60}\n{texto.upper()}\n{'=' * 60}"


def mensaje(exito, texto):
    prefijo = "OK" if exito else "ERROR"
    return f"[{prefijo}] {texto}"
