from datetime import date, timedelta
from abc import ABC, abstractmethod

class Persona:
    def __init__(self, nombre: str, email: str):
        self.nombre = nombre
        self.email = email
        self.puntaje = 0

class Asignacion:
    def __init__(self, desarrollador: Persona, fecha_inicio: date):
        self.desarrollador = desarrollador
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = None

    def cerrar(self, fecha: date):
        self.fecha_fin = fecha

class TareaBase(ABC):
    def __init__(self, titulo: str, descripcion: str, complejidad: int, fecha_limite: date):
        self.titulo = titulo
        self.descripcion = descripcion
        self.complejidad = max(1, min(5, complejidad))
        self.fecha_limite = fecha_limite
        self.fecha_creacion = date.today()
        self.fecha_cierre = None
        self.asignaciones = []

    def asignar(self, desarrollador: Persona):
        hoy = date.today()
        if self.asignaciones and self.asignaciones[-1].fecha_fin is None:
            self.asignaciones[-1].cerrar(hoy)
        self.asignaciones.append(Asignacion(desarrollador, hoy))

    def cerrar(self):
        hoy = date.today()
        self.fecha_cierre = hoy
        if self.asignaciones and self.asignaciones[-1].fecha_fin is None:
            self.asignaciones[-1].cerrar(hoy)

    def esta_cerrada(self) -> bool:
        return self.fecha_cierre is not None

    def se_cerro_a_tiempo(self) -> bool:
        return self.esta_cerrada() and self.fecha_cierre <= self.fecha_limite

    def obtener_desarrollador_actual(self):
        return self.asignaciones[-1].desarrollador if self.asignaciones else None

    @abstractmethod
    def puntaje_desarrollador(self) -> int:
        pass

class TareaDIU(TareaBase):
    def puntaje_desarrollador(self) -> int:
        return 2 * self.complejidad if self.se_cerro_a_tiempo() else 1

class TareaProgramacion(TareaBase):
    def puntaje_desarrollador(self) -> int:
        return self.complejidad ** 2 if self.se_cerro_a_tiempo() else 0

class Lista:
    def __init__(self, titulo: str):
        self.titulo = titulo
        self.tareas = []

    def agregar_tarea(self, tarea: TareaBase):
        self.tareas.append(tarea)

    def remover_tarea(self, tarea: TareaBase):
        if tarea in self.tareas:
            self.tareas.remove(tarea)

class Tablero:
    def __init__(self, titulo: str, lider: Persona):
        self.titulo = titulo
        self.lider = lider
        self.listas = {"Backlog": Lista("Backlog")}
        self.cerrado = False

    def agregar_lista(self, lista: Lista):
        self.listas[lista.titulo] = lista

    def agregar_tarea_a_lista(self, titulo_lista: str, tarea: TareaBase):
        if titulo_lista not in self.listas:
            self.listas[titulo_lista] = Lista(titulo_lista)
        self.listas[titulo_lista].agregar_tarea(tarea)

    def mover_tarea(self, tarea: TareaBase, titulo_lista_destino: str):
        for lista in self.listas.values():
            if tarea in lista.tareas:
                lista.remover_tarea(tarea)
                self.agregar_tarea_a_lista(titulo_lista_destino, tarea)
                return True
        return False

    def cerrar_sprint(self):
        if self.cerrado:
            return
        self.cerrado = True
        fecha_limite_sprint = date.today() - timedelta(days=15)
        for tarea in self.obtener_tareas():
            if tarea.esta_cerrada() and tarea.fecha_cierre >= fecha_limite_sprint:
                if tarea.se_cerro_a_tiempo():
                    self.lider.puntaje += 1
                desarrollador = tarea.obtener_desarrollador_actual()
                if desarrollador:
                    desarrollador.puntaje += tarea.puntaje_desarrollador()

    def obtener_tareas(self) -> list:
        return [tarea for lista in self.listas.values() for tarea in lista.tareas]

class Sistema:
    def __init__(self):
        self.tableros = []

    def crear_tablero(self, titulo: str, lider: Persona) -> Tablero:
        nuevo_tablero = Tablero(titulo, lider)
        self.tableros.append(nuevo_tablero)
        return nuevo_tablero

    def crear_tarea(self, tablero: Tablero, titulo: str, descripcion: str, complejidad: int, fecha_limite: date, tipo: str) -> TareaBase:
        if tipo.lower() == "diu":
            tarea = TareaDIU(titulo, descripcion, complejidad, fecha_limite)
        elif tipo.lower() == "programacion":
            tarea = TareaProgramacion(titulo, descripcion, complejidad, fecha_limite)
        else:
            raise ValueError("Tipo de tarea desconocido. Use 'DIU' o 'Programacion'.")
        tablero.agregar_tarea_a_lista("Backlog", tarea)
        return tarea

    def asignar_tarea(self, tarea: TareaBase, desarrollador: Persona) -> TareaBase:
        tarea.asignar(desarrollador)
        return tarea

    def mover_tarea(self, tarea: TareaBase, tablero: Tablero, titulo_lista_destino: str):
        tablero.mover_tarea(tarea, titulo_lista_destino)

    def cerrar_tarea(self, tarea: TareaBase):
        tarea.cerrar()

    def cerrar_sprint(self, tablero: Tablero):
        tablero.cerrar_sprint()

    def listar_tareas_pendientes(self) -> list:
        return sorted(
            [tarea for tablero in self.tableros for tarea in tablero.obtener_tareas() if not tarea.esta_cerrada()],
            key=lambda t: t.fecha_creacion
        )

    def listar_tareas_usuario(self, usuario: Persona) -> list:
        return [
            tarea for tablero in self.tableros for tarea in tablero.obtener_tareas()
            if usuario in [asignacion.desarrollador for asignacion in tarea.asignaciones]
        ]

if __name__ == "__main__":
    lider = Persona("Sergio Firmenich", "sergio@example.com")
    dev1 = Persona("Alejandro Taylor", "alex@example.com")
    dev2 = Persona("Carlos Rangel", "carlos@example.com")
    
    sistema = Sistema()
    tablero = sistema.crear_tablero("Proyecto Alpha", lider)

    tarea1 = sistema.crear_tarea(tablero, "Implementar login", "Desarrollar la funcionalidad de login", 3, date(2025, 3, 15), "Programacion")
    tarea2 = sistema.crear_tarea(tablero, "Diseño de interfaz", "Crear el diseño de la pantalla principal", 2, date(2025, 3, 10), "DIU")

    sistema.asignar_tarea(tarea1, dev1)
    sistema.asignar_tarea(tarea2, dev2)

    sistema.cerrar_tarea(tarea1)
    sistema.cerrar_tarea(tarea2)

    sistema.cerrar_sprint(tablero)

    print("Puntaje del líder:", lider.puntaje)
    print("Puntaje de Alejandro:", dev1.puntaje)
    print("Puntaje de Carlos:", dev2.puntaje)
    print("Cantidad de tareas pendientes:", len(sistema.listar_tareas_pendientes()))
    print("Cantidad de tareas de Alejandro:", len(sistema.listar_tareas_usuario(dev1)))
