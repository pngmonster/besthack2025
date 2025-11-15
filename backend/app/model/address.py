from app.model.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Float, BigInteger

class AddressModel(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    node_id: Mapped[int] = mapped_column(BigInteger)
    localy: Mapped[str] = mapped_column(String)
    street: Mapped[str] = mapped_column(String)
    number: Mapped[str] = mapped_column(String)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
