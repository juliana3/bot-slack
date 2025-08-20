
from services.helpers_utils import convertir_a_int,  formatear_fecha_PF

def payloadALTA(datos):
    #arma el payload con los datos de la fila de la base de datos
    payload = {
        "first_name" : datos.get("nombre", ""),
        "last_name": datos.get("apellido", ""),
        "personal_email" : datos.get("email", ""),
        "dni" : convertir_a_int(datos.get("dni", "")),
        "direccion" : datos.get("domicilio", ""),
        "localidad" : datos.get("localidad", ""),
        "celular": convertir_a_int(datos.get("celular", "")),
        "date_of_birth" : formatear_fecha_PF(datos.get("fecha_nacimiento", "")),
        
    }
    
    if datos.get("tipo_contrato") == "rrdd" or datos.get("tipo_contrato") == "monotributo":
        if datos.get("localidad").lower() != "santa fe":
            #deposito y transferencia con los mismos datos
            payload.update({
                #deposito
                "banco_2" : datos.get("banco"),
                "nro_de_cuenta_3" : datos.get("cuenta"),
                "alias_3" : datos.get("alias"),
                "cbu_3": datos.get("cbu"),
                "cuil_3" : datos.get("cuil"),


                #transferencia
                "banco": datos.get("banco"),
                "nro_de_cuenta_2" : datos.get("cuenta"),
                "alias_2": datos.get("alias"),
                "cbu_2": datos.get("cbu"),
                "cuil_2" : datos.get("cuil"),

                "obra_social" : datos.get("obra_social", ""),
                "código_obra_social" : datos.get("codigo_afip", ""),
            })
        else:
            payload.update({
                #transferencia
                "banco": datos.get("banco"),
                "nro_de_cuenta_2" : datos.get("cuenta"),
                "alias_2": datos.get("alias"),
                "cbu_2": datos.get("cbu"),
                "cuil_2" : datos.get("cuil"),
                "obra_social" : datos.get("obra_social", ""),
                "código_obra_social" : datos.get("codigo_afip", ""),
            })
    else:
        payload.update({
            "banco_3" : datos.get("bank_name"),
            "dirección_del_banco_2": datos.get("bank_address"),
            "bank_swift_code_2" : datos.get("swift_code"),
            "account_holder_2": datos.get("account_holder"),
            "account_number_2": datos.get("account_number"),
            "routing_number_2": datos.get("routing_number"),
            "tipo_de_cuenta_2" : datos.get("tipo_cuenta"),
            "zip_code_2" : datos.get("zip"),
        })

    return payload

