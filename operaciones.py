from datos import consultar_usuario, guardar_usuario, agregar_usuario, consultar_informaciones,UsuarioNoEncontrado, transacciones_debito_credito, CuentaNoEncontrada
from abc import ABC,abstractmethod
from exceptios import SaldoInsuficiente, MontoInvalido, UsuarioInvalido, TipoCuentaNovalido


class Cuenta(ABC):

    def __init__(self, id_titular, id_cuenta, nombre, saldo):
        self.id_titular = id_titular
        self.nombre = nombre
        self.id_cuenta = id_cuenta
        self._saldo = saldo

    def sincronizar (self, archivo = "datos_usuario_banco.json" ):

        datos = consultar_usuario(archivo)

        for dato in datos:
            if dato['id'] == self.id_titular:
                for cuenta in dato['cuentas']:
                    if cuenta['id_cuenta'] == self.id_cuenta:
                        cuenta['saldo'] = self.saldo

        guardar_usuario(datos, archivo)

    @property
    def saldo (self):
        return self._saldo

    @saldo.setter
    def saldo (self, new_saldo):
        self._saldo = new_saldo
    
    @abstractmethod
    def retirar (self, monto, razon):
        pass

    @abstractmethod
    def depositar (self, monto, razon, referencia = None):

        if monto <= 0:
            raise MontoInvalido("No es permitido monto menor a 1 para depositos")
        self.saldo += monto
        referencia = referencia if referencia is not None else self.id_cuenta
        transacciones_debito_credito(self.id_titular, referencia, razon, (monto, "+"))
        self.sincronizar()

    @abstractmethod
    def transferencias (self, id_titular_beneficiario, id_cuenta,  monto, razon):

        cuenta_beneficiario = cargar_cuenta(id_titular_beneficiario, id_cuenta )
        self.retirar(monto, razon, referencia=id_cuenta)
        cuenta_beneficiario.depositar(monto, razon, referencia = self.id_cuenta)

    


class CuentaAhorro(Cuenta):

    tipo = "Cuenta Ahorro"

    def __init__(self,id_titular ,id_cuenta, nombre, saldo ):
        super().__init__(id_titular,id_cuenta , nombre, saldo)
        self.tasa_interes = 0.20

    def retirar (self, monto, razon, referencia = None):

        if monto <= 0:
            raise MontoInvalido("El monto a retirar debe ser mayor a 0")
        if monto > self.saldo:
            raise SaldoInsuficiente("El monto a retirar excede el saldo disponible")
        
        referencia = referencia if referencia is not None else self.id_cuenta

        self.saldo -= monto
        transacciones_debito_credito(self.id_titular, referencia , razon, (monto, "-"))
        self.sincronizar()

    def depositar(self, monto, razon, referencia=None):
        return super().depositar(monto, razon, referencia)

    
    def intereses (self, referencia, razon = "Intereses"):
        interes_neto = self.saldo * self.tasa_interes
        interes = self.saldo + interes_neto
        self.saldo = interes
        transacciones_debito_credito(self.id_titular, referencia , razon, (interes_neto, "+"))
        self.sincronizar()

    def transferencias(self, id_titular_beneficiario, id_cuenta, monto, razon):
        return super().transferencias(id_titular_beneficiario, id_cuenta, monto, razon)

    def consultar_cuenta (self, id_cuenta):
            consultar_informaciones(self.id_titular , id_cuenta)


class CuentaCorriente (Cuenta):

    tipo = "Cuenta Corriente"

    def __init__(self,id_titular,id_cuenta,nombre,saldo):
        super().__init__(id_titular, id_cuenta, nombre, saldo)


    def retirar (self, monto, razon, referencia = None):

        if monto <= 0:
            raise MontoInvalido("El monto a retirar debe ser mayor a 0")
        if monto > self.saldo + 500:
            raise SaldoInsuficiente("El monto a retirar excede el saldo disponible más el sobregiro permitido")

        referencia = referencia if referencia is not None else self.id_cuenta

        self.saldo -= monto
        transacciones_debito_credito(self.id_titular, referencia, razon, (monto, "-"))
        self.sincronizar()


    def depositar(self, monto, razon, referencia=None):
        return super().depositar(monto, razon, referencia)
    

    def transferencias(self, id_titular_beneficiario, id_cuenta, monto, razon):
        return super().transferencias(id_titular_beneficiario, id_cuenta, monto, razon)
    
    def consultar_cuenta (self, id_cuenta):
        consultar_informaciones(self.id_titular , id_cuenta)
        


def cargar_cuenta (id_usuario, id_cuenta, archivo = "datos_usuario_banco.json" ): 

    datos = consultar_usuario(archivo)

    id_usuario_encontrado = None

    for dato in datos:
        if dato['id'] == id_usuario:
            id_usuario_encontrado = dato
            break

    if id_usuario_encontrado is None:
        raise UsuarioNoEncontrado("Usuario no encontrado")
    
    cuenta_encontrada = None
    for cuenta in id_usuario_encontrado['cuentas']:
        if cuenta['id_cuenta'] == id_cuenta:
            cuenta_encontrada  =  cuenta
            break

    if cuenta_encontrada is None:
        raise CuentaNoEncontrada ("Cuenta no encontrada para ese usuario")

    cuenta_saldo = cuenta_encontrada['saldo']

    cuenta_cliente = None
    if cuenta_encontrada['tipo_cuenta'] == "Cuenta Ahorro":
        cuenta_cliente =  CuentaAhorro(id_usuario_encontrado['id'], cuenta_encontrada['id_cuenta'], id_usuario_encontrado['usuario'],cuenta_encontrada['saldo'], )


    if cuenta_encontrada['tipo_cuenta'] == "Cuenta Corriente":
        cuenta_cliente =  CuentaCorriente(id_usuario_encontrado['id'], cuenta_encontrada['id_cuenta'], id_usuario_encontrado['usuario'],cuenta_saldo)

    if cuenta_cliente is None:
       raise ValueError(f"Tipo de cuenta desconocido: {cuenta_encontrada['tipo_cuenta']}")

    return cuenta_cliente



