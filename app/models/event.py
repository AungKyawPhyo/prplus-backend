from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String)
    venue = Column(String)
    description = Column(String)

    event_date = Column(DateTime, nullable=False)

    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, onupdate=func.now())

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_by = relationship("User", foreign_keys=[created_by_id], lazy="selectin")
    updated_by = relationship("User", foreign_keys=[updated_by_id], lazy="selectin")