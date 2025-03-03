from __future__ import annotations
from typing import List
from datetime import date
from abc import ABC, abstractmethod

class Usuario: 

    def __init__(self, nombre, email, clave):
        self.nombre: str = nombre
        self.email: str = email
        self.clave: str = clave
        self.matriculas: List[Matricula] = []
        self.bono: float = 0

    def cargarBono(self, bono) -> None:
        self.bono += bono

    def descontarBono(self, bono) -> None:
        self.bono -= bono
           
    def registrarMatricula(self, matricula) -> None:
        self.matriculas.append(matricula)

    def matricular(self, curso, fecha) -> Matricula:
        if curso.hayPlazasLibres():  
            descuento = min(self.bono, curso.precio * 0.5)
            importe = curso.precio - descuento
            self.descontarBono(descuento)
            matricula = Matricula(self, curso, importe, fecha)
            self.registrarMatricula(matricula)
            curso.registrarMatricula(matricula)    
            return matricula

class Curso(ABC): 

    def __init__(self, nombre, descripcion, precio):
        self.nombre: str = nombre
        self.descripcion: str = descripcion
        self.precio: float = precio
        self.valoraciones: List[Valoracion] = []
        self.matriculas: List[Matricula] = [] 

    @abstractmethod
    def hayPlazasLibres(self):
        pass

    @abstractmethod
    def comenzarCurso(self):
        pass

    def cambiarPrecio(self, precio) -> None:
        self.precio = precio

    def registrarMatricula(self, matricula) -> None:
        self.matriculas.append(matricula)

    def registrarValoracion(self, nota, fecha, comentario) -> None:
        if not (1 <= nota <= 5):
            return
        self.valoraciones.append(Valoracion(nota, fecha, comentario)) 

class CursoGrabado(Curso):

    def __init__(self, nombre, descripcion, precio):
        super().__init__(nombre, descripcion, precio)

    def hayPlazasLibres(self) -> bool:
        return True
    
    def comenzarCurso(self) -> None:
        pass

class CursoPresencial(Curso):
    
    def __init__(self, nombre, descripcion, precio, max_inscripciones, fecha_inicio, inscripciones_bono, porcentaje_bono):
        super().__init__(nombre, descripcion, precio)
        self.max_inscripciones: int = max_inscripciones
        self.fecha_inicio: date = fecha_inicio
        self.inscripciones_bono: int = inscripciones_bono
        self.porcentaje_bono: float = porcentaje_bono

    def hayPlazasLibres(self) -> bool:
        return len(self.matriculas) < self.max_inscripciones and date.today() < self.fecha_inicio

    def comenzarCurso(self) -> None:
        bono = self.calcularBono()
        self.repartirBono(bono)

    def calcularBono(self) -> float:
        if len(self.matriculas) > self.inscripciones_bono:
            return self.precio * self.porcentaje_bono / 100 
        return 0

    def repartirBono(self, bono) -> None:
        for matricula in self.matriculas:
            matricula.usuario.cargarBono(bono)
              
class Matricula:
    def __init__(self, usuario, curso, importe, fecha):
        self.usuario : Usuario = usuario
        self.curso: Curso = curso
        self.fecha: date = fecha
        self.importe: float = importe
        
class Valoracion:

    def __init__(self, nota, fecha, comentario):
        self.nota: int = nota
        self.fecha: date = fecha
        self.comentario: str = comentario

class Sistema:
    
    def __init__(self):
        self.usuarios: List[Usuario] = []
        self.cursos: List [Curso] = []

    def registrarUsuario(self, usuario) -> Usuario:
        self.usuarios.append(usuario)
        return usuario

    def registrarCurso(self, curso) -> Curso:
        self.cursos.append(curso)
        return curso

    def comenzarCurso(self, curso_presencial) -> None:
        curso_presencial.comenzarCurso()

    def getListado(self, usuario) -> None:
        print(f"Cursos de {usuario.nombre}")
        for matricula in usuario.matriculas:
            curso = matricula.curso
            print(f"  Nombre: {curso.nombre} - Precio: {curso.precio}€ - Importe pagado: {matricula.importe}€ - Fecha: {matricula.fecha}")
    
    def getPromedio(self) -> None:
        grabados = [curso for curso in self.cursos if isinstance(curso, CursoGrabado)]
        presenciales = [curso for curso in self.cursos if isinstance(curso, CursoPresencial)]
    
        prom_grabados = sum(len(c.matriculas) for c in grabados) / len(grabados) if grabados else 0
        prom_presenciales = sum(len(c.matriculas) for c in presenciales) / len(presenciales) if presenciales else 0

        print(f"Promedio de inscriptos en Cursos Grabados: {prom_grabados:.2f}")
        print(f"Promedio de inscriptos en Cursos Presenciales: {prom_presenciales:.2f}")

    def getMejorValoracion(self) -> None:
        cursos_valorados = [curso for curso in self.cursos if curso.valoraciones]
        cursos_valorados.sort(key=lambda c: sum(v.nota for v in c.valoraciones) / max(1, len(c.valoraciones)), reverse=True)
        
        print("Top 10 cursos con mejor valoración:")
        for curso in cursos_valorados[:10]:
            promedio_valoracion = sum(v.nota for v in curso.valoraciones) / len(curso.valoraciones)
            print(f"{curso.nombre} - Valoración promedio: {promedio_valoracion:.2f}")


sistema = Sistema();

