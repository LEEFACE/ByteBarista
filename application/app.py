from flask import Flask, render_template, request, redirect, url_for, session

import boto3
import botocore
import os
import psycopg2
from sshtunnel import SSHTunnelForwarder

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
# S3_BUCKET = 'aws-glue-byte-barista-data-bucket'


def execute_query(sql: str, update: str = None):
    # Create an SSH tunnel
    tunnel = SSHTunnelForwarder(
    (EC2_BASTION_SERVER, 22),
    ssh_username='ubuntu',
    ssh_private_key=SSH_PRIVATE_KEY_PATH,
    remote_bind_address=(RDS_SERVER, 5432),
    local_bind_address=('localhost', 6543), # could be any available port
    )
    # Start the tunnel
    tunnel.start()

# Create a database connection
    conn = psycopg2.connect(
        dbname=RDS_DB_NAME,
        user=RDS_USERNAME,
        password=RDS_PASSWORD,
        host=tunnel.local_bind_host,
        port=tunnel.local_bind_port,
        )
    
    cursor = conn.cursor()
    print('opened database successfully')

    try:
        cursor.execute(sql)
    except:
        print("error")
        try:
            cursor.close()
            cursor = conn.cursor()
        except:
            conn.close()
            conn = psycopg2.connect(dbname=RDS_DB_NAME,
                user=RDS_USERNAME,
                password=RDS_PASSWORD,
                host=tunnel.local_bind_host,
                port=tunnel.local_bind_port,)
        cursor = conn.cursor()

    if update is not None:
        conn.commit()
        result = "success"
    else:
        try:
            result = cursor.fetchall()
            print(result)
        except: 
            print("No results")
            result = None


    conn.close()
    tunnel.stop()
    print('closed database successfully')

    return result


# Login page route
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = f"""
        SELECT password FROM Staff WHERE CAST(staff_id AS VARCHAR) = CAST({username} AS VARCHAR)
        """
        result = execute_query(sql)        
        # print("password from sender", password)

        ## if password in db, then go ahead, else no.
        if result is not None: 
            if password == result[0][0]:
                print("passwords match")

            # if username in users and users[username] == password:
                # Store the username in the session
                session['username'] = username
                return redirect(url_for('user_home'))
            else:
                return render_template('login.html', error='Passwords do not match')  
        else:
            return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        sql = f"UPDATE Staff SET password = '{password}' WHERE CAST(staff_id AS VARCHAR) = CAST({username} AS VARCHAR)"
        result = execute_query(sql, "update")

        return redirect(url_for('login'))

    else:
        return render_template('register.html')
    
@app.route('/index', methods=['POST'])
def index():
    return render_template('home.html')

@app.route('/user_home', methods=['GET', 'POST'])
def user_home():
    sql_product = "SELECT Product.product, COUNT(salesreceipts.product_id) AS count_records FROM SalesReceipts LEFT JOIN Product ON Product.product_id=SalesReceipts.product_id GROUP BY 1 ORDER BY 2 DESC LIMIT 5;"
    result_product = execute_query(sql_product) 
    print(result_product)

    sql_sales = "SELECT salesoutlet.neighbourhood, SUM(salesreceipts.line_item_amount) AS sales_to_date FROM SalesReceipts LEFT JOIN Salesoutlet ON Salesoutlet.sales_outlet_id=SalesReceipts.sales_outlet_id GROUP BY 1 ORDER BY 2 DESC LIMIT 3;"
    result_sales = execute_query(sql_sales) 
    print(result_sales)

    return render_template('user_home.html', row_product=result_product, row_sales=result_sales)

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
