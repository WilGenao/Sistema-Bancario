"""
Pruebas pytest para el sistema bancario (datos.py, operaciones.py).

Cómo ejecutar:
    pip install pytest
    pytest test_banco.py -v

Este archivo debe colocarse en la misma carpeta que datos.py, operaciones.py
y exceptios.py. Todas las pruebas usan archivos temporales (tmp_path) para
NO tocar tu datos_usuario_banco.json real.
"""

import json
import pytest

import datos
from operaciones import CuentaAhorro, CuentaCorriente, cargar_cuenta
from exceptios import (
    SaldoInsuficiente,
    MontoInvalido,
    UsuarioInvalido,
    TipoCuentaNovalido,
    ArchivoCorruptoError,
    UsuarioNoEncontrado,
    CuentaNoEncontrada,
)


# ---------------------------------------------------------------------------
# Fixtures comunes
# ---------------------------------------------------------------------------

@pytest.fixture
def archivo_temp(tmp_path):
    """Ruta a un json temporal que datos.py puede recibir por parámetro."""
    return str(tmp_path / "datos_test.json")


@pytest.fixture
def datos_base():
    """Dos usuarios de ejemplo: uno con Cuenta Ahorro, otro con Corriente."""
    return [
        {
            "id": "11111111",
            "usuario": "Usuario Uno",
            "cuentas": [
                {"id_cuenta": "22222222", "saldo": 1000, "tipo_cuenta": "Cuenta Ahorro"}
            ],
            "transacciones": [],
        },
        {
            "id": "33333333",
            "usuario": "Usuario Dos",
            "cuentas": [
                {"id_cuenta": "44444444", "saldo": 500, "tipo_cuenta": "Cuenta Corriente"}
            ],
            "transacciones": [],
        },
    ]


@pytest.fixture
def archivo_con_datos(archivo_temp, datos_base):
    """Escribe datos_base en archivo_temp y devuelve la ruta."""
    with open(archivo_temp, "w") as f:
        json.dump(datos_base, f)
    return archivo_temp


@pytest.fixture
def entorno_banco(tmp_path, monkeypatch, datos_base):
    """
    Varias funciones/métodos de operaciones.py (retirar, depositar,
    sincronizar, transferencias, intereses) usan 'datos_usuario_banco.json'
    como valor por defecto, SIN permitir pasar otra ruta. Por eso, para
    probarlas de forma aislada, nos movemos a un directorio temporal
    (chdir) y creamos ahí el archivo con ese nombre exacto.
    """
    monkeypatch.chdir(tmp_path)
    archivo = "datos_usuario_banco.json"
    with open(archivo, "w") as f:
        json.dump(datos_base, f)
    return archivo


# ---------------------------------------------------------------------------
# generar_id / generar_id_cuentas
# ---------------------------------------------------------------------------

class TestGeneracionIds:

    def test_generar_id_longitud_y_formato(self):
        nuevo_id = datos.generar_id(8, [])
        assert len(nuevo_id) == 8
        assert nuevo_id.isdigit()

    def test_generar_id_no_colisiona_con_existentes(self):
        existentes = [{"id": "12345678"}, {"id": "87654321"}]
        nuevo_id = datos.generar_id(8, existentes)
        assert nuevo_id not in [d["id"] for d in existentes]

    def test_generar_id_reintenta_si_hay_colision(self, monkeypatch):
        """Fuerza una colisión en el primer intento y valida que reintente."""
        existentes = [{"id": "11111111"}]
        secuencia = iter(list("11111111") + list("22222222"))
        monkeypatch.setattr(datos.secrets, "choice", lambda seq: next(secuencia))
        nuevo_id = datos.generar_id(8, existentes)
        assert nuevo_id == "22222222"

    def test_generar_id_cuentas_no_colisiona(self, datos_base):
        nuevo_id = datos.generar_id_cuentas(8, datos_base)
        ids_existentes = [c["id_cuenta"] for d in datos_base for c in d["cuentas"]]
        assert nuevo_id not in ids_existentes
        assert len(nuevo_id) == 8


