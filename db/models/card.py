from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String
from sqlalchemy.orm import relationship
from db.settings import Base

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.user_id", ondelete="CASCADE"))
    
    user = relationship(
        "User",
        back_populates="cards"
    )
    