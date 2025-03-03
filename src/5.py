from __future__ import annotations
from abc import abstractmethod, ABC
from datetime import date, timedelta
from typing import List

class Usuario:
    
    def __init__(self, nombre, email, contraseña):
        self.nombre: str = nombre
        self.email: str = email
        self.contraseña: str = contraseña
        self.recursos_comprados: List[Recurso] = []

    def agregarRecursoComprado(self, recurso) -> None:
        self.recursos_comprados.append(recurso)

class Creador(Usuario):

    def __init__(self, nombre, email, contraseña):
        super().__init__(nombre, email, contraseña)
        self.puntos: float = 0
        self.recursos_creados: List[Recurso] = []

    def sumarPuntos(self, puntos) -> None:
        self.puntos += puntos

    def agregarRecursoCreado(self, recurso) -> None:
        self.recursos_creados.append(recurso)

class Recurso:

    def __init__(self, creador, descripcion, imagen, url, fecha_carga, precio_base, estrategia):
        self.creador: Creador = creador
        self.descripcion: str = descripcion
        self.imagen: str = imagen
        self.url: str = url
        self.fecha_carga: date = fecha_carga
        self.precio_base: float = precio_base
        self.estrategia: Estrategia = estrategia
        self.num_compras: int = 0

    def calcularPrecio(self) -> float:
        return self.estrategia.calcularPrecio(self.precio_base)

    def calcularPuntos(self) -> float:
        return self.estrategia.calcularPuntos(self.precio_base)

    def puedeLiberarRecurso(self) -> bool:
        return self.estrategia.puedeLiberarRecurso(self.num_compras)

    def incrementarCompra(self) -> None:
        self.num_compras += 1

class Estrategia(ABC):

    @abstractmethod
    def calcularPrecio(self, precio_base) -> float:
        pass    
    
    @abstractmethod
    def calcularPuntos(self, precio_base) -> float:
        pass

    @abstractmethod
    def puedeLiberarRecurso(self, num_compras) -> bool:
        pass

class EstrategiaNormal(Estrategia):
    
    def calcularPrecio(self, precio_base) -> float:
        return precio_base

    def calcularPuntos(self, precio_base) -> float:
        return precio_base * 10

    def puedeLiberarRecurso(self, num_compras) -> bool:
        return True

class EstrategiaOferta(Estrategia):

    def __init__(self, fecha_limite, porcentaje):
        self.fecha_limite: date = fecha_limite
        self.porcentaje: float = porcentaje

    def calcularPrecio(self, precio_base) -> float:
        if self.fecha_limite > date.today():
            return precio_base * (1 - self.porcentaje / 100)
        return precio_base

    def calcularPuntos(self, precio_base) -> float:
        precio_final = self.calcularPrecio(precio_base)
        if self.fecha_limite > date.today():
            return precio_final * 5
        return precio_final * 10

    def puedeLiberarRecurso(self, num_compras) -> bool:
        return True

class EstrategiaCrowdBased(Estrategia):
    
    def __init__(self, usuarios_minimos):
        self.usuarios_minimos: int = usuarios_minimos

    def calcularPrecio(self, precio_base) -> float:
        return precio_base

    def calcularPuntos(self, precio_base) -> float:
        return precio_base * 50 / self.usuarios_minimos

    def puedeLiberarRecurso(self, num_compras) -> bool:
        return num_compras >= self.usuarios_minimos
        

def comprarRecurso(usuario, recurso):

    precio = recurso.calcularPrecio()
    puntos = recurso.calcularPuntos()

    print(f"Precio: {precio}")
    print(f"Puntos: {puntos}")

    recurso.incrementarCompra()
    recurso.creador.sumarPuntos(puntos)
    usuario.agregarRecursoComprado(recurso)
    
    if recurso.puedeLiberarRecurso():
        print(f"Compra exitosa. Puedes descargar el recurso desde {recurso.url}.")
        return

    print(f"Compra en espera. Se necesita un mínimo de {recurso.estrategia.usuarios_minimos} compradores. Actualmente hay {recurso.num_compras}.")



# Crear usuarios
usuario1 = Usuario("Juan Perez", "juan@example.com", "1234")
usuario2 = Usuario("Maria Gomez", "maria@example.com", "5678")
usuario3 = Usuario("Carlos Ruiz", "carlos@example.com", "abcd1234")
creador1 = Creador("Ana Lopez", "ana@example.com", "abcd")

# Crear estrategias
estrategia_normal = EstrategiaNormal()
estrategia_oferta = EstrategiaOferta(date.today() + timedelta(days=5), 20)  # 20% de descuento hasta dentro de 5 días
estrategia_crowd = EstrategiaCrowdBased(3)  # Se necesitan al menos 3 compradores

# Crear recursos con diferentes estrategias
recurso1 = Recurso(creador1, "Recurso Normal", "imagen1.png", "http://recurso1.com", date.today(), 100, estrategia_normal)
recurso2 = Recurso(creador1, "Recurso en Oferta", "imagen2.png", "http://recurso2.com", date.today(), 200, estrategia_oferta)
recurso3 = Recurso(creador1, "Recurso Crowd-Based", "imagen3.png", "http://recurso3.com", date.today(), 300, estrategia_crowd)

# Agregar recursos creados al creador
creador1.agregarRecursoCreado(recurso1)
creador1.agregarRecursoCreado(recurso2)
creador1.agregarRecursoCreado(recurso3)

# Simular compras
print("Compra de recurso normal:")
comprarRecurso(usuario1, recurso1)

print("\nCompra de recurso en oferta:")
comprarRecurso(usuario1, recurso2)

print("\nCompra de recurso Crowd-Based:")
comprarRecurso(usuario1, recurso3)

# Segunda compra para el recurso Crowd-Based
print("\nSegunda compra del recurso Crowd-Based:")
comprarRecurso(usuario2, recurso3)

# Tercera compra para liberar el recurso Crowd-Based
print("\nTercera compra del recurso Crowd-Based:")
comprarRecurso(usuario3, recurso3)