# ---------------------------------------------------------------------------
# guardar_usuario / consultar_usuario
# ---------------------------------------------------------------------------

class TestPersistencia:

    def test_guardar_y_consultar_usuario(self, archivo_temp, datos_base):
        datos.guardar_usuario(datos_base, archivo_temp)
        resultado = datos.consultar_usuario(archivo_temp)
        assert resultado == datos_base

    def test_consultar_usuario_archivo_no_existe_retorna_lista_vacia(self, archivo_temp):
        resultado = datos.consultar_usuario(archivo_temp)  # el archivo no existe
        assert resultado == []

    def test_consultar_usuario_json_invalido_lanza_error(self, archivo_temp):
        with open(archivo_temp, "w") as f:
            f.write("{esto no es json valido")
        with pytest.raises(ArchivoCorruptoError):
            datos.consultar_usuario(archivo_temp)

    def test_guardar_usuario_no_serializable_lanza_typeerror(self, archivo_temp):
        with pytest.raises(TypeError):
            datos.guardar_usuario({"no_serializable": {1, 2, 3}}, archivo_temp)


# ---------------------------------------------------------------------------
# agregar_usuario
# ---------------------------------------------------------------------------

class TestAgregarUsuario:

    def test_agregar_usuario_exitoso(self, archivo_temp):
        datos.agregar_usuario("Juan Perez", 1000, "Cuenta Ahorro", archivo_temp)
        registrados = datos.consultar_usuario(archivo_temp)
        assert len(registrados) == 1
        assert registrados[0]["usuario"] == "Juan Perez"
        assert registrados[0]["cuentas"][0]["saldo"] == 1000
        assert registrados[0]["cuentas"][0]["tipo_cuenta"] == "Cuenta Ahorro"
        assert len(registrados[0]["id"]) == 8

    def test_agregar_usuario_nombre_muy_corto_lanza_error(self, archivo_temp):
        with pytest.raises(UsuarioInvalido):
            datos.agregar_usuario("   ", 100, "Cuenta Ahorro", archivo_temp)
    def test_agregar_usuario_nombre_corto_valido(self, archivo_temp):
        # Un nombre corto es válido siempre que no esté vacío ni sea solo espacios.
        datos.agregar_usuario("Ana", 100, "Cuenta Ahorro", archivo_temp)
        assert len(datos.consultar_usuario(archivo_temp)) == 1

    def test_agregar_usuario_saldo_negativo_lanza_error(self, archivo_temp):
        with pytest.raises(MontoInvalido):
            datos.agregar_usuario("Juan Perez", -1, "Cuenta Ahorro", archivo_temp)

    def test_agregar_usuario_saldo_cero_es_valido(self, archivo_temp):
        datos.agregar_usuario("Juan Perez", 0, "Cuenta Ahorro", archivo_temp)
        assert datos.consultar_usuario(archivo_temp)[0]["cuentas"][0]["saldo"] == 0

    def test_agregar_usuario_tipo_cuenta_invalido_lanza_error(self, archivo_temp):
        with pytest.raises(TipoCuentaNovalido):
            datos.agregar_usuario("Juan Perez", 100, "Cuenta Inventada", archivo_temp)


# ---------------------------------------------------------------------------
# agregar_cuenta_usuario
# ---------------------------------------------------------------------------

