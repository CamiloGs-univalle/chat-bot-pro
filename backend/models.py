from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Usuario(Base):

    __tablename__ = "usuarios"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    telefono = Column(
        String,
        unique=True,
        nullable=False
    )


class MensajeDB(Base):

    __tablename__ = "mensajes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    telefono = Column(
        String,
        nullable=False
    )

    mensaje = Column(
        String,
        nullable=False
    )