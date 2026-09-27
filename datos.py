from exceptios import ArchivoCorruptoError, UsuarioNoEncontrado, CuentaNoEncontrada, MontoInvalido, UsuarioInvalido, TipoCuentaNovalido
import json
import logging
import secrets
import string
import time


def generar_id(cantidad_d, datos_existentes):

    cantidad = cantidad_d
    ids_existentes = [d['id'] for d in datos_existentes]
    numeros = string.digits
    nuevo_id = ''.join(secrets.choice(numeros) for _ in range(cantidad_d))

    while nuevo_id in ids_existentes:
        nuevo_id = ''.join(secrets.choice(numeros) for _ in range(cantidad))
    return nuevo_id

def generar_id_cuentas(cantidad_d, datos_existentes):

    cantidad = cantidad_d
    ids_existentes = [n['id_cuenta'] for d in datos_existentes for n in d['cuentas']]
    numeros = string.digits
    nuevo_id = ''.join(secrets.choice(numeros) for _ in range(cantidad_d))

    while nuevo_id in ids_existentes:
        nuevo_id = ''.join(secrets.choice(numeros) for _ in range(cantidad))
    return  nuevo_id

def guardar_usuario (datos, archivo ='datos_usuario_banco.json'):

    try:
        with open (archivo, 'w') as f:
            json.dump(datos, f,indent=4, ensure_ascii=False)
    except TypeError:
        logging.error("No se pudo Serializar el Archivo json")
        raise

def consultar_usuario (archivo = 'datos_usuario_banco.json'):

    try:
        with open (archivo , 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f'Archivo {archivo} no encontrado, creando Archivo Nuevo')
        return []
    except json.JSONDecodeError:
        logging.warning(f"Archivo {archivo} tiene JSON inválido")
        raise ArchivoCorruptoError(f"No se pudo leer {archivo}: formato inválido")

def agregar_usuario (usuario, saldo, tipo_cuenta, archivo = 'datos_usuario_banco.json'):

    datos = consultar_usuario(archivo)
    nuevo_id = generar_id(8 , datos)
    nuevo_id_cuenta = generar_id_cuentas(8 , datos)

    if usuario.strip() == "":
        raise UsuarioInvalido("Usuario no Valido")

    if saldo < 0 :
        raise MontoInvalido ("Saldo debe ser igual o Mayor a 0")

    if tipo_cuenta not in ["Cuenta Ahorro", "Cuenta Corriente"]:
        raise TipoCuentaNovalido("Tipo de Cuenta no valida")
    

    datos.append({'id' : nuevo_id , 'usuario' : usuario, 'cuentas' : [{'id_cuenta' : nuevo_id_cuenta, 'saldo': saldo, 'tipo_cuenta' : tipo_cuenta}], 'transacciones' : []})

    guardar_usuario (datos, archivo)

def agregar_cuenta_usuario (id_usuario, saldo, tipo_cuenta, archivo = "datos_usuario_banco.json"):

    datos = consultar_usuario(archivo)
    nuevo_id_cuenta = generar_id_cuentas(8 , datos)
    
    if saldo < 0 :
        raise MontoInvalido ("Saldo debe ser igual o Mayor a 0")
    
    if tipo_cuenta not in ["Cuenta Ahorro", "Cuenta Corriente"]:
        raise TipoCuentaNovalido("Tipo de Cuenta no valida")

    if id_usuario not in [d['id'] for d in datos]:
        raise UsuarioNoEncontrado("Usuario no encontrado")

    for usuarios in datos:
        if usuarios['id'] == id_usuario:
            usuarios['cuentas'].append({'id_cuenta' : nuevo_id_cuenta, 'saldo': saldo, 'tipo_cuenta' : tipo_cuenta})
        logging.info("Cuenta nueva Agregada Correctamente")
        guardar_usuario (datos, archivo)

def transacciones (id_usuario, id_usuario_beneficiario, id_cuenta_beneficiario,  accion , monto, archivo = "datos_usuario_banco.json" ):

    datos = consultar_usuario(archivo)
    tiempo = time.localtime()
    fecha_hoy = time.strftime("%Y-%m-%d %H:%M:%S", tiempo)


    if id_usuario not in [d['id'] for d in datos]:
        raise UsuarioNoEncontrado("Usuario no encontrado")

    for usuarios in datos:
        if usuarios['id'] == id_usuario:
            usuarios['transacciones'].append({'id' : id_usuario  , 'accion': accion, 'id_2': id_cuenta_beneficiario , 'monto' : (monto, "-"), 'fecha' : fecha_hoy})

    for usuarios in datos:
        if usuarios['id'] == id_usuario_beneficiario:
            usuarios['transacciones'].append({'id' : id_cuenta_beneficiario  , 'accion': accion, 'id_2': id_usuario , 'monto' : (monto, "+"), 'fecha' : fecha_hoy})
    guardar_usuario (datos, archivo)

def transacciones_debito_credito (id_usuario, id_cuenta_beneficiario,  accion , monto, archivo = "datos_usuario_banco.json" ):

    datos = consultar_usuario(archivo)
    tiempo = time.localtime()
    fecha_hoy = time.strftime("%Y-%m-%d %H:%M:%S", tiempo)


    if id_usuario not in [d['id'] for d in datos]:
        raise UsuarioNoEncontrado("Usuario no encontrado")

    for usuarios in datos:
        if usuarios['id'] == id_usuario:
            usuarios['transacciones'].append({'id' : id_usuario  , 'accion': accion, 'id_2': id_cuenta_beneficiario , 'monto' : monto, 'fecha' : fecha_hoy})

    guardar_usuario (datos, archivo)

def consultar_informaciones (id_usuario, id_cuenta, archivo = "datos_usuario_banco.json"):

    datos = consultar_usuario(archivo)


    for dato in datos:
        if dato['id'] == id_usuario:
            print (f"\nTitular: {dato['usuario']}\n")

            for cuenta in dato['cuentas']:
                if cuenta['id_cuenta'] == id_cuenta:
                    print(f"Numero de cuenta: {cuenta['id_cuenta']}\nSaldo: {cuenta['saldo']}\nTipo de cuenta: {cuenta['tipo_cuenta']}\n")
            print("Transacciones: \n")
            for trans in dato['transacciones']:
                print(f"{trans['id']}\nAccion: {trans['accion']}\n{trans['id_2']}\nMonto: {trans['monto']}\n fecha: {trans['fecha']}\n")





