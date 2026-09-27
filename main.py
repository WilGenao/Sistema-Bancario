from datos import consultar_usuario, UsuarioNoEncontrado, agregar_cuenta_usuario, agregar_usuario, consultar_informaciones, CuentaNoEncontrada
from operaciones import cargar_cuenta, SaldoInsuficiente
from exceptios import MontoInvalido, TipoCuentaNovalido


def menu():
    print("\n=== BANCO GENAO ===")
    print("1. Consultar saldo")
    print("2. Depositar")
    print("3. Retirar")
    print("4. Transferencia")
    print("5. Crear Usuario")
    print("6. Crear Cuenta Nueva Usuario")
    print("7. Consultar Informaciones")
    print("8. Salir")
    return input("Elige una opción: ")


while True:

    razon = ""

    opcion = menu()

    if opcion == '5':
        try:
            nombre = input("Digite el nombre del nuevo usuario: ")
            saldo = int (input("Digite el saldo a depositar: "))
            tipo_cuenta = input("Digite el tipo de cuenta: [Ahorro (1) , Corriente (2)] ")
            if tipo_cuenta == '1':
                tipo_cuenta = "Cuenta Ahorro"
            elif tipo_cuenta == '2':
                tipo_cuenta = "Cuenta Corriente"
            agregar_usuario(nombre, saldo, tipo_cuenta)
        except ValueError as e:
            print(f"Datos inválidos: {e}\n")
        except SaldoInsuficiente as e:
            print(f"Operación no permitida: {e}\n")
        break

    if opcion == '6':
        try:
            id_usuario = input("Digite el código del usuario: ")
            saldo = int(input("Digite el saldo inicial de la nueva cuenta: "))
            tipo_cuenta = input("Digite el tipo de cuenta: [Ahorro (1), Corriente (2)] ")
            if tipo_cuenta == '1':
                tipo_cuenta = "Cuenta Ahorro"
            elif tipo_cuenta == '2':
                tipo_cuenta = "Cuenta Corriente"
            agregar_cuenta_usuario(id_usuario, saldo, tipo_cuenta)
            print("Cuenta creada correctamente.\n")
        except ValueError as e:
            print(f"Datos inválidos: {e}\n")
        except (UsuarioNoEncontrado, MontoInvalido, TipoCuentaNovalido) as e:
            print(f"No se pudo crear la cuenta: {e}\n")
        continue

    if opcion == '8':
        print("Gracias por preferirnos!\n")
        break

    

    id_usuario = input('Digite tu codigo de Usuario: ')
    datos = consultar_usuario()

    if id_usuario not in [d['id'] for d in datos]:
        print("Usuario no identificado")
        break

    num_cuenta = input("Digite el numero de Cuenta: ")

    try:
        cliente = cargar_cuenta(id_usuario, num_cuenta)
    except (UsuarioNoEncontrado, ValueError) as e:
        print(f"No se pudo cargar la cuenta: {e}\n")
        continue

    print(f"Bienvenido {cliente.nombre}.")

    

    if opcion == '1':
        print(f"Saldo disponible es de {cliente.saldo}\n")
        print("Gracias por preferirnos!\n")

    elif opcion == '2':
        try:
            cantidad = int(input("Cantidad a Depositar: "))
            cliente.depositar(cantidad, razon="Deposito")
            print(f'Nuevo saldo es de {cliente.saldo}\n')
            print("Gracias por preferirnos!\n")
        except ValueError as e:
            print(f"Cantidad inválida: {e}\n")
        except SaldoInsuficiente as e:
            print(f"Operación no permitida: {e}\n")

    elif opcion == '3':
        try:
            cantidad = int(input("Cantidad a Retirar: "))
            cliente.retirar(cantidad, razon="Retiro")
            print(f'Nuevo saldo es de {cliente.saldo}\n')
            print("Gracias por preferirnos!\n")
        except ValueError as e:
            print(f"Cantidad inválida: {e}\n")
        except SaldoInsuficiente as e:
            print(f"Operación no permitida: {e}\n")

    elif opcion == '4':
        try:
            id_beneficiario = input("Numero de identificacion beneficiario: ")
            id_cuenta = input("Numero de Cuenta beneficiario: ")
            cantidad = int(input("Cantidad a transferir: "))
            cliente.transferencias(id_beneficiario, id_cuenta, cantidad, razon="Transferencia")
            print(f'Nuevo saldo es de {cliente.saldo}\n')
            print("Gracias por preferirnos!\n")
        except ValueError as e:
            print(f"Datos inválidos: {e}\n")
        except SaldoInsuficiente as e:
            print(f"Operación no permitida: {e}\n")
        except UsuarioNoEncontrado as e:
            print(f"Beneficiario no encontrado: {e}\n")


    elif opcion == '7':
        try:
            id_usuario = input("Digite el id del usuario: ")
            id_cuenta = input("Numero de Cuenta beneficiario: ")
            consultar_informaciones(id_usuario,id_cuenta)
        except UsuarioNoEncontrado as e:
            print(f"Usuario no encontrado: {e}\n")
        except CuentaNoEncontrada as e:
            print(f"Cuenta no encontrada: {e}\n")
    else:
        print("Opción inválida, intenta de nuevo.\n")