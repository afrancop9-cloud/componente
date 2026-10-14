from shared.colores import titulo, mensaje
import views


def pedir(texto, obligatorio=True):
    while True:
        valor = input(texto).strip()
        if valor or not obligatorio:
            return valor
        print("Este campo es obligatorio.")


def mostrar_lista(registros, encabezado="REGISTROS"):
    print(titulo(encabezado))
    if not registros:
        print("No hay registros.")
        return
    # Polimorfismo: cada modelo implementa etiqueta() con sus propios datos.
    for registro in registros:
        print(f"{registro.etiqueta()}")


def mostrar_detalle(objeto):
    if objeto is None:
        print("No se encontró el registro.")
    else:
        print(objeto.etiqueta())
        print(objeto.a_diccionario())


def pedir_id():
    try: return int(pedir("ID: "))
    except ValueError:
        print("El ID debe ser numérico.")
        return None


def menu_crud(entidad):
    funciones = {
        "estudiantes": (views.obtener_estudiantes, views.obtener_estudiante, views.buscar_estudiantes,
                        views.crear_estudiante, views.actualizar_estudiante, views.eliminar_estudiante),
        "materias": (views.obtener_materias, views.obtener_materia, views.buscar_materias,
                     views.crear_materia, views.actualizar_materia, views.eliminar_materia),
    }
    obtener_todos, obtener_uno, buscar, crear, actualizar, eliminar = funciones[entidad]
    while True:
        print(titulo(f"{entidad}: gestión CRUD"))
        print("1. Crear\n2. Ver todos\n3. Buscar\n4. Ver por ID\n5. Actualizar\n6. Eliminar\n0. Volver")
        op = input("Opción: ").strip()
        if op == "0": return
        if op == "1":
            if entidad == "estudiantes":
                datos = {k: pedir(etq) for k, etq in [("nombre", "Nombre: "), ("apellido", "Apellido: "), ("email", "Email: "), ("carnet", "Carnet: "), ("carrera", "Carrera: ")]}
            else:
                datos = {k: pedir(etq) for k, etq in [("nombre", "Nombre de la materia: "), ("codigo", "Código: "), ("creditos", "Créditos (1-10): "), ("cupos", "Cupos (0-30): ")]}
            print(mensaje(*crear(datos)))
        elif op == "2": mostrar_lista(obtener_todos(), entidad)
        elif op == "3": mostrar_lista(buscar(pedir("Texto a buscar: ")), "RESULTADOS")
        elif op == "4": mostrar_detalle(obtener_uno(pedir_id()))
        elif op == "5":
            ident = pedir_id()
            if ident is None: continue
            if entidad == "estudiantes":
                campos = [("nombre", "Nombre"), ("apellido", "Apellido"), ("email", "Email"), ("carnet", "Carnet"), ("carrera", "Carrera")]
            else:
                campos = [("nombre", "Nombre"), ("codigo", "Código"), ("creditos", "Créditos"), ("cupos", "Cupos")]
            cambios = {k: input(f"{etq} (Enter conserva el actual): ").strip() for k, etq in campos}
            print(mensaje(*actualizar(ident, cambios)))
        elif op == "6":
            ident = pedir_id()
            if ident is not None and input("¿Confirmar eliminación? (s/n): ").lower() == "s":
                print(mensaje(*eliminar(ident)))
        else: print("Opción no válida.")


def menu_matriculas():
    while True:
        print(titulo("Matrículas"))
        print("1. Matricular\n2. Ver todas\n3. Registrar nota\n4. Ver certificado\n5. Retirar matrícula\n0. Volver")
        op = input("Opción: ").strip()
        if op == "0": return
        if op == "1":
            mostrar_lista(views.obtener_estudiantes(), "ESTUDIANTES")
            mostrar_lista(views.obtener_materias(), "MATERIAS")
            datos = {"estudiante_id": pedir("ID estudiante: "), "materia_id": pedir("ID materia: "), "periodo": pedir("Periodo (ej. 2026-1): ")}
            print(mensaje(*views.crear_matricula(datos)))
        elif op == "2": mostrar_lista(views.obtener_matriculas(), "MATRÍCULAS")
        elif op == "3":
            ident = pedir_id()
            if ident is not None: print(mensaje(*views.registrar_nota(ident, pedir("Nota (0-20): "))))
        elif op == "4":
            ident = pedir_id(); datos = views.certificado(ident) if ident is not None else None
            if not datos: print("No se encontró el certificado o faltan registros relacionados.")
            else:
                m, e, a = datos["matricula"], datos["estudiante"], datos["materia"]
                print(titulo(f"CERTIFICADO #{m.id} · Periodo: {m.periodo}"))
                print(f"Estudiante: {e.nombre} {e.apellido} ({e.carnet})")
                print(f"Materia: {a.nombre} ({a.codigo}) · {a.creditos} créditos")
                print(f"Nota: {'Sin registrar' if m.nota is None else m.nota}\nEstado: {m.estado()}")
        elif op == "5":
            ident = pedir_id()
            if ident is not None: print(mensaje(*views.retirar_matricula(ident)))
        else: print("Opción no válida.")


def mostrar_resumen():
    datos = views.resumen()
    print(titulo("Resumen académico"))
    print(f"Estudiantes registrados: {datos['estudiantes']}")
    print("Carreras distintas: " + (", ".join(datos["carreras"]) if datos["carreras"] else "ninguna"))
    print("Materias sin cupo:")
    mostrar_lista(datos["materias_sin_cupo"], "MATERIAS SIN CUPO")
    print(f"Matrículas aprobadas: {datos['matriculas_aprobadas']}")


def main():
    while True:
        print(titulo("Sistema académico · MVC + CRUD"))
        print("1. Estudiantes\n2. Materias\n3. Matrículas\n4. Resumen\n0. Salir")
        op = input("Opción: ").strip()
        if op == "1": menu_crud("estudiantes")
        elif op == "2": menu_crud("materias")
        elif op == "3": menu_matriculas()
        elif op == "4": mostrar_resumen()
        elif op == "0": print("Hasta luego."); break
        else: print("Opción no válida.")


if __name__ == "__main__":
    main()
