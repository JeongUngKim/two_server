
from config import Config
from sqlalchemy import create_engine

def get_db_table():

    engine = create_engine('mysql+mysqldb://'+Config.DB_USER+':'+Config.DB_PASSWORD+"@"+Config.HOST+":3306/"+Config.DATABASE)

    return engine