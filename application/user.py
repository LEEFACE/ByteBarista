from database import DBConnector
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


class User:
    def __init__(self, username, password, session):
        self.username = username
        self.password = password
        self.session = session

    def user_login(self, session):
        connector = DBConnector(RDS_SERVER, 5432, RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD)
        ssh_tunnel = connector.connect()

        sql = f"""
        SELECT password FROM Staff WHERE CAST(staff_id AS VARCHAR) = CAST({self.username} AS VARCHAR)
        """
        
        result = connector.execute_query(sql)

        connector.close_conn(ssh_tunnel)

        # if password in db, then go ahead, else no.
        if result is not None: 
            if self.password == result[0][0]:
                print("passwords match")

            # if username in users and users[username] == password:
                # Store the username in the session
                session['username'] = self.username
                return True
        return False
    
    def register(self):
        connector = DBConnector(RDS_SERVER, 5432, RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD)
        ssh_tunnel = connector.connect()
        
        sql = f"""
        UPDATE Staff SET password = '{self.password}' WHERE CAST(staff_id AS VARCHAR) = CAST({username} AS VARCHAR)
        """

        result = connector.execute_query(sql, "update") 
        print(result)

        connector.close_conn(ssh_tunnel)
        