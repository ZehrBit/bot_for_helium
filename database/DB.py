from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///./database/idchats.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def add_chat_to_db(chat_id: int, title: str, chat_type: str):
    """Функция для добавления чата в базу данных"""
    session = SessionLocal()
    db_chat = Chat(chat_id=chat_id, title=title, type=chat_type)
    session.add(db_chat)
    session.commit()
    session.close()


def remove_chat_from_db(chat_id: int):
    """Функция для удаления чата из базы данных"""
    session = SessionLocal()
    db_chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
    if db_chat:
        session.delete(db_chat)
        session.commit()
    session.close()


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, unique=True, index=True)
    title = Column(String)
    type = Column(String)


Base.metadata.create_all(bind=engine)
