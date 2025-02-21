from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://logisticaRODVAL:logisticaRODVAL@localhost/rodval"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Metadata para reflejar las tablas existentes
metadata = MetaData()
metadata.reflect(bind=engine)

# Función para obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()