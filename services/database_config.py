import os
import logging
from dotenv import load_dotenv

from sqlalchemy  import create_engine, Column, Integer, String, Text #tipos de ccolumnas
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

#cofiguracion del logging
logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s [%(levelname)s] %(message)s"
)

#configuracion de sqlalchemy para postgres

Base = declarative_base()

class Ingresante(Base):
    __tablename__ = 'ingresantes'
    id = Column(Integer, primary_key= True)
    nombre = Column(String(100), nullable=False)
    apellido= Column(String(100), nullable=False)
    dni = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    celular = Column(String(20), nullable=False)
    domicilio = Column(String(255), nullable=False)
    localidad = Column(String(100), nullable=False)
    fecha_nacimiento = Column(String(20), nullable=False)
    nivel_terciario = Column(String(100))
    nivel_universitario = Column(String(100))

    obra_social = Column(String(100), nullable=False)
    codigo_afip = Column(String(50))

    cbu = Column(String(50))
    alias = Column(String(100))
    cuil = Column(String(50))
    banco = Column(String(100))
    numero_cuenta = Column(String(100))

    bank_name = Column(String(100))
    bank_address = Column(String(255))
    swift_code = Column(String(50))
    account_holder = Column(String(100))
    holder_address = Column(String(100))
    account_number = Column(String(50))
    routing_number = Column(String(50))
    tipo_cuenta = Column(String(50))
    zip_code = Column(String(20))

    tipo_contrato = Column(String(50), nullable=False)
    dni_frente = Column(Text, nullable=False)
    dni_dorso = Column(Text, nullable=False)

    estado_alta = Column(String(50), default='Pendiente')
    id_pf = Column(String(50))
    estado_pdf = Column(String(50), default='Pendiente')

    def __repr__(self):
        return f"<Ingresante(nombre={self.nombre}, apellido={self.apellido}, dni={self.dni})>"


#inicializar motor de base de daatos y sesion
DATABASE_URL = os.getenv('DATABASE_URL')
engine = None
Session = None

if DATABASE_URL:
    try:
        engine= create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        logging.info("Conexión a PostgreSQL y modelos inicializados con exito")
    except Exception as e:
        logging.error(f"Error al inicializar la conexion a PostreSQL: {e}")
else:
    logging.error("DATABASE_URL no está configurada en el entorno. Verifica tu archivo .env")