from datetime import date


class ModeloBase:
    def __init__(self, id_registro):
        self.id = int(id_registro)

    def a_diccionario(self):
        return {"id": self.id}

    @classmethod
    def desde_diccionario(cls, datos):
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def etiqueta(self):
        return f"#{self.id}"


class Persona(ModeloBase):
    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = str(nombre).strip()
        self.apellido = str(apellido).strip()
        self.email = str(email).strip().lower()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({"nombre": self.nombre, "apellido": self.apellido, "email": self.email})
        return datos

    def etiqueta(self):
        return f"{self.nombre} {self.apellido} · {self.email}"


class Estudiante(Persona):
    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = str(carnet).strip().upper()
        self.carrera = str(carrera).strip()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({"carnet": self.carnet, "carrera": self.carrera})
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera}"


class Materia(ModeloBase):
    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre = str(nombre).strip()
        self.codigo = str(codigo).strip().upper()
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        try:
            numero = float(valor)
            return 0 <= numero <= 20
        except (TypeError, ValueError):
            return False

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if self.hay_cupo():
            self.cupos -= 1
            return True
        return False

    def liberar_cupo(self):
        if self.cupos < self.CUPOS_MAXIMOS:
            self.cupos += 1
            return True
        return False

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({"nombre": self.nombre, "codigo": self.codigo,
                      "creditos": self.creditos, "cupos": self.cupos})
        return datos

    def etiqueta(self):
        return f"{self.nombre} · {self.codigo} · {self.creditos} créditos · {self.cupos} cupos"


class Matricula(ModeloBase):
    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=None, fecha=None):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo).strip()
        self.nota = None if nota in (None, "") else float(nota)
        self.fecha = str(fecha or date.today().isoformat())

    def esta_aprobada(self):
        return self.nota is not None and self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        if self.nota is None:
            return "Pendiente"
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({"estudiante_id": self.estudiante_id, "materia_id": self.materia_id,
                      "periodo": self.periodo, "nota": self.nota, "fecha": self.fecha})
        return datos

    def etiqueta(self):
        nota = "Sin nota" if self.nota is None else str(self.nota)
        return f"Matrícula #{self.id} · estudiante #{self.estudiante_id} · materia #{self.materia_id} · {self.periodo} · {nota} · {self.estado()}"
