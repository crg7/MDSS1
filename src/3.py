from __future__ import annotations
from ast import Set
from typing import List
from abc import ABC, abstractmethod
from datetime import date

class Usuario: 
    def __init__(self, nombre, email, contraseña):
        self.nombre: str = nombre
        self.email: str = email
        self.contraseña: str = contraseña
        self.raiz: Directorio = Directorio("Home", self)

    def crearDirectorio(self, nombre, directorio_destino) -> Directorio:
        if not directorio_destino.esPropietario(self):
            print(f"Error: Usuario '{self.nombre}' no es propietario de '{directorio_destino.nombre}'.")
            return None

        nuevo_directorio = Directorio(nombre, self)
        nuevo_directorio = Directorio(nombre, self)
        directorio_destino.agregar(nuevo_directorio)
        return nuevo_directorio

    def crearArchivo(self, nombre, peso, directorio_destino) -> Archivo:
        if not directorio_destino.esPropietario(self):
            print(f"Error: Usuario '{self.nombre}' no es propietario de '{directorio_destino.nombre}'.")
            return None

        nuevo_archivo = Archivo(nombre, self, date.today(), peso)
        directorio_destino.agregar(nuevo_archivo)
        return nuevo_archivo

    def compartir(self, componente, usuario) -> None:
        if componente.esPropietario(self):
            if not componente.esPublico():
                componente.darPermisos(usuario)
            else:
                print("Error: El componente ya es Publico")
        else:
            print(f"Error: El usuario {self.nombre} no tiene permisos para compartir el archivo {componente.nombre}") 

    def hacerPublico(self, componente, fecha_limite) -> None:
        if componente.esPropietario(self):
            componente.hacerPublico(fecha_limite)
        else: 
            print(f"Error: El usuario {self.nombre} no tiene permisos para hacer publico el archivo {componente.nombre}") 
            
    def calcularPeso(self) -> float:
        return self.raiz.calcularPeso()

    def contarArchivos(self) -> int: 
        return self.raiz.contarArchivos()
    
    def mostrar(self) -> str:
        return self.raiz.mostrar()

    def __repr__(self) -> str:
        return self.mostrar()

class Componente(ABC):

    def __init__(self, nombre, propietario: Usuario):
        self.nombre = nombre
        self.es_publico: bool = False
        self.fecha_limite: date | None = None
        self.propietario: Usuario = propietario
        self.usuarios: Set[Usuario] = set()

    @abstractmethod
    def calcularPeso(self) -> float:    
        pass
    
    @abstractmethod
    def contarArchivos(self) -> int:
        pass

    @abstractmethod
    def mostrar(self, nivel = 0) -> str:
        pass

    def darPermisos(self, usuario) -> None:
        self.usuarios.add(usuario)

    def quitarPermisos(self, usuario) -> None:
        self.usuarios.discard(usuario)

    def esPropietario(self, usuario) -> bool:
        return usuario == self.propietario
        
    def esPublico(self) -> bool:
        return self.es_publico

    def hacerPublico(self, fecha_limite) -> None:
        self.es_publico = True
        self.fecha_limite = fecha_limite

    def hacerPrivado(self) -> None:
        self.es_publico = False
        self.fecha_limite = None

    def puedeAcceder(self, usuario) -> bool:
        if self.es_publico and (self.fecha_limite is None or self.fecha_limite >= date.today()):
            return True
        return usuario in self.usuarios or usuario == self.propietario

    def __repr__(self) -> str:
        return self.mostrar()

class Archivo(Componente):

    def __init__(self, nombre, propietario, fecha_creacion, peso):
        super().__init__(nombre, propietario)
        self.fecha_creacion: date = fecha_creacion
        self.fecha_modificacion: date = fecha_creacion
        self.peso: float = peso

    def calcularPeso(self) -> float:
        return self.peso
    
    def contarArchivos(self) -> int:
        return 1

    def modificar(self, fecha_modificacion, peso) -> None:
        self.fecha_modificacion = fecha_modificacion
        self.peso = peso

    def mostrar(self, nivel = 0) -> str:
        return "   " * nivel + f"📄 {self.nombre} | {self.peso} KB | {self.fecha_creacion} | {self.fecha_modificacion}"

