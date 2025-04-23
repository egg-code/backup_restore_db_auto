import subprocess
import os
import logging
import glob
from datetime import datetime

# Configure logging
logging.basicConfig(filename='./logs/restore.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Define Neon DB connection details
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = '5432'

# Define backup directory
backup_dir = './backups'

# Sort the backup files by modification time and get the latest one
backup_files = sorted(glob.glob(os.path.join(backup_dir, f'{DB_NAME}_*.dump')),key=os.path.getmtime, reverse=True)

if not backup_files:
    logging.error("No backup files found in the backup directory.")
    exit(1) # Exit if no backup files are found

latest_backup_file = backup_files[0]
logging.info(f"Latest backup file found: {latest_backup_file}")

# Set db password enviroment variable
os.environ['PGPASSWORD'] = DB_PASSWORD

# First, drop the existing database to ensure a clean restore
drop_command = [
    "psql",
    '-h', DB_HOST,
    '-p', DB_PORT,
    '-U', DB_USER,
    '-d', 'postgres', # Connect to the default postgres db to drop the target db
    '-c', f"DROP DATABASE IF EXISTS {DB_NAME};"
]

create_command = [
    "psql",
    '-h', DB_HOST,
    '-p', DB_PORT,
    '-U', DB_USER,
    '-d', 'postgres', # Connect to the default postgres db to create the target db
    '-c', f"CREATE DATABASE {DB_NAME};"
]

try:
    logging.info(f"Dropping database: {DB_NAME}")
    subprocess.run(drop_command, check=True)
    logging.info(f"Database {DB_NAME} dropped successfully!")

    logging.info(f"Creating database: {DB_NAME}")
    subprocess.run(create_command, check=True)
    logging.info(f"Database {DB_NAME} created successfully!")
except subprocess.CalledProcessError as e:
    logging.error(f"Failed to drop and create database {DB_NAME} with error: {e}")
    exit(1)

# pg_restore command to restore the backup
restore_command= [
    'pg_restore',
    '-h', DB_HOST,
    '-p', DB_PORT,
    '-U', DB_USER,
    '-d', DB_NAME,
    '-v', # Verbose mode to capture detailed output
    latest_backup_file
]

try:
    logging.info(f"Starting restore for database: {DB_NAME} from {latest_backup_file}")
    subprocess.run(restore_command, check=True)
    logging.info(f"Restore completed successfully!")
except subprocess.CalledProcessError as e:
    logging.error(f"Restore failed with error: {e}")
    exit(1)

print("Restore completed successfully!")