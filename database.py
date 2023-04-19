from config import Config
from mysql.connector import Error
from mysql.connector import pooling
from sqlalchemy import create_engine
from playhouse.pool import PooledMySQLDatabase


config = Config().get_config_json()


class DatabaseConnections:
    """
    * Get Following DB Connection Pool :-
        1. MySQl-Connector  
        2. Peewee
        3. SQLAlchemy
    """

    def mysql_connection(self):
        try:
            connection_pool = pooling.MySQLConnectionPool(pool_size=30,
                                                          pool_reset_session=True,
                                                          host=config['DB_HOST_IP'],
                                                          database=config['DB_NAME'],
                                                          user=config['DB_USER_NAME'],
                                                          password=config['DB_PASSWORD'],
                                                          pool_name="pool"
                                                          )
                                                        
            conObj = connection_pool.get_connection()
            return conObj

        except Error as e:
            print("Error while connecting to MySQL using Connection pool ", e)

    def peewee_connection(self):
        try:
            pooled_peewee_connection = PooledMySQLDatabase(max_connections=30,
                                                           host=config['DB_HOST_IP'],
                                                           database=config['DB_NAME'],
                                                           user=config['DB_USER_NAME'],
                                                           password=config['DB_PASSWORD']
                                                           )
            return pooled_peewee_connection

        except Error as e:
            print("Error while connecting to Peewee using Connection pool ", e)

    def sqlalchemy_connection(self):
        try:
            DB_URL = f"mysql+mysqlconnector://{config['DB_USER_NAME']}:{config['DB_PASSWORD']}@{config['DB_HOST_IP']}:{config['DB_PORT']}/{config['DB_NAME']}"
            pooled_sqlalchemy_engine = create_engine(url=DB_URL, pool_size=30, max_overflow=35, pool_pre_ping=True)

            return pooled_sqlalchemy_engine

        except Error as e:
            print("Error while connecting to SQLAlchemy using Connection pool ", e)


if __name__ == '__main__':
    # * Get connection object from a pool
    
    db = DatabaseConnections()

    # * MySQL Connector
    
    con = db.mysql_connection()
    print(con)
    
    # # print(f"pool_name \t= {con.pool_name}")
    # # print(f"pool_size \t= {con.pool_size}")
    # conObj = con.get_connection()
    # if conObj.is_connected():
    #     print(f"get_server_info = {conObj.get_server_info()}")
    #     cur = conObj.cursor(buffered=True)
    #     cur.execute("select count(*) from retailerid;")
    #     print(f"fetchone \t= {cur.fetchone()}")
    #     cur.close()
    #     conObj.close()
   
    peewee_con = db.peewee_connection()
    peewee_result = peewee_con.execute_sql("select count(*) from retailerid;")
    peewee_record = peewee_result.fetchone()
    print(f"Pewee Record {peewee_record}")

    sqlalchemy_con = db.sqlalchemy_connection()
    sqlalchemy_record = sqlalchemy_con.execute(
        "select count(*) from retailerid;")
    sqlalchemy_record = sqlalchemy_record.fetchone()
    print("SQLalchemy record",sqlalchemy_record)
