from __future__ import annotations
from math import e
from typing import List, Dict
from datetime import date, datetime, timedelta
from abc import ABC, abstractmethod

class Estacion:

    def __init__(self, ubicacion, capacidad):
        self.ubicacion: str = ubicacion
        self.capacidad: int = capacidad
        self.bicicletas: List[Bicicleta] = []

    def registrarBicicleta(self, id_bicicleta) -> Bicicleta | None:
        if not self.estacionamientoDisponible():
            print(f"Error: No hay estacionamiento disponible en [{self.ubicacion}]")
            return None
        bicicleta = Bicicleta(id_bicicleta)
        self.bicicletas.append(bicicleta)
        return bicicleta
     
    def sacarBicicleta(self, bicicleta) -> bool:
        if not self.estaBicicleta(bicicleta):
            print(f"Error: Bicicleta no se encuentra la estacion {self.ubicacion}")
            return False
        self.bicicletas.remove(bicicleta)
        return True
               
    def estacionarBicicleta(self, bicicleta) -> bool:
        if not self.estacionamientoDisponible():
            print(f"Error: No hay estacionamiento disponible en {self.ubicacion}")
            return False
        self.bicicletas.append(bicicleta)
        return True 

    def bicicletaDisponible(self) -> bool:
        return bool(self.bicicletas)

    def estacionamientoDisponible(self) -> bool:
        return len(self.bicicletas) < self.capacidad
    
    def estaBicicleta(self, bicicleta) -> bool:
        return bicicleta in self.bicicletas

class Bicicleta:

    def __init__(self, id):
        self.id: str = id

class Usuario:
    
    def __init__(self, dni, nombre, apellido, num_tarjeta, abono = None):
        self.dni : str = dni
        self.nombre: str = nombre
        self.apellido: str = apellido
        self.num_tarjeta: str = num_tarjeta
        self.abono: Abono = abono

    def cambiarAbono(self, abono):
        self.abono = abono

class Uso:

    def __init__(self, usuario, bicicleta, estacion, fecha_hora):
        self.usuario: Usuario = usuario
        self.bicicleta: Bicicleta = bicicleta
        self.estacion_retirada: Estacion = estacion
        self.fecha_hora_retirada: datetime = fecha_hora
        self.estacion_devolucion: Estacion = None
        self.fecha_hora_devolucion: datetime = None
        self.pago: Pago = None
        
    def finalizarUso(self, estacion, fecha_hora):
        print(f"Finalizando Uso de {self.usuario.nombre}")
        self.estacion_devolucion = estacion
        self.fecha_hora_devolucion = fecha_hora
        importe = self.calcularCoste()
        self.pago = Pago(self.usuario.num_tarjeta, importe)
        self.pago.procesarPago()

    def bicicletaEnUso(self) -> bool:
        return self.estacion_devolucion is None

    def tiempoDeUso(self) -> timedelta:
        if self.fecha_hora_devolucion:
            return self.fecha_hora_devolucion - self.fecha_hora_retirada
        return timedelta(0)

    def calcularCoste(self) -> float:
        tiempo_de_uso = self.tiempoDeUso()
        precio = self.usuario.abono.calcularPrecio(tiempo_de_uso)
        print(f"Tiempo de uso: {tiempo_de_uso}, Coste: {precio:.2f}")
        return precio

class Abono(ABC):

    @abstractmethod
    def abonoValido(self) -> bool:
        pass

    @abstractmethod
    def calcularPrecio(self, tiempo_de_uso) -> float:
        pass

    def cobrarRetraso(self):
        pass

