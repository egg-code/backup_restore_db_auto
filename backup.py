import subprocess
import os
from datetime import datetime
import logging

# Ensure the logs directory exists
if not os.path.exists('./logs'):
    os.makedirs('./logs')

# Configure logging
logging.basicConfig(filename='./logs/backup.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Define Neon DB connection details
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = '5432'

# Define backup directory and filename
backup_dir = './backups'
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir) # Create backup directory if it doesn't exist)

# Create backup file with timestamp
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
backup_file = f"{DB_NAME}_{timestamp}.dump"
backup_path = os.path.join(backup_dir, backup_file)

# Set db password environment variable
os.environ['PGPASSWORD'] = DB_PASSWORD

# pg_dump command to create a backup
pg_command = [
    'pg_dump',
    '-h', DB_HOST,
    '-p', DB_PORT,
    '-U', DB_USER,
    '-F', 'c', # Custom format to allow for compression
    '-v', # Verbose mode to capture detailed output
    '-f', backup_path,
    DB_NAME
]

# Run the backup command
try:
    logging.info(f"Starting backup for database: {DB_NAME} to {backup_path}")
    subprocess.run(pg_command, check=True, text=True)
    logging.info(f"Backup completed successfully!")
except subprocess.CalledProcessError as e:
    logging.error(f"Backup failed with error: {e}")