u1 = sistema.registrarUsuario(Usuario("A", "-", "-"))
u2 = sistema.registrarUsuario(Usuario("B", "-", "-"))
u3 = sistema.registrarUsuario(Usuario("C", "-", "-"))
u4 = sistema.registrarUsuario(Usuario("D", "-", "-"))
u5 = sistema.registrarUsuario(Usuario("E", "-", "-"))
u6 = sistema.registrarUsuario(Usuario("F", "-", "-"))
u7 = sistema.registrarUsuario(Usuario("G", "-", "-"))
u8 = sistema.registrarUsuario(Usuario("H", "-", "-"))


c1 = sistema.registrarCurso(CursoGrabado("Curso de Python", "Aprende Python desde cero", 50))
c2 = sistema.registrarCurso(CursoPresencial("Curso de Marketing Digital", "Publicidad en redes sociales", 120, 15, date(2026, 3, 10), 1, 15))
c3 = sistema.registrarCurso(CursoGrabado("Curso de Fotografía", "Técnicas y edición fotográfica", 80))
c4 = sistema.registrarCurso(CursoPresencial("Curso de Finanzas Personales", "Administra mejor tu dinero", 150, 20, date(2025, 9, 1), 1, 20))
c5 = sistema.registrarCurso(CursoGrabado("Curso de Diseño Gráfico", "Photoshop, Illustrator y más", 90))
c6 = sistema.registrarCurso(CursoPresencial("Curso de Programación Web", "HTML, CSS y JavaScript", 200, 25, date(2025, 11, 15), 2, 12))
c7 = sistema.registrarCurso(CursoGrabado("Curso de Desarrollo Móvil", "Apps para iOS y Android", 110))
c8 = sistema.registrarCurso(CursoPresencial("Curso de Inteligencia Artificial", "Machine Learning y Deep Learning", 300, 30, date(2026, 5, 20), 2, 25))
c9 = sistema.registrarCurso(CursoGrabado("Curso de Escritura Creativa", "Técnicas narrativas y storytelling", 70))
c10 = sistema.registrarCurso(CursoPresencial("Curso de Gestión de Proyectos", "Metodologías ágiles y Scrum", 180, 18, date(2025, 7, 5), 3, 18))
c11 = sistema.registrarCurso(CursoGrabado("Curso de Música Digital", "Producción y mezcla de sonido", 95))


u1.matricular(c2, date.today())
u1.matricular(c5, date.today())
u1.matricular(c7, date.today())
u2.matricular(c1, date.today())
u2.matricular(c3, date.today())
u2.matricular(c8, date.today())
u3.matricular(c4, date.today())
u3.matricular(c6, date.today())
u3.matricular(c9, date.today())
u4.matricular(c2, date.today())
u4.matricular(c10, date.today())
u4.matricular(c11, date.today())
u5.matricular(c1, date.today())
u5.matricular(c5, date.today())
u5.matricular(c9, date.today())
u6.matricular(c3, date.today())
u6.matricular(c7, date.today())
u6.matricular(c11, date.today())
u7.matricular(c4, date.today())
u7.matricular(c6, date.today())
u7.matricular(c8, date.today())
u8.matricular(c2, date.today())
u8.matricular(c5, date.today())
u8.matricular(c10, date.today())


c1.registrarValoracion(5, date.today(), "-")
c1.registrarValoracion(4, date.today(), "-")
c1.registrarValoracion(3, date.today(), "-")
c2.registrarValoracion(5, date.today(), "-")
c2.registrarValoracion(5, date.today(), "-")
c2.registrarValoracion(4, date.today(), "-")
c3.registrarValoracion(3, date.today(), "-")
c3.registrarValoracion(2, date.today(), "-")
c3.registrarValoracion(1, date.today(), "-")
c4.registrarValoracion(4, date.today(), "-")
c4.registrarValoracion(4, date.today(), "-")
c4.registrarValoracion(5, date.today(), "-")
c5.registrarValoracion(5, date.today(), "-")
c5.registrarValoracion(5, date.today(), "-")
c5.registrarValoracion(5, date.today(), "-")
c6.registrarValoracion(2, date.today(), "-")
c6.registrarValoracion(3, date.today(), "-")
c6.registrarValoracion(4, date.today(), "-")
c7.registrarValoracion(5, date.today(), "-")
c7.registrarValoracion(5, date.today(), "-")
c7.registrarValoracion(4, date.today(), "-")
c8.registrarValoracion(3, date.today(), "-")
c8.registrarValoracion(4, date.today(), "-")
c8.registrarValoracion(5, date.today(), "-")
c9.registrarValoracion(1, date.today(), "-")
c9.registrarValoracion(2, date.today(), "-")
c9.registrarValoracion(3, date.today(), "-")
c10.registrarValoracion(4, date.today(), "-")
c10.registrarValoracion(4, date.today(), "-")
c10.registrarValoracion(5, date.today(), "-")
c11.registrarValoracion(5, date.today(), "-")
c11.registrarValoracion(4, date.today(), "-")
c11.registrarValoracion(3, date.today(), "-")

for curso in sistema.cursos:
    sistema.comenzarCurso(curso)

sistema.getListado(u1)
sistema.getListado(u2)
sistema.getListado(u3)
sistema.getListado(u4)
sistema.getListado(u5)
sistema.getListado(u6)
sistema.getListado(u7)
sistema.getListado(u8)

sistema.getPromedio()
sistema.getMejorValoracion()
