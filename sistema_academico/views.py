from datetime import date
from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.validaciones import es_email_valido, texto_obligatorio, convertir_entero


gestor_estudiantes = GestorJSON("estudiantes.json")
gestor_materias = GestorJSON("materias.json")
gestor_matriculas = GestorJSON("matriculas.json")

# Funciones genéricas: el mismo código sirve para cualquier modelo y gestor.
def leer_objetos(gestor, modelo):
    return [modelo.desde_diccionario(registro) for registro in gestor.leer()]


def obtener_por_id(gestor, modelo, id_registro):
    try:
        buscado = int(id_registro)
    except (TypeError, ValueError):
        return None
    for registro in leer_objetos(gestor, modelo):
        if registro.id == buscado:
            return registro
    return None


def buscar(gestor, modelo, termino, campos):
    termino = str(termino).casefold().strip()
    if not termino:
        return []
    # Tupla: define el conjunto fijo de campos que se pueden buscar.
    return [obj for obj in leer_objetos(gestor, modelo)
            if any(termino in str(getattr(obj, campo, "")).casefold() for campo in campos)]


def siguiente_id(gestor):
    registros = gestor.leer()
    return max((int(r.get("id", 0)) for r in registros), default=0) + 1


def guardar_nuevo(gestor, objeto):
    registros = gestor.leer()
    registros.append(objeto.a_diccionario())
    gestor.guardar(registros)


def reemplazar(gestor, objeto):
    registros = gestor.leer()
    for indice, registro in enumerate(registros):
        if int(registro.get("id", -1)) == objeto.id:
            registros[indice] = objeto.a_diccionario()
            gestor.guardar(registros)
            return True
    return False


def eliminar(gestor, id_registro):
    registros = gestor.leer()
    filtrados = [r for r in registros if int(r.get("id", -1)) != int(id_registro)]
    if len(filtrados) == len(registros):
        return False
    gestor.guardar(filtrados)
    return True


def ids_registrados(gestor):
    # Set: comprobar pertenencia y duplicados de forma eficiente.
    return {int(r["id"]) for r in gestor.leer()}


def indice_por_id(gestor, modelo):
    # Diccionario índice {id: objeto} para localizar registros por id.
    return {obj.id: obj for obj in leer_objetos(gestor, modelo)}


def carnets_registrados(excepto_id=None):
    return {r["carnet"].upper() for r in gestor_estudiantes.leer() if r["id"] != excepto_id}


def emails_registrados(excepto_id=None):
    return {r["email"].lower() for r in gestor_estudiantes.leer() if r["id"] != excepto_id}


def codigos_registrados(excepto_id=None):
    return {r["codigo"].upper() for r in gestor_materias.leer() if r["id"] != excepto_id}


def validar_estudiante(datos, id_actual=None, al_crear=True):
    if al_crear and not all(texto_obligatorio(datos.get(k)) for k in ("nombre", "apellido", "email", "carnet", "carrera")):
        return "Nombre, apellido, email, carnet y carrera son obligatorios."
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        if campo in datos and not texto_obligatorio(datos[campo]):
            return f"El campo {campo} no puede quedar vacío."
    email = str(datos.get("email", "")).strip().lower()
    carnet = str(datos.get("carnet", "")).strip().upper()
    if email and not es_email_valido(email):
        return "El email no tiene un formato válido."
    if carnet and carnet in carnets_registrados(id_actual):
        return "Ese carnet ya está registrado."
    if email and email in emails_registrados(id_actual):
        return "Ese email ya está registrado."
    return None


def crear_estudiante(datos):
    error = validar_estudiante(datos)
    if error:
        return False, error
    estudiante = Estudiante(siguiente_id(gestor_estudiantes), datos["nombre"], datos["apellido"],
                            datos["email"], datos["carnet"], datos["carrera"])
    guardar_nuevo(gestor_estudiantes, estudiante)
    return True, f"Estudiante creado con ID {estudiante.id}."


