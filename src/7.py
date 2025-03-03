from datetime import date, timedelta
from abc import ABC, abstractmethod

class Proyectista:
    def __init__(self, nombre, email):
        self.nombre = nombre
        self.email = email

class Freelancer:
    def __init__(self, nombre, email, precio_hora, categorias):
        self.nombre = nombre
        self.email = email
        self.precio_hora = precio_hora
        self.categorias = categorias
        self.puntos = 0

    def agregar_puntos(self, puntos):
        self.puntos += puntos

class Proyecto:
    def __init__(self, nombre, descripcion, fecha_limite_ofertas, categorias):
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_limite_ofertas = fecha_limite_ofertas
        self.categorias = categorias
        self.ofertas = []
        self.oferta_ganadora = None
        self.finalizado = False
        self.fecha_finalizacion = None

    def agregar_oferta(self, oferta):
        self.ofertas.append(oferta)

    def recomendar_ofertas(self):
        return sorted(self.ofertas, key=lambda o: o.puntaje(self.fecha_limite_ofertas))

    def asignar_oferta(self, oferta):
        if oferta in self.ofertas:
            self.oferta_ganadora = oferta
        else:
            raise ValueError("La oferta no pertenece al proyecto.")

    def get_freelancer_asignado(self):
        if self.oferta_ganadora:
            return self.oferta_ganadora.freelancer
        return None

    def registrar_finalizacion(self, puntaje, fecha_finalizacion):
        if self.oferta_ganadora is None:
            raise ValueError("No hay freelancer asignado al proyecto.")
        if not (1 <= puntaje <= 50):
            raise ValueError("El puntaje debe estar entre 1 y 50.")
        self.finalizado = True
        self.fecha_finalizacion = fecha_finalizacion
        self.oferta_ganadora.freelancer.agregar_puntos(puntaje)

class Oferta(ABC):
    def __init__(self, freelancer, fecha_oferta):
        self.freelancer = freelancer
        self.fecha_oferta = fecha_oferta

    @abstractmethod
    def precio_final(self):
        pass

    @abstractmethod
    def dias_entrega(self, fecha_inicio):
        pass

    def puntaje(self, fecha_inicio):
        dias = self.dias_entrega(fecha_inicio)
        if dias <= 0:
            return float('inf')
        return self.precio_final() / dias

class OfertaPorHora(Oferta):
    def __init__(self, freelancer, fecha_oferta, horas_estimadas, fecha_entrega_estimada):
        super().__init__(freelancer, fecha_oferta)
        self.horas_estimadas = horas_estimadas
        self.fecha_entrega_estimada = fecha_entrega_estimada

    def precio_final(self):
        return self.horas_estimadas * self.freelancer.precio_hora

    def dias_entrega(self, fecha_inicio):
        delta = self.fecha_entrega_estimada - fecha_inicio
        return delta.days

class OfertaPorPosicion(Oferta):
    def __init__(self, freelancer, fecha_oferta, sueldo_mensual, horas_por_mes, meses):
        super().__init__(freelancer, fecha_oferta)
        self.sueldo_mensual = sueldo_mensual
        self.horas_por_mes = horas_por_mes
        self.meses = meses

    def precio_final(self):
        return self.sueldo_mensual * self.meses

    def dias_entrega(self, fecha_inicio):
        return self.meses * 30

class Plataforma:
    def __init__(self):
        self.proyectistas = []
        self.freelancers = []
        self.proyectos = []

    def registrar_proyectista(self, nombre, email):
        p = Proyectista(nombre, email)
        self.proyectistas.append(p)
        return p

    def registrar_freelancer(self, nombre, email, precio_hora, categorias):
        f = Freelancer(nombre, email, precio_hora, categorias)
        self.freelancers.append(f)
        return f

    def registrar_proyecto(self, nombre, descripcion, fecha_limite_ofertas, categorias):
        pr = Proyecto(nombre, descripcion, fecha_limite_ofertas, categorias)
        self.proyectos.append(pr)
        return pr

    def registrar_oferta(self, proyecto, oferta):
        proyecto.agregar_oferta(oferta)

    def buscar_proyecto_por_categoria(self, categoria):
        return [p for p in self.proyectos if categoria in p.categorias]

    def buscar_freelancer_por_categoria(self, categoria):
        return [f for f in self.freelancers if categoria in f.categorias]

    def recomendar_ofertas(self, proyecto):
        return proyecto.recomendar_ofertas()

    def asignar_oferta_a_proyecto(self, proyecto, oferta):
        proyecto.asignar_oferta(oferta)

    def get_freelancer_asignado(self, proyecto):
        return proyecto.get_freelancer_asignado()

    def registrar_finalizacion_proyecto(self, proyecto, puntaje, fecha_finalizacion):
        proyecto.registrar_finalizacion(puntaje, fecha_finalizacion)

