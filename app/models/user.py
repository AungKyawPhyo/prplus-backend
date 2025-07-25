from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, onupdate=func.now())

    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    updated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # ✅ Async-safe relationships with selectin loading
    created_by = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[created_by_id],
        post_update=True,
        lazy="selectin"
    )
    updated_by = relationship(
        "User",
        remote_side=[id],
        foreign_keys=[updated_by_id],
        post_update=True,
        lazy="selectin"
    )