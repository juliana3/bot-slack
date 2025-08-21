from sqlalchemy import Column, Integer, String, Date
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

Base = declarative_base()

logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)


class Ingresante(Base):
    __tablename__ = 'ingresantes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String)
    apellido = Column(String)
    dni = Column(String)
    email = Column(String)
    domicilio = Column(String)
    localidad = Column(String)
    celular = Column(String)
    fecha_nacimiento = Column(Date)
    tipo_contrato = Column(String)

    banco = Column(String)
    numero_cuenta = Column(String)
    cbu = Column(String)
    alias = Column(String)
    obra_social = Column(String)
    codigo_afip = Column(String)

    bank_name = Column(String)
    bank_address = Column(String)
    swift_code = Column(String)
    account_holder = Column(String)
    account_number = Column(String)
    routing_number = Column(String)
    tipo_cuenta = Column(String)
    zip = Column(String)


def guardar_ingresante(data_json, session):
    #guarda los datos del ingresante en la bs y retorna el id o None si falla

    #url de s3
    dni_frente_s3 = data_json.get("dni-frente", "")
    dni_dorso_s3 = data_json.get("dni-dorso", "")

    #crear una instancia de Ingresante
    ingresante_db = Ingresante(
        nombre=data_json.get("nombre", ""),
        apellido=data_json.get("apellido", ""),
        dni=data_json.get("dni", ""),
        email=data_json.get("email", ""),
        celular=data_json.get("celular", ""),
        domicilio=data_json.get("domicilio", ""),
        localidad=data_json.get("localidad", ""),
        fecha_nacimiento=data_json.get("fecha-nacimiento", ""), 
        nivel_terciario=data_json.get("nivel-terciario", ""), 
        nivel_universitario=data_json.get("nivel-universitario", ""), 
        obra_social=data_json.get("obra-social", ""),
        codigo_afip=data_json.get("codigo-afip", ""),
        cbu=data_json.get("cbu", ""),
        alias=data_json.get("alias", ""),
        cuil=data_json.get("cuil", ""), 
        banco=data_json.get("banco", ""),
        numero_cuenta=data_json.get("numero-cuenta", ""),
        bank_name=data_json.get("bank-name", ""), 
        bank_address=data_json.get("bank-address", ""),
        swift_code=data_json.get("swift-code", ""), 
        account_holder=data_json.get("account-holder", ""),
        holder_address=data_json.get("holder-address", ""), 
        account_number=data_json.get("account-number", ""), 
        routing_number=data_json.get("routing-number", ""), 
        tipo_cuenta=data_json.get("tipo-cuenta", ""), 
        zip_code=data_json.get("zip-code", ""), 
        tipo_contrato=data_json.get("tipo-contrato", ""), 
        dni_frente=dni_frente_s3,
        dni_dorso=dni_dorso_s3,
        estado_alta="Pendiente",
        id_pf="",
        estado_pdf="Pendiente"
    )

    try:
        session.add(ingresante_db)
        session.commit()
        session.refresh(ingresante_db) #refresh para obtener el id generado
        logging.info(f"Datos del formulario guardados en la base de datos con ID: {ingresante_db.id}")
        return ingresante_db.id
    except Exception as e:
        session.rollback()
        logging.error(f"Error al guardar datos iniciales en la base de datos: {str(e)}", exc_info=True)
        return None
    

def actualizar_estado(ingresante_id, campo, valor, session):
    """
    Args:
    ingresante_id : el id del ingresante en la BD
    campo: el nombre ddel campo a actualizar (estado_alta / id_pf / estado_pdf)
    valor: el nuevo valor para el campo
    Retorna un bool 
    """

    try:
        ingresante = session.query(Ingresante).filter_by(id=ingresante_id).first()
        if ingresante:
            setattr(ingresante, campo, valor) #setattr permite actualizar dnamicamente
            session.commit()
            logging.info(f"Ingresante ID {ingresante_id}: Campo '{campo}' actualizado a '{valor}'")
            return True
        else:
            logging.warning(f"Ingresante con ID {ingresante_id} no encontrado para actualizar")
            return False
        
    except Exception as e:
        session.rollback()
        logging.error(f"Error al actualizar el campo '{campo}' para ingresante ID {ingresante_id}")
        return False
    




