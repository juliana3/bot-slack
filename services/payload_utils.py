
from services.helpers_utils import convertir_a_int,  formatear_fecha_PF

def payloadALTA(datos):
    #arma el payload con los datos de la fila de la base de datos
    payload = {
        "first_name" : datos.get("first_name", ""),
        "last_name": datos.get("last_name", ""),
        "personal_email" : datos.get("email", ""),
        "dni" : convertir_a_int(datos.get("dni", "")),
        "direccion" : datos.get("address", ""),
        "localidad" : datos.get("locality", ""),
        "celular": convertir_a_int(datos.get("phone_number", "")),
        "date_of_birth" : formatear_fecha_PF(datos.get("date_of_birth", "")),

    }

    if datos.get("type_of_contract") == "rrdd" or datos.get("type_of_contract") == "monotributo":
        if datos.get("locality").lower() != "santa fe":
            #deposito y transferencia con los mismos datos
            payload.update({
                #deposito
                "banco_2" : datos.get("national_bank"),
                "nro_de_cuenta_3" : datos.get("national_account_number"),
                "alias_3" : datos.get("alias"),
                "cbu_3": datos.get("cbu"),
                "cuil_3" : datos.get("cuil"),


                #transferencia
                "banco": datos.get("national_bank"),
                "nro_de_cuenta_2" : datos.get("account_number"),
                "alias_2": datos.get("alias"),
                "cbu_2": datos.get("cbu"),
                "cuil_2" : datos.get("cuil"),

                "obra_social" : datos.get("health_insurance", ""),
                "código_obra_social" : datos.get("afip_code", ""),
            })
        else:
            payload.update({
                #transferencia
                "banco": datos.get("national_bank"),
                "nro_de_cuenta_2" : datos.get("national_account_number"),
                "alias_2": datos.get("alias"),
                "cbu_2": datos.get("cbu"),
                "cuil_2" : datos.get("cuil"),
                "obra_social" : datos.get("health_insurance", ""),
                "código_obra_social" : datos.get("afip_code", ""),
            })
    else:
        payload.update({
            "banco_3" : datos.get("bank_name"),
            "dirección_del_banco_2": datos.get("bank_address"),
            "bank_swift_code_2" : datos.get("swift_code"),
            "account_holder_2": datos.get("account_holder"),
            "account_number_2": datos.get("account_number"),
            "routing_number_2": datos.get("routing_number"),
            "tipo_de_cuenta_2" : datos.get("account_type"),
            "zip_code_2" : datos.get("zip_code"),
        })

    return payload