class AbonoAnual(Abono):
    
    def __init__(self, fecha_inicio):
        super().__init__()
        self.fecha_inicio: date = fecha_inicio

    def abonoValido(self) -> bool:
        return date.today() <= self.fecha_inicio + timedelta(days = 365)

    def calcularPrecio(self, tiempo_de_uso) -> float:
        if not self.abonoValido():
            print("Error: El abono ha vencido. No se puede calcular el precio.")
            return float('inf')
        
        tiempo_extra = max(tiempo_de_uso - timedelta(minutes = 30), timedelta(0))
        precio = ((tiempo_extra.total_seconds() // (5 * 60)) + 1) * 2
        return precio

class AbonoPrePago(Abono):    

    def __init__(self, saldo):
        super().__init__()
        self.saldo: float = saldo
  
    def abonoValido(self) -> bool:
        return self.saldo >= 5

    def calcularPrecio(self, tiempo_de_uso) -> float:
        if not self.abonoValido():
            print("Error: Saldo insuficiente")
            return float('inf')  

        precio = ((tiempo_de_uso.total_seconds() // (15 * 60)) + 1) * 5
        self.reducirSaldo(precio)
        return precio

    def recargarSaldo(self, recarga):
        self.saldo += recarga

    def reducirSaldo(self, pago):
        self.saldo -= pago
         
class AbonoTuristico(Abono):    

    def __init__(self, fecha_inicio):
        super().__init__()
        self.fecha_inicio: date = fecha_inicio

    def abonoValido(self) -> bool:
        return date.today() <= self.fecha_inicio + timedelta(days = 7)

    def calcularPrecio(self, tiempo_de_uso):
        if not self.abonoValido():
            print("Error: El abono ha vencido. No se puede calcular el precio.")
            return float('inf')
        
        tiempo_extra = max(tiempo_de_uso - timedelta(hours = 2), timedelta(0))
        precio = ((tiempo_extra.total_seconds() // (15 * 60)) + 1) * 10
        return precio


class Pago:
    
    def __init__(self, num_tarjeta, importe):
        self.num_tarjeta: str = num_tarjeta
        self.importe: float = importe

    def procesarPago(self) -> bool:
        #print(f"procesando pago en {self.num_tarjeta}. Importe: {self.importe}")
        return True


class Sistema:

    def __init__(self):
        self.estaciones: List[Estacion] = []
        self.usos: List[Uso] = []

    def registrarEstacion(self, ubicacion, capacidad) -> Estacion:
        estacion = Estacion(ubicacion, capacidad)
        self.estaciones.append(estacion)
        return estacion
        
    def iniciarUso(self, usuario, bicicleta, estacion, fecha_hora) -> Uso: 
        uso = Uso(usuario, bicicleta, estacion, fecha_hora)
        self.usos.append(uso)
        return uso

    def finalizarUso(self, uso, estacion, fecha_hora):
        uso.finalizarUso(estacion, fecha_hora)

    def estacionamientoDisponibleEn(self) -> None:
        print("Estaciones con estacionamiento(s) disponible:")
        for estacion in self.estaciones:
            if estacion.estacionamientoDisponible():
                print(f" [{estacion.ubicacion}]")

    def bicicletaDisponibleEn(self) -> None:
        print("Estaciones con bicicleta(s) disponible:")
        for estacion in self.estaciones:
            if estacion.bicicletaDisponible():
                print(f" [{estacion.ubicacion}]")

sistema = Sistema()
estacion1 = sistema.registrarEstacion("Estacion A", 5)
estacion2 = sistema.registrarEstacion("Estacion B", 10)

usuario1 = Usuario("1", "U1", "-", "1", AbonoAnual(date.today()))
usuario2 = Usuario("2", "U2", "-", "2", AbonoPrePago(100))
usuario3 = Usuario("3", "U3", "-", "3", AbonoTuristico(date.today()))

bicicleta1 = estacion1.registrarBicicleta("B001")
bicicleta2 = estacion1.registrarBicicleta("B002")
bicicleta3 = estacion1.registrarBicicleta("B003")

uso1 = sistema.iniciarUso(usuario1, bicicleta1, estacion1, datetime.now())
uso2 = sistema.iniciarUso(usuario2, bicicleta2, estacion1, datetime.now())
uso3 = sistema.iniciarUso(usuario3, bicicleta3, estacion1, datetime.now())

sistema.finalizarUso(uso1, estacion2, datetime.now() + timedelta(minutes = 59))
sistema.finalizarUso(uso2, estacion2, datetime.now() + timedelta(minutes = 59))
sistema.finalizarUso(uso3, estacion2, datetime.now() + timedelta(minutes = 59))

sistema.bicicletaDisponibleEn()
sistema.estacionamientoDisponibleEn()
