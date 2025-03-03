from __future__ import annotations
from datetime import date
from typing import List

class Usuario:

    def __init__(self, nombre):
        self.nombre: str = nombre
        self.propiedades: List[Propiedad] = []
        self.reservas: List[Reserva] = []

    def registrarPropiedad(self, propiedad) -> Propiedad:
        self.propiedades.append(propiedad)
        return propiedad

    def registrarReserva(self, reserva) -> Reserva:
        self.reservas.append(reserva)
        return reserva

class Propiedad:

    def __init__(self, nombre, precio_por_noche):
        self.nombre: str = nombre   
        self.precio_por_noche: float = precio_por_noche
        self.reservas: List[Reserva] = []
        self.reglas: List[Regla] = [] 

    def registrarReserva(self, reserva) -> Reserva:
        self.reservas.append(reserva)
        return reserva

    def registrarRegla(self, regla) -> Regla:
        if self.comprobarRegla(regla):
            self.reglas.append(regla)
        else:
            print("ERROR: [Regla no valida]") 
        return regla

    def comprobarRegla(self, regla) -> bool:
        if isinstance(regla, ReglaRangoFechas):
            for regla_existente in self.reglas:
                if isinstance(regla_existente, ReglaRangoFechas) and regla_existente.solapaCon(regla):
                    return False
        if isinstance(regla, ReglaEstanciaProlongada):
            for regla_existente in self.reglas:
                if isinstance(regla_existente, ReglaEstanciaProlongada):
                    return False
        return True 
    
    def propiedadDisponible(self, fecha_inicio, fecha_fin) -> bool:
        for reserva in self.reservas:
            if fecha_inicio < reserva.fecha_fin and fecha_fin > reserva.fecha_inicio:
                return False
        return True
      
    def __repr__(self) -> str:
        return f"Propiedad({self.nombre}, Precio: {self.precio_por_noche}€)"

class Reserva:

    def __init__(self, usuario, propiedad, fecha_inicio, fecha_fin):
        self.usuario: Usuario = usuario
        self.propiedad: Propiedad = propiedad
        self.fecha_inicio: date = fecha_inicio
        self.fecha_fin: date = fecha_fin
        self.precio_final: float = self.calcularPrecioFinal()

    def calcularPrecioFinal(self) -> float:
        dias = self.calcularDias()
        precio_final = dias * self.propiedad.precio_por_noche
        precio_final = self.aplicarReglasRangoFechas(precio_final)
        precio_final = self.aplicarReglasEstanciaProlongada(precio_final, dias)
        return precio_final

    def aplicarReglasRangoFechas(self, precio_final) -> float:   
        for regla in self.propiedad.reglas:
            if isinstance(regla, ReglaRangoFechas):
                dias = self.diasAplicables(regla.fecha_inicio, regla.fecha_fin)
                if dias > 0:
                    precio_ajustado = self.propiedad.precio_por_noche * (1 + (regla.porcentaje / 100))
                    precio_ajustado_dias = dias * precio_ajustado
                    precio_base_dias = dias * self.propiedad.precio_por_noche
                    precio_final += precio_ajustado_dias - precio_base_dias
        return precio_final

    def aplicarReglasEstanciaProlongada(self, precio_final, dias) -> float:
        for regla in self.propiedad.reglas:
            if isinstance(regla, ReglaEstanciaProlongada) and dias >= regla.dias_minimos:
                precio_final *= (1 - (regla.porcentaje / 100))
        return precio_final
        return precio_final

    def diasAplicables(self, fecha_inicio, fecha_fin) -> int:
        inicio_solapamiento = max(self.fecha_inicio, fecha_inicio)
        fin_solapamiento = min(self.fecha_fin, fecha_fin)
        if inicio_solapamiento < fin_solapamiento:
            return (fin_solapamiento - inicio_solapamiento).days
        return 0

    def calcularDias(self) -> int:
        return (self.fecha_fin - self.fecha_inicio).days
    
class Regla:

    def __init__(self, porcentaje):
        self.porcentaje: float = porcentaje

class ReglaRangoFechas(Regla):

    def __init__(self, porcentaje, fecha_inicio, fecha_fin):
        super().__init__(porcentaje)
        self.fecha_inicio: date = fecha_inicio
        self.fecha_fin: date = fecha_fin

    def solapaCon(self, otra_regla: ReglaRangoFechas) -> bool:
        return (self.fecha_inicio < otra_regla.fecha_fin and self.fecha_fin > otra_regla.fecha_inicio)

class ReglaEstanciaProlongada(Regla):

    def __init__(self, porcentaje, dias_minimos):
        super().__init__(porcentaje)
        self.dias_minimos: int = dias_minimos

class Sistema():

    def hacerReserva(self, usuario, propiedad, fecha_inicio, fecha_fin) -> Reserva:
        if not propiedad.propiedadDisponible(fecha_inicio, fecha_fin):
            print(f"La propiedad {propiedad.nombre} no está disponible en esas fechas.")
            return None

        reserva = Reserva(usuario, propiedad, fecha_inicio, fecha_fin)
        usuario.registrarReserva(reserva)
        propiedad.registrarReserva(reserva)
        return reserva


# Crear el sistema
sistema = Sistema()

# Crear usuarios
usuario1 = Usuario("Juan")
usuario2 = Usuario("María")

# Crear propiedades
propiedad1 = Propiedad("Apartamento en Madrid", 100)
propiedad2 = Propiedad("Casa en Barcelona", 150)

# Registrar propiedades a usuarios
usuario1.registrarPropiedad(propiedad1)
usuario2.registrarPropiedad(propiedad2)

# Crear reglas
regla1 = ReglaRangoFechas(20, date(2024, 8, 1), date(2024, 8, 31))  # 20% extra en agosto
regla2 = ReglaEstanciaProlongada(10, 7)  # 10% descuento si se queda más de 7 días

# Registrar reglas en propiedades
propiedad1.registrarRegla(regla1)
propiedad1.registrarRegla(regla2)
propiedad2.registrarRegla(regla2)

# Hacer reservas
reserva1 = sistema.hacerReserva(usuario1, propiedad1, date(2024, 8, 10), date(2024, 8, 17))  # 7 días en agosto
reserva2 = sistema.hacerReserva(usuario2, propiedad2, date(2024, 9, 1), date(2024, 9, 10))  # 9 días en septiembre

# Mostrar resultados
if reserva1:
    print(f"Reserva 1: {reserva1.usuario.nombre} reservó {reserva1.propiedad.nombre} por {reserva1.calcularDias()} días.")
    print(f"Precio final: {reserva1.precio_final:.2f}€\n")

if reserva2:
    print(f"Reserva 2: {reserva2.usuario.nombre} reservó {reserva2.propiedad.nombre} por {reserva2.calcularDias()} días.")
    print(f"Precio final: {reserva2.precio_final:.2f}€\n")




