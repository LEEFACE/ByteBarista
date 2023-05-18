from flask import Flask, render_template, request, redirect, url_for, session

import boto3
import botocore
import os
from dotenv import load_dotenv

## allows loading configuration vars in .env file
load_dotenv()

from database import ( DBConnector )
from user import User

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

## GLOBAL ENV VARS
S3_BUCKET = os.getenv('S3_BUCKET')
EC2_BASTION_SERVER = os.getenv('EC2_BASTION_SERVER')
SSH_PRIVATE_KEY_PATH = os.getenv('SSH_PRIVATE_KEY_PATH')
RDS_SERVER = os.getenv('RDS_SERVER')
RDS_DB_NAME = os.getenv('RDS_DB_NAME')
RDS_USERNAME = os.getenv('RDS_USERNAME')
RDS_PASSWORD = os.getenv('RDS_PASSWORD')

# Configure the S3 connection
s3 = boto3.client('s3', region_name='us-east-1')

# Login page route
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Username and password from the flask session
        username = request.form['username']
        password = request.form['password']
        user = User(username)

        if user.user_login(username, password, session):
            return redirect(url_for('user_home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    else:
        return render_template('login.html')
        
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Username and password from the flask session
        username = request.form['username']
        password = request.form['password']
        user = User(username)
        user.register(password)
        
        return redirect(url_for('login'))

    else:
        return render_template('register.html')

    
@app.route('/index', methods=['POST'])
def index():
    return render_template('home.html')


@app.route('/user_home', methods=['GET', 'POST'])
def user_home():
    username = session.get('username')

    ## Queries for load to page upon open
    sql_name = f"SELECT first_name, last_name FROM Staff WHERE CAST(staff_id AS VARCHAR) = CAST({username} AS VARCHAR)"               
    sql_product = "SELECT Product.product, COUNT(salesreceipts.product_id) AS count_records FROM SalesReceipts LEFT JOIN Product ON Product.product_id=SalesReceipts.product_id GROUP BY 1 ORDER BY 2 DESC LIMIT 5;"
    sql_sales = "SELECT salesoutlet.neighbourhood, SUM(salesreceipts.line_item_amount) AS sales_to_date FROM SalesReceipts LEFT JOIN Salesoutlet ON Salesoutlet.sales_outlet_id=SalesReceipts.sales_outlet_id GROUP BY 1 ORDER BY 2 DESC LIMIT 3;"

    connector = DBConnector(RDS_SERVER, 5432, RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD)
    ssh_tunnel = connector.connect()
    
    ## update param allows the query to execute and commit instead of read-only
    result_name = connector.execute_query(sql_name) 
    result_product = connector.execute_query(sql_product) 
    result_sales = connector.execute_query(sql_sales)

    staff_name = f"{result_name[0][0]} {result_name[0][1]}"

    connector.close_conn(ssh_tunnel)

    return render_template('user_home.html', row_product=result_product, row_sales=result_sales, staff_name=staff_name)


@app.route('/upload', methods=['GET','POST'])
def upload():
    return render_template('upload.html')


@app.route('/upload_file', methods=['POST'])
def upload_file():
    file = request.files['file']
    filename = file.filename

    print("file", file)
    print("filename", filename)
    ## check file is csv
    if not filename.endswith('.csv'):
        print(f"Object {filename} is not a CSV file.")
        return render_template('upload.html', error='Not a .csv, please upload a valid file')  

    try:
        s3.upload_fileobj(file, S3_BUCKET, filename)
        return 'File uploaded successfully!'
    except botocore.exceptions.ClientError as e:
        return 'Error uploading file: ' + str(e)


# Dashboard page route
@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in
    if 'username' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('login'))


# Logout route
@app.route('/logout')
def logout():
    # Remove the username from the session if it exists
    session.pop('username', None)
    return redirect(url_for('home'))


# Start the Flask application
if __name__ == '__main__':
    app.run(port=8000, debug=True)