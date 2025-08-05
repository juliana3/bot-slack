
def payloadALTA(datos):
    #arma el payload con los datos de la fila
    payload = {
        "first_name" : datos.get("nombre", ""),
        "last_name": datos.get("apellido", ""),
        "personal_email" : datos.get("email", ""),
        "dni" : datos.get("dni", ""),
        "direccion" : datos.get("domicilio", ""),
        "localidad" : datos.get("localidad", ""),
        "celular": datos.get("celular", ""),
        "date_of_birth" : datos.get("fecha_nacimiento", ""),
        "obra_social" : datos.get("obra_social", ""),
        "código_obra_social" : datos.get("codigo_afip", ""),
    }
    
    if datos.get("tipo_contrato") == "Relación de Dependencia" or datos.get("tipo_contrato") == "Monotributo":
        if datos.get("localidad").lower() != "santa fe":
            #deposito y transferencia con los mismos datos
            payload.update({
                #deposito
                "banco_2" : datos.get("banco"),
                "nro_de_cuenta_3" : datos.get("numero_cuenta"),
                "alias_3" : datos.get("alias"),
                "cbu_3": datos.get("cbu"),
                "alias_3" : datos.get("cuil"),


                #transferencia
                "banco": datos.get("banco"),
                "nro_de_cuenta_2" : datos.get("numero_cuenta"),
                "alias_2": datos.get("alias"),
                "cbu_2": datos.get("cbu"),
                "cuil_2" : datos.get("cuil"),
            })
        else:
            payload.update({
                #transferencia
                "banco": datos.get("banco"),
                "nro_de_cuenta_2" : datos.get("numero_cuenta"),
                "alias_2": datos.get("alias"),
                "cbu_2": datos.get("cbu"),
                "cuil_2" : datos.get("cuil"),
            })
    else:
        payload.update({
            "banco_3" : datos.get("bank_name"),
            "dirección_del_banco_2": datos.get("bank_address"),
            "bank_swift_code_2" : datos.get("swift_code"),
            "account_holder_2": datos.get("account_holder"),
            "routing_number_2": datos.get("routing_number"),
            "tipo_de_cuenta_2" : datos.get("tipo_cuenta"),
            "zip_code_2" : datos.get("zip_code"),
        })

    return payload


#esta me parece que no funciona
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
