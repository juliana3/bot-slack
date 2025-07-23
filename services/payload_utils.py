

def detectar_entidad(fila_data, columnas):
    valor = fila_data[columnas["CBU"] -1] if "CBU" in columnas and columnas["CBU"] -1 < len(fila_data) else ""
    if valor and valor.strip() != "":
        return "nacional"
    else:
        return "extranjera"


def payloadALTA(nro_fila, columnas, fila_data):
    #comprobacion para saber si la columna existe y si el indice es valido
    get_val = lambda col_name: fila_data[columnas[col_name] - 1] if col_name in columnas and columnas[col_name] - 1 < len(fila_data) else ""

    #arma el payload con los datos de la fila
    payload = {
        "first_name" : get_val("Nombre"),
        "last_name": get_val("Apellido"),
        "personal_email" : get_val("Email"), #o personal_email
        "dni" : get_val("DNI"),
        "direccion" : get_val("Domicilio Real"),
        "localidad" : get_val("Localidad"),
        "celular": get_val("Celular"),
        "date_of_birth" : get_val("Fecha de Nacimiento"),
        "obra_social" : get_val("Nombre de la Obra Social o Prepaga"),
        "código_obra_social" : get_val("Código de Identificación"),
    }
    
    if detectar_entidad(fila_data, columnas) == "nacional":
        payload.update({
            "banco_1" : get_val("Banco"), #y todos los demas
        })
    else:
        payload.update({
            "banco_3" : get_val("Bank Name"),
            "dirección_del_banco_2": get_val("Bank Address"),
            "bank_swift_code_2" : get_val("Bank Swift Code"),
            "account_holder_2": get_val("Account Holder"),
            "routing_number_2": get_val("Routing Number"),
            "tipo_de_cuenta_2" : get_val("Tipo de Cuenta"),
            "zip_code_2" : get_val("Zip Code"),
        })

    return payload

def payloadPDF(nro_fila, columnas, fila_data):
    #comprobacion para saber si la columna existe y si el indice es valido
    get_val = lambda col_name: fila_data[columnas[col_name] - 1] if col_name in columnas and columnas[col_name] - 1 < len(fila_data) else ""

    payload = {
        "fila" : nro_fila,
        "nombre" : get_val("Nombre"),
        "apellido" : get_val("Apellido"),
        "email" : get_val("Email"),
        "dni_f" : get_val("DNI frente"),
        "dni_d" : get_val("DNI dorso"),
        "employee_id" : get_val("ID PF")
    }

    return payload