class TestAgregarCuentaUsuario:

    def test_agregar_cuenta_exitosa(self, archivo_con_datos):
        datos.agregar_cuenta_usuario("11111111", 300, "Cuenta Corriente", archivo_con_datos)
        registrados = datos.consultar_usuario(archivo_con_datos)
        usuario = next(d for d in registrados if d["id"] == "11111111")
        assert len(usuario["cuentas"]) == 2
        nueva = usuario["cuentas"][1]
        assert nueva["saldo"] == 300
        assert nueva["tipo_cuenta"] == "Cuenta Corriente"

    def test_agregar_cuenta_usuario_no_encontrado(self, archivo_con_datos):
        with pytest.raises(UsuarioNoEncontrado):
            datos.agregar_cuenta_usuario("99999999", 100, "Cuenta Ahorro", archivo_con_datos)

    def test_agregar_cuenta_saldo_negativo(self, archivo_con_datos):
        with pytest.raises(MontoInvalido):
            datos.agregar_cuenta_usuario("11111111", -50, "Cuenta Ahorro", archivo_con_datos)

    def test_agregar_cuenta_tipo_invalido(self, archivo_con_datos):
        with pytest.raises(TipoCuentaNovalido):
            datos.agregar_cuenta_usuario("11111111", 50, "Cuenta Rara", archivo_con_datos)


# ---------------------------------------------------------------------------
# transacciones / transacciones_debito_credito
# ---------------------------------------------------------------------------

class TestTransacciones:

    def test_transacciones_registra_en_ambos_usuarios(self, archivo_con_datos):
        datos.transacciones("11111111", "33333333", "44444444", "Transferencia", 100, archivo_con_datos)
        registrados = datos.consultar_usuario(archivo_con_datos)
        emisor = next(d for d in registrados if d["id"] == "11111111")
        receptor = next(d for d in registrados if d["id"] == "33333333")
        assert emisor["transacciones"][-1]["monto"] == [100, "-"]
        assert receptor["transacciones"][-1]["monto"] == [100, "+"]

    def test_transacciones_usuario_no_encontrado(self, archivo_con_datos):
        with pytest.raises(UsuarioNoEncontrado):
            datos.transacciones("99999999", "33333333", "44444444", "Transferencia", 100, archivo_con_datos)

    def test_transacciones_debito_credito_registra(self, archivo_con_datos):
        datos.transacciones_debito_credito("11111111", "22222222", "Deposito", 500, archivo_con_datos)
        registrados = datos.consultar_usuario(archivo_con_datos)
        usuario = next(d for d in registrados if d["id"] == "11111111")
        assert usuario["transacciones"][-1]["monto"] == 500
        assert usuario["transacciones"][-1]["accion"] == "Deposito"


# ---------------------------------------------------------------------------
# consultar_informaciones (salida impresa)
# ---------------------------------------------------------------------------

class TestConsultarInformaciones:

    def test_consultar_informaciones_imprime_datos_correctos(self, archivo_con_datos, capsys):
        datos.consultar_informaciones("11111111", "22222222", archivo_con_datos)
        salida = capsys.readouterr().out
        assert "Usuario Uno" in salida
        assert "22222222" in salida
        assert "1000" in salida


# ---------------------------------------------------------------------------
# cargar_cuenta
# ---------------------------------------------------------------------------

class TestCargarCuenta:

    def test_cargar_cuenta_ahorro(self, archivo_con_datos):
        cuenta = cargar_cuenta("11111111", "22222222", archivo_con_datos)
        assert isinstance(cuenta, CuentaAhorro)
        assert cuenta.saldo == 1000
        assert cuenta.nombre == "Usuario Uno"

    def test_cargar_cuenta_corriente(self, archivo_con_datos):
        cuenta = cargar_cuenta("33333333", "44444444", archivo_con_datos)
        assert isinstance(cuenta, CuentaCorriente)
        assert cuenta.saldo == 500

    def test_cargar_cuenta_usuario_no_encontrado(self, archivo_con_datos):
        with pytest.raises(UsuarioNoEncontrado):
            cargar_cuenta("99999999", "22222222", archivo_con_datos)

    def test_cargar_cuenta_cuenta_no_encontrada(self, archivo_con_datos):
        with pytest.raises(CuentaNoEncontrada):
            cargar_cuenta("11111111", "00000000", archivo_con_datos)


