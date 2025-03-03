from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import timedelta, date
import datetime
from typing import List

class Tren:

    def __init__(self, numero_serie, modelo, marca, fecha_incorporacion, kilometraje_inicial):
        self.numero_serie: str = numero_serie
        self.modelo: Modelo = modelo
        self.marca: str = marca
        self.fecha_incorporacion: date = fecha_incorporacion
        self.kilometraje_inicial: float = kilometraje_inicial
        self.kilometraje_total: float = kilometraje_inicial
        self.viajes: List[Viaje] = []
        self.tareas_realizadas: List[TareaRealizada] = []

    def registrarViaje(self, viaje) -> None:
        self.viajes.append(viaje)
        self.actualizarKilometraje(viaje.km_recorridos)

    def registrarTareaRealizada(self, tarea_realiazda) -> None:
        self.tareas_realizadas.append(tarea_realiazda)

    def actualizarKilometraje(self, km) -> None:
        self.kilometraje_total += km

class Modelo:

    def __init__(self, nombre, plan_mantenimiento):
        self.nombre: str = nombre
        self.plan_mantenimiento: PlanMantenimiento = plan_mantenimiento

    def asignarPlanMantenimiento(self, plan_mantenimiento) -> PlanMantenimiento:
        self.plan_mantenimiento = plan_mantenimiento
        return plan_mantenimiento

class Viaje:

    def __init__(self, fecha_hora, km_recorridos):
         self.fecha_hora: datetime = fecha_hora
         self.km_recorridos: float = km_recorridos

class Repuesto:

    def __init__(self, nombre, precio):
        self.nombre: str = nombre
        self.precio: float = precio

class Tarea(ABC):
    
    def __init__(self, id, tiempo_estimado, precio_base, repuestos):
        self.id: str = id
        self.tiempo_estimado: timedelta = tiempo_estimado
        self.precio_base: float = precio_base
        self.repuestos: List[Repuesto] = repuestos

    def costeBase(self) -> float:
        return self.precio_base + sum(repuesto.precio for repuesto in self.repuestos)

    @abstractmethod
    def calcularCosteFinal(self, km_recorridos = None):
        pass

class TareaPeriodica(Tarea):

    def __init__(self, id, tiempo_estimado, precio_base, repuestos, periodicidad_tiempo):
        super().__init__(id, tiempo_estimado, precio_base, repuestos)
        self.periodicidad_tiempo: timedelta = periodicidad_tiempo

    def calcularCosteFinal(self, km_recorridos = None):
        return self.costeBase()

class TareaPorRodadura(Tarea):

    def __init__(self, id, tiempo_estimado, precio_base, repuestos, periodicidad_km):
        super().__init__(id, tiempo_estimado, precio_base, repuestos)
        self.periodicidad_km: float = periodicidad_km

    def calcularCosteFinal(self, km_recorridos) -> float:
        return self.costeBase() + (0.05 * km_recorridos)

class TareaRealizada():

    def __init__(self, tarea, fecha, descripcion):
        self.tarea: Tarea = tarea
        self.fecha: date = fecha
        self.descripcion: str = descripcion

class PlanMantenimiento():

    def __init__(self, version):
        self.version: str = version
        self.modelos_aplicables: List[Modelo] = []
        self.tareas: List[Tarea] = []

    def agregarModelo(self, modelo):
        self.modelos_aplicables.append(modelo)

    def agregarTarea(self, tarea):
        self.tareas.append(tarea)

class SistemaMantenimiento():

    def __init__(self):
        self.trenes: List[Tren] = []
        self.planes_mantenimiento: List[PlanMantenimiento] = []

    def registrarTren(self, tren) -> Tren:
        self.trenes.append(tren)
        return tren

    def registrarPlanMantenimiento(self, plan) -> PlanMantenimiento:
        self.planes_mantenimiento.append(plan)
        return plan

    def obtenerCostoTareasPorMes(self, tren, anio, mes) -> float:
        costo_total = 0
        for tarea_realizada in tren.tareas_realizadas:
            if tarea_realizada.fecha.year == anio and tarea_realizada.fecha.month == mes:
                costo_total += tarea_realizada.tarea.calcularCosteFinal(tren.kilometraje_total)
        return costo_total

    def obtenerPlanesMantenimientoMasCostosos(self) -> List[PlanMantenimiento]:
        planes_ordenados = sorted(
            self.planes_mantenimiento,
            key=lambda plan: sum(tarea.costeBase() for tarea in plan.tareas),
            reverse=True
        )[:5]
        
        print("Planes de mantenimiento más costosos:")
        for plan in planes_ordenados:
            costo_total = sum(tarea.costeBase() for tarea in plan.tareas)
            print(f"Versión: {plan.version}, Costo Total: {costo_total}")

sistema = SistemaMantenimiento()

# Crear modelos de trenes
modelo_A = Modelo("Modelo A", None)
modelo_B = Modelo("Modelo B", None)

# Crear planes de mantenimiento y asignarlos a los modelos
plan_A = PlanMantenimiento("V1.0")
plan_B = PlanMantenimiento("V2.0")

sistema.registrarPlanMantenimiento(plan_A)
sistema.registrarPlanMantenimiento(plan_B)

plan_A.agregarModelo(modelo_A)
plan_B.agregarModelo(modelo_B)

modelo_A.asignarPlanMantenimiento(plan_A)
modelo_B.asignarPlanMantenimiento(plan_B)

# Crear repuestos
repuesto1 = Repuesto("Filtro de aire", 50.0)
repuesto2 = Repuesto("Aceite lubricante", 30.0)

# Agregar tareas periódicas y por rodadura a los planes de mantenimiento
tarea1 = TareaPeriodica("TP-001", timedelta(hours=2), 200.0, [repuesto1], timedelta(days=30))
tarea2 = TareaPorRodadura("TR-001", timedelta(hours=3), 150.0, [repuesto2], 10000)

plan_A.agregarTarea(tarea1)
plan_A.agregarTarea(tarea2)

# Registrar trenes en el sistema
tren_1 = Tren("12345A", modelo_A, "MarcaX", date(2022, 5, 10), 5000)
tren_2 = Tren("67890B", modelo_B, "MarcaY", date(2021, 8, 15), 20000)

sistema.registrarTren(tren_1)
sistema.registrarTren(tren_2)

# Registrar viajes de trenes
viaje_1 = Viaje(datetime.datetime(2024, 2, 10, 10, 0), 1200)
viaje_2 = Viaje(datetime.datetime(2024, 2, 15, 14, 30), 800)

tren_1.registrarViaje(viaje_1)
tren_1.registrarViaje(viaje_2)

# Registrar tareas realizadas en un tren
tarea_realizada_1 = TareaRealizada(tarea1, date(2024, 2, 28), "Cambio de filtro de aire")
tarea_realizada_2 = TareaRealizada(tarea2, date(2024, 2, 28), "Cambio de aceite por rodadura")

tren_1.registrarTareaRealizada(tarea_realizada_1)
tren_1.registrarTareaRealizada(tarea_realizada_2)

# Obtener costo de tareas realizadas en febrero 2024
costo_febrero = sistema.obtenerCostoTareasPorMes(tren_1, 2024, 2)
print(f"\n💰 Costo total de tareas realizadas en febrero 2024 para el tren {tren_1.numero_serie}: ${costo_febrero:.2f}\n")

# Obtener los 5 planes de mantenimiento más costosos
sistema.obtenerPlanesMantenimientoMasCostosos()