class Directorio(Componente):

    def __init__(self, nombre, propietario):
        super().__init__(nombre, propietario)
        self.contenidos: List[Componente] = []
       
    def agregar(self, componente) -> None:
        self.contenidos.append(componente)

    def eliminar(self, componente) -> None:
        if componente in self.contenidos:
            self.contenidos.remove(componente)
        else:
             print(f"Error: El componente {componente.nombre} no se encuentra en {self.nombre}.") 

    def calcularPeso(self) -> float:
        return sum(elemento.calcularPeso() for elemento in self.contenidos)
    
    def contarArchivos(self) -> int:
        return sum(elemento.contarArchivos() for elemento in self.contenidos)
  
    def mostrar(self, nivel = 0) -> str:
        resultado = "   " * nivel + f"📁 {self.nombre}/"
        for contenido in self.contenidos:
            resultado += "\n" + contenido.mostrar(nivel + 1)
        return resultado
    
def puedeAcceder(usuario, archivo) -> bool:
    return archivo.puedeAcceder(usuario)

def contarArchivos(usuario) -> int:
    return usuario.contarArchivos()

def calcularPeso(usuario) -> float:
    return usuario.calcularPeso()

# Crear usuarios
u1 = Usuario("A", "a@example.com", "claveA")
u2 = Usuario("B", "b@example.com", "claveB")

# Crear directorios para el usuario A
d1 = u1.crearDirectorio("Documentos A", u1.raiz)
d2 = u1.crearDirectorio("Proyectos A", u1.raiz)

# Crear archivos dentro de los directorios de A
a1 = u1.crearArchivo("archivo1.txt", 10, d1)
a1 = u1.crearArchivo("archivo1.txt", 10, d1)
a2 = u1.crearArchivo("archivo2.txt", 20, d1)
a3 = u1.crearArchivo("archivo3.txt", 30, d2)

# Crear directorios para el usuario B
d3 = u2.crearDirectorio("Documentos B", u2.raiz)

# Crear archivo dentro de los directorios de B
a4 = u2.crearArchivo("archivo4.txt", 15, d3)

# Mostrar información de los usuarios
print(f"Usuario {u1.nombre}:\n {u1}")
print(f"Usuario {u2.nombre}:\n {u2}")

# Calcular y mostrar el total de archivos de cada usuario
print(f"Cantidad de archivos de {u1.nombre}: {contarArchivos(u1)}")
print(f"Cantidad de archivos de {u2.nombre}: {contarArchivos(u2)}")

# Calcular y mostrar el peso total de los archivos de cada usuario
print(f"Peso total de archivos de {u1.nombre}: {calcularPeso(u1)} KB")
print(f"Peso total de archivos de {u2.nombre}: {calcularPeso(u2)} KB")

# Probar compartir archivos
print("\n--- Intentando compartir archivos ---")
u1.compartir(a1, u2)  # A intenta compartir a1 con B

if puedeAcceder(u2, a1):
    print(f"El usuario {u2.nombre} puede acceder al archivo {a1.nombre}.")
else:
    print(f"El usuario {u2.nombre} NO puede acceder al archivo {a1.nombre}.")

# Hacer un archivo público
print("\n--- Haciendo público un archivo ---")
u1.hacerPublico(a2, date(2025, 12, 31))  

if puedeAcceder(u2, a2):
    print(f"El usuario {u2.nombre} puede acceder al archivo {a2.nombre}.")
else:
    print(f"El usuario {u2.nombre} NO puede acceder al archivo {a2.nombre}.")

print("\n---  Accediendo a un archivo privado ---")
if puedeAcceder(u2, a3):
    print(f"El usuario {u2.nombre} puede acceder al archivo {a3.nombre}.")
else:
    print(f"El usuario {u2.nombre} NO puede acceder al archivo {a3.nombre}.")