if __name__ == "__main__":
    plataforma = Plataforma()
    proyectista1 = plataforma.registrar_proyectista("Sergio Firmenich", "sergio@example.com")
    freelancer1 = plataforma.registrar_freelancer("Alejandro Taylor", "alex@example.com", 20, ["Desarrollo Web", "Diseño Gráfico"])
    freelancer2 = plataforma.registrar_freelancer("Carlos Rangel", "carlos@example.com", 25, ["Desarrollo Web"])
    proyecto1 = plataforma.registrar_proyecto(
        "Aplicación Web",
        "Desarrollo de una aplicación web para e-commerce",
        date(2025, 3, 1),
        ["Desarrollo Web"]
    )
    oferta1 = OfertaPorHora(
        freelancer1,
        fecha_oferta=date(2025, 2, 20),
        horas_estimadas=100,
        fecha_entrega_estimada=date(2025, 4, 1)
    )
    oferta2 = OfertaPorPosicion(
        freelancer2,
        fecha_oferta=date(2025, 2, 21),
        sueldo_mensual=2000,
        horas_por_mes=160,
        meses=2
    )
    plataforma.registrar_oferta(proyecto1, oferta1)
    plataforma.registrar_oferta(proyecto1, oferta2)
    print("Ofertas recomendadas ordenadas por puntaje:")
    for oferta in plataforma.recomendar_ofertas(proyecto1):
        if isinstance(oferta, OfertaPorHora):
            print("OfertaPorHora - Freelancer:", oferta.freelancer.nombre, 
                  "Horas estimadas:", oferta.horas_estimadas, 
                  "Fecha entrega:", oferta.fecha_entrega_estimada, 
                  "Puntaje:", f"{oferta.puntaje(proyecto1.fecha_limite_ofertas):.2f}")
        elif isinstance(oferta, OfertaPorPosicion):
            print("OfertaPorPosicion - Freelancer:", oferta.freelancer.nombre, 
                  "Sueldo mensual:", oferta.sueldo_mensual, 
                  "Meses:", oferta.meses, 
                  "Puntaje:", f"{oferta.puntaje(proyecto1.fecha_limite_ofertas):.2f}")
    ofertas_recomendadas = plataforma.recomendar_ofertas(proyecto1)
    plataforma.asignar_oferta_a_proyecto(proyecto1, ofertas_recomendadas[0])
    freelancer_asignado = plataforma.get_freelancer_asignado(proyecto1)
    
    if freelancer_asignado:
        print("\nFreelancer asignado al proyecto:", freelancer_asignado.nombre)
    else:
        print("\nNo hay freelancer asignado al proyecto.")
        
    plataforma.registrar_finalizacion_proyecto(proyecto1, puntaje=40, fecha_finalizacion=date(2025, 4, 15))
    print("\nProyecto finalizado:", proyecto1.finalizado, "- Fecha finalización:", proyecto1.fecha_finalizacion)
    print("Puntos actuales del freelancer asignado:", freelancer_asignado.puntos)
    proyectos_devweb = plataforma.buscar_proyecto_por_categoria("Desarrollo Web")
    print("\nProyectos en la categoría 'Desarrollo Web':", [p.nombre for p in proyectos_devweb])
    freelancers_devweb = plataforma.buscar_freelancer_por_categoria("Desarrollo Web")
    print("Freelancers en la categoría 'Desarrollo Web':", [f.nombre for f in freelancers_devweb])
