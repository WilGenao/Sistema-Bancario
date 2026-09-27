# Sistema Bancario en Python 🏦

Este es un proyecto que desarrollé como parte de mi aprendizaje de Python. La idea fue poner en práctica varios de los conceptos que había estado estudiando por separado y utilizarlos juntos en un proyecto más completo.

El programa simula algunas operaciones básicas de un sistema bancario. Permite crear usuarios y cuentas, realizar depósitos, retiros y transferencias, consultar información y mantener un historial de las transacciones.

## Funcionalidades

- Crear usuarios
- Crear nuevas cuentas para usuarios existentes
- Cuenta de ahorro y cuenta corriente
- Depósitos y retiros
- Transferencias entre cuentas
- Consulta de saldo
- Historial de transacciones
- Intereses para cuentas de ahorro
- Sobregiro de hasta RD$500 para cuentas corrientes
- Persistencia de los datos utilizando JSON
- Validación de datos y manejo de errores

## ¿Qué practiqué con este proyecto?

El objetivo principal del proyecto fue practicar Programación Orientada a Objetos en Python.

Durante el desarrollo trabajé con:

- Clases y objetos
- Herencia
- Encapsulación
- Abstracción
- Polimorfismo
- `super()`
- `@property`
- Excepciones personalizadas
- Manejo de archivos JSON
- Separación del código en diferentes módulos
- Testing con Pytest

Una de las partes en las que más trabajé fue en las pruebas. Actualmente el proyecto cuenta con **37 tests**, donde pruebo diferentes comportamientos del sistema como depósitos, retiros, transferencias, intereses, sobregiros, creación de usuarios y manejo de errores.

## Estructura

```text
├── main.py
├── operaciones.py
├── datos.py
├── exceptios.py
├── datos_usuario_banco.json
├── test_sistema.py
├── requirements.txt
└── README.md
```

`main.py` contiene el menú desde donde se utiliza el programa.

`operaciones.py` contiene las clases `Cuenta`, `CuentaAhorro` y `CuentaCorriente`, además de la lógica de las principales operaciones.

`datos.py` se encarga de trabajar con el archivo JSON, crear usuarios y cuentas, generar IDs y registrar las transacciones.

`exceptios.py` contiene las excepciones personalizadas del proyecto.

`test_sistema.py` contiene las pruebas realizadas con Pytest.

## Instalación

Clona el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
```

Entra a la carpeta e instala las dependencias:

```bash
pip install -r requirements.txt
```

Luego puedes ejecutar el programa con:

```bash
python main.py
```

Para ejecutar las pruebas:

```bash
pytest -v
```

## Algunas cosas que aprendí

Además de practicar POO, este proyecto me ayudó a entender mejor cómo organizar un programa cuando empieza a crecer.

También aprendí bastante trabajando con Pytest. Al principio veía los tests simplemente como una forma de comprobar si el código funcionaba, pero durante el proyecto entendí que son especialmente útiles para asegurar que cambios futuros no rompan comportamientos que ya funcionaban.

Todavía hay muchas cosas que podría mejorar en el proyecto, pero decidí mantenerlo como parte de mi progreso y continuar avanzando con mi roadmap de aprendizaje.

## Autor

**Wilmer Genao**

Estudiante de Ingeniería en Sistemas, actualmente fortaleciendo mis conocimientos de Python y continuando mi formación en desarrollo de software, análisis de datos e inteligencia artificial.