def obtener_estudiantes(): return leer_objetos(gestor_estudiantes, Estudiante)
def obtener_estudiante(id_registro): return obtener_por_id(gestor_estudiantes, Estudiante, id_registro)
def buscar_estudiantes(termino): return buscar(gestor_estudiantes, Estudiante, termino, ("nombre", "apellido", "email", "carnet", "carrera"))


def actualizar_estudiante(id_registro, cambios):
    actual = obtener_estudiante(id_registro)
    if not actual: return False, "No existe un estudiante con ese ID."
    datos = actual.a_diccionario(); datos.update({k: v for k, v in cambios.items() if v is not None and str(v).strip()})
    error = validar_estudiante(datos, actual.id, al_crear=False)
    if error: return False, error
    actualizado = Estudiante(actual.id, datos["nombre"], datos["apellido"], datos["email"], datos["carnet"], datos["carrera"])
    reemplazar(gestor_estudiantes, actualizado)
    return True, "Estudiante actualizado."


def eliminar_estudiante(id_registro):
    if not obtener_estudiante(id_registro): return False, "No existe ese estudiante."
    if any(r["estudiante_id"] == int(id_registro) for r in gestor_matriculas.leer()):
        return False, "No se puede eliminar: tiene matrículas registradas. Retírelas primero."
    return (True, "Estudiante eliminado.") if eliminar(gestor_estudiantes, id_registro) else (False, "No se pudo eliminar.")


def crear_materia(datos):
    nombre, codigo = str(datos.get("nombre", "")).strip(), str(datos.get("codigo", "")).strip().upper()
    if not nombre or not codigo: return False, "Nombre y código son obligatorios."
    if codigo in codigos_registrados(): return False, "Ese código ya está registrado."
    creditos = convertir_entero(datos.get("creditos"), 1, 10)
    cupos = convertir_entero(datos.get("cupos"), 0, Materia.CUPOS_MAXIMOS)
    if creditos is None: return False, "Los créditos deben estar entre 1 y 10."
    if cupos is None: return False, f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}."
    materia = Materia(siguiente_id(gestor_materias), nombre, codigo, creditos, cupos)
    guardar_nuevo(gestor_materias, materia)
    return True, f"Materia creada con ID {materia.id}."


def obtener_materias(): return leer_objetos(gestor_materias, Materia)
def obtener_materia(id_registro): return obtener_por_id(gestor_materias, Materia, id_registro)
def buscar_materias(termino): return buscar(gestor_materias, Materia, termino, ("nombre", "codigo"))
def materias_sin_cupo(): return [m for m in obtener_materias() if not m.hay_cupo()]


def actualizar_materia(id_registro, cambios):
    actual = obtener_materia(id_registro)
    if not actual: return False, "No existe una materia con ese ID."
    datos = actual.a_diccionario(); datos.update({k: v for k, v in cambios.items() if v is not None and str(v).strip()})
    nombre, codigo = str(datos["nombre"]).strip(), str(datos["codigo"]).strip().upper()
    if not nombre or not codigo: return False, "Nombre y código son obligatorios."
    if codigo in codigos_registrados(actual.id): return False, "Ese código ya está registrado."
    creditos = convertir_entero(datos["creditos"], 1, 10)
    cupos = convertir_entero(datos["cupos"], 0, Materia.CUPOS_MAXIMOS)
    if creditos is None: return False, "Los créditos deben estar entre 1 y 10."
    if cupos is None: return False, f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}."
    actualizado = Materia(actual.id, nombre, codigo, creditos, cupos)
    reemplazar(gestor_materias, actualizado)
    return True, "Materia actualizada."


def eliminar_materia(id_registro):
    if not obtener_materia(id_registro): return False, "No existe esa materia."
    if any(r["materia_id"] == int(id_registro) for r in gestor_matriculas.leer()):
        return False, "No se puede eliminar: tiene matrículas. Retírelas primero."
    return (True, "Materia eliminada.") if eliminar(gestor_materias, id_registro) else (False, "No se pudo eliminar.")


