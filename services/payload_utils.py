

def detectar_entidad(datos):
    if datos.get("CBU"):
        return "nacional"
    elif datos.get("Bank Swift Code"):
        return "extranjera"
    else:
        return "desconocida"
    

def payloadALTA(datos):

    payload = {
        "first_name" : datos.get("nombre"),
        "last_name": datos.get("apellido"),
        "email" : datos.get("email"), #o personal_email
        "dni" : datos.get("dni"),
        "direccion" : datos.get("domicilio"),
        "localidad" : datos.get("localidad"),
        "celular": datos.get("celular"),
        "date_of_birth" : datos.get("fecha_de_nacimiento"),
        "obra_social" : datos.get("obra_social"),
        "código_obra_social" : datos.get("codigo_OS")

    }
    
    if detectar_entidad(datos) == "nacional":
        payload.update({
            #datos bancarios nacionales
        })
    else:
        payload.update({
            "banco_3" : datos.get("bank_name"),
            "dirección_del_banco_2": datos.get("bank_address"),
            "bank_swift_code_2" : datos.get("bank_swift_code"),
            "account_holder_2": datos.get("account_holder"),
            "routing_number_2": datos.get("routing_number"),
            "tipo_de_cuenta_2" : datos.get("tipo_de_cuenta"),
            "zip_code_2" : datos.get("zip_code"),
        })

    return payload


