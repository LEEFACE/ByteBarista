Byte Barista README

Install the below packages as a starting point for running the application. This is best performed in a virtual environment by running the following at the root of the directory:

`python3 -m venv venv`

then activate the virtual environment

`source venv/bin/activate`

then install the requirements below:

`pip3 install -r requirements.txt`

Packages in requirements file shoudl be:
```
Python 3.x
Flask
boto3
botocore
psycopg2
dotenv
```

Additional configuration:
Create a .env file in the root directory of the project.

Include the following environment variables in the .env file:


```
FLASK_SECRET_KEY: Secret key used for session encryption in Flask.
S3_BUCKET: Name of the Amazon S3 bucket for file uploads.
EC2_BASTION_SERVER: The address of the EC2 Bastion server.
SSH_PRIVATE_KEY_PATH: Path to the SSH private key file.
RDS_SERVER: Address of the RDS server.
RDS_DB_NAME: Name of the RDS database.
RDS_USERNAME: Username for connecting to the RDS database.
RDS_PASSWORD: Password for connecting to the RDS database.
```

Usage
To start the Flask application, run the following command:

`flask run`

The application will output the address to navigate to upon success of running the application

Routes
The application provides the following routes:

```
/: Home page route. Renders the home.html template.
/login: Login page route. Handles user login and authentication.
/register: Registration page route. Handles user registration.
/index: Redirects to the home page.
/user_home: User home page route. Displays user-specific information from the database.
/upload: File upload page route. Renders the upload.html template.
/upload_file: File upload route. Handles file uploads to Amazon S3.
/dashboard: Dashboard page route. Requires user authentication and renders the dashboard.html template.
/logout: Logout route. Clears the session and redirects to the home page.
```
Database Connection
The application uses a PostgreSQL database that is hosted within AWS RDS for storing user information and executing queries. The database connection details are provided in the environment variables (`RDS_SERVER`, `RDS_DB_NAME`, `RDS_USERNAME`, `RDS_PASSWORD`) and utilises an SSH Tunnel to access the RDS through the VPC. The DBConnector class in the database.py file handles the database connection and query execution.

File Upload
The application allows users to upload CSV files to an Amazon S3 bucket as a part of the ETL process within the application. This kicks off an AWS Glue job dependant on the filename that is running. The S3 bucket name is specified in the `S3_BUCKET` environment variable. Additionally, uploaded files are validated to ensure they are in CSV format before being uploaded to the S3 bucket.
