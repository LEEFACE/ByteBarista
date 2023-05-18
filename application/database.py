import psycopg2
from sshtunnel import SSHTunnelForwarder
import os
from dotenv import load_dotenv

## allows loading configuration vars in .env file
load_dotenv()

S3_BUCKET = os.getenv('S3_BUCKET')
EC2_BASTION_SERVER = os.getenv('EC2_BASTION_SERVER')
SSH_PRIVATE_KEY_PATH = os.getenv('SSH_PRIVATE_KEY_PATH')
RDS_SERVER = os.getenv('RDS_SERVER')
RDS_DB_NAME = os.getenv('RDS_DB_NAME')
RDS_USERNAME = os.getenv('RDS_USERNAME')
RDS_PASSWORD = os.getenv('RDS_PASSWORD')

## Creates the class for database connector
class DBConnector:
    def __init__(self, host, port, db_name, user, password):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.user = user
        self.password = password
        self.conn = None

    def connect(self):
        ## Because we are in a secure VPC, we need to tunnel through the Bastion server to the RDS server
        ssh_tunnel = SSHTunnelForwarder(
            (EC2_BASTION_SERVER, 22),
            ssh_username = "ubuntu",
            ssh_private_key=SSH_PRIVATE_KEY_PATH,
            remote_bind_address=(self.host, self.port),
            local_bind_address=('localhost', 6543) # can be any port avail
        )

        ssh_tunnel.start()

        # connect to RDS db through the tunnel
        self.conn = psycopg2.connect(
            dbname=self.db_name,
            user=self.user,
            password=self.password,
            host=ssh_tunnel.local_bind_host,
            port=ssh_tunnel.local_bind_port
        )

        return ssh_tunnel

        print("Database connection success!")

    def close_conn(self, ssh_tunnel=None):
        if self.conn:
            self.conn.close()

        print("Database connection closed")
        ssh_tunnel.stop()
    

    def execute_query(self, sql: str, update: str = None):
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql)
        except Exception as e:
            print("ERROR: ", e)
            cursor.close() ## Ensure closed to not lock db
            self.conn.rollback()
            cursor = self.conn.cursor()

        if update is not None:
            self.conn.commit()
            result = "success"
        else:
            try:
                result = cursor.fetchall()
                print(result)
            except Exception as e:
                print('No results: ', e)
                result = None
            
        cursor.close()
        return result