from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String
from sqlalchemy.orm import relationship
from bot.shared.db.settings import Base

class OnModeration(Base):
    __tablename__ = "onModeration"
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"))
    
    user = relationship(
        "User", 
        back_populates="on_moderation"
        )
    
class Statistics(Base):
    __tablename__ = "statistics"
    
    id = Column(BigInteger, primary_key=True)
    approved = Column(BigInteger, nullable=False)
    rejected = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"))
    
    user = relationship(
        "User", 
        back_populates="statistics"
        )
    
class Applications(Base):
    __tablename__ = "applications"
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"))
    username = Column(String, nullable=True)
    address = Column(String, nullable=False)
    sum_withdrow = Column(BigInteger, nullable=False)
    
    user = relationship(
        "User", 
        back_populates="applications"
        )