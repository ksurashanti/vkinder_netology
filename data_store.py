# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session

from config import db_url_object

# схема БД
metadata = MetaData()
Base = declarative_base()

engine = create_engine(db_url_object)

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


# добавление записи в бд
class data_store_tools:
    def __init__(self, engine):
        self.engine = engine

    def add_user(self, profile_id, worksheet_id):
        with Session(self.engine) as session:
            to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
            session.add(to_bd)
            session.commit()

# извлечение записей из БД

    def check_user(self, profile_id, worksheet_id):
        with Session(self.engine) as session:
            from_bd = session.query(Viewed).filter(
                Viewed.profile_id == profile_id,
                Viewed.worksheet_id == worksheet_id
                ).first()
            return True if from_bd else False

if __name__ == '__main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    data_store_tools.add_user(engine, 2115, 1245512)
    res = data_store_tools.check_user(engine, 2115, 1245512)
    print(res)