def crear_matricula(datos):
    try:
        estudiante_id, materia_id = int(datos.get("estudiante_id")), int(datos.get("materia_id"))
    except (TypeError, ValueError): return False, "Los IDs de estudiante y materia deben ser números."
    estudiante, materia = obtener_estudiante(estudiante_id), obtener_materia(materia_id)
    if not estudiante: return False, "El estudiante no existe."
    if not materia: return False, "La materia no existe."
    if not materia.hay_cupo(): return False, "La materia no tiene cupos disponibles."
    periodo = str(datos.get("periodo", "")).strip()
    if not periodo: return False, "El periodo es obligatorio."
    # Comparar los tres campos evita matricular dos veces en la misma materia y periodo.
    if any(int(r["estudiante_id"]) == estudiante_id and int(r["materia_id"]) == materia_id and r["periodo"].casefold() == periodo.casefold() for r in gestor_matriculas.leer()):
        return False, "El estudiante ya está matriculado en esa materia durante ese periodo."
    matricula = Matricula(siguiente_id(gestor_matriculas), estudiante_id, materia_id, periodo, None, date.today().isoformat())
    guardar_nuevo(gestor_matriculas, matricula)
    materia.ocupar_cupo(); reemplazar(gestor_materias, materia)
    return True, f"Matrícula creada con ID {matricula.id}; cupos disponibles: {materia.cupos}."


def obtener_matriculas(): return leer_objetos(gestor_matriculas, Matricula)
def obtener_matricula(id_registro): return obtener_por_id(gestor_matriculas, Matricula, id_registro)


def registrar_nota(id_registro, nota):
    matricula = obtener_matricula(id_registro)
    if not matricula: return False, "No existe esa matrícula."
    if not Materia.es_nota_valida(nota): return False, "La nota debe ser un número entre 0 y 20."
    matricula.nota = float(nota)
    reemplazar(gestor_matriculas, matricula)
    return True, f"Nota registrada. Estado: {matricula.estado()}."


def retirar_matricula(id_registro):
    matricula = obtener_matricula(id_registro)
    if not matricula: return False, "No existe esa matrícula."
    materia = obtener_materia(matricula.materia_id)
    eliminar(gestor_matriculas, matricula.id)
    if materia:
        materia.liberar_cupo(); reemplazar(gestor_materias, materia)
    return True, "Matrícula retirada; el cupo ha sido liberado."


def certificado(id_registro):
    matricula = obtener_matricula(id_registro)
    if not matricula: return None
    # Índices por ID para resolver relaciones sin buscar repetidamente cada registro.
    estudiantes = indice_por_id(gestor_estudiantes, Estudiante)
    materias = indice_por_id(gestor_materias, Materia)
    estudiante, materia = estudiantes.get(matricula.estudiante_id), materias.get(matricula.materia_id)
    if not estudiante or not materia: return None
    return {"matricula": matricula, "estudiante": estudiante, "materia": materia}


def matriculas_por_estudiante():
    agrupadas = {}
    for matricula in obtener_matriculas():
        # Diccionario de listas: agrupa matrículas por estudiante y setdefault crea cada lista.
        agrupadas.setdefault(matricula.estudiante_id, []).append(matricula)
    return agrupadas


def promedio_de_estudiante(id_estudiante):
    notas = [m.nota for m in matriculas_por_estudiante().get(int(id_estudiante), []) if m.nota is not None]
    return sum(notas) / len(notas) if notas else None


def resumen():
    estudiantes = obtener_estudiantes()
    carreras = sorted({e.carrera for e in estudiantes if e.carrera})
    matriculas = obtener_matriculas()
    return {"estudiantes": len(estudiantes), "carreras": carreras,
            "materias_sin_cupo": materias_sin_cupo(),
            "matriculas_aprobadas": sum(m.esta_aprobada() for m in matriculas)}
