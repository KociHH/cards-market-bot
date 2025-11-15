from sqlalchemy import Boolean, Column, ForeignKey, Integer, BigInteger, String
from sqlalchemy.orm import relationship
from db.settings import Base

class User(Base):
    """
    user_id: int
    admin: bool
    """
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    admin = Column(Boolean, nullable=False, default=False)
    
    balances = relationship("Balance", back_populates="user")
    cards = relationship("Card", back_populates="user")
    on_moderation = relationship("OnModeration", back_populates="user")
    statistics = relationship("Statistics", back_populates="user")
    applications = relationship("Applications", back_populates="user")
    
class Balance(Base):
    """
    user_id: int ForeignKey("users.user_id", ondelete="CASCADE")
    balance: int
    """
    __tablename__ = "balances"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    balance = Column(BigInteger, nullable=True)
    
    user = relationship(    
        "User", 
        back_populates="balances"
        )