# ---------------------------------------------------------------------------
# CuentaAhorro: retirar / depositar / intereses
# ---------------------------------------------------------------------------

class TestCuentaAhorro:

    def test_retirar_exitoso_actualiza_saldo_y_persiste(self, entorno_banco):
        cuenta = cargar_cuenta("11111111", "22222222", entorno_banco)
        cuenta.retirar(400, "Retiro")
        assert cuenta.saldo == 600
        persistido = datos.consultar_usuario(entorno_banco)
        usuario = next(d for d in persistido if d["id"] == "11111111")
        assert usuario["cuentas"][0]["saldo"] == 600

    def test_retirar_monto_igual_al_saldo_deja_en_cero(self, entorno_banco):
        cuenta = cargar_cuenta("11111111", "22222222", entorno_banco)
        cuenta.retirar(1000, "Retiro")
        assert cuenta.saldo == 0

    def test_retirar_mas_del_saldo_lanza_error(self, entorno_banco):
        cuenta = cargar_cuenta("11111111", "22222222", entorno_banco)
        with pytest.raises(SaldoInsuficiente):
            cuenta.retirar(1001, "Retiro")

    def test_retirar_monto_cero_o_negativo_lanza_error(self, entorno_banco):
        cuenta = cargar_cuenta("11111111", "22222222", entorno_banco)
        with pytest.raises(MontoInvalido):
            cuenta.retirar(0, "Retiro")
        with pytest.raises(MontoInvalido):
            cuenta.retirar(-50, "Retiro")

    def test_depositar_exitoso(self, entorno_banco):
        cuenta = cargar_cuenta("11111111", "22222222", entorno_banco)
        cuenta.depositar(500, "Deposito")
        assert cuenta.saldo == 1500

    def test_depositar_monto_invalido_lanza_error(self, entorno_banco):
        cuenta = cargar_cuenta("11111111", "22222222", entorno_banco)
        with pytest.raises(MontoInvalido):
            cuenta.depositar(0, "Deposito")

    def test_intereses_aumenta_saldo_segun_tasa(self, entorno_banco):
        cuenta = cargar_cuenta("11111111", "22222222", entorno_banco)
        cuenta.intereses(referencia="22222222")
        assert cuenta.saldo == 1200  # 1000 + 20%


# ---------------------------------------------------------------------------
# CuentaCorriente: sobregiro
# ---------------------------------------------------------------------------

class TestCuentaCorriente:

    def test_retirar_dentro_del_sobregiro_permitido(self, entorno_banco):
        cuenta = cargar_cuenta("33333333", "44444444", entorno_banco)
        cuenta.retirar(1000, "Retiro")  # saldo 500 + 500 de sobregiro
        assert cuenta.saldo == -500

    def test_retirar_excede_sobregiro_lanza_error(self, entorno_banco):
        cuenta = cargar_cuenta("33333333", "44444444", entorno_banco)
        with pytest.raises(SaldoInsuficiente):
            cuenta.retirar(1001, "Retiro")


# ---------------------------------------------------------------------------
# Transferencias entre cuentas
# ---------------------------------------------------------------------------

class TestTransferencias:

    def test_transferencia_exitosa_actualiza_ambas_cuentas(self, entorno_banco):
        origen = cargar_cuenta("11111111", "22222222", entorno_banco)
        origen.transferencias("33333333", "44444444", 200, "Transferencia")
        assert origen.saldo == 800

        destino = cargar_cuenta("33333333", "44444444", entorno_banco)
        assert destino.saldo == 700  # 500 + 200

    def test_transferencia_beneficiario_no_encontrado_no_afecta_origen(self, entorno_banco):
        origen = cargar_cuenta("11111111", "22222222", entorno_banco)
        with pytest.raises(UsuarioNoEncontrado):
            origen.transferencias("99999999", "00000000", 200, "Transferencia")
        # como cargar_cuenta falla antes de retirar, el saldo no debe cambiar
        assert origen.saldo == 1000