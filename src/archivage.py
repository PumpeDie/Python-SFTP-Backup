import time
import requests
import zipfile
import os
import datetime
import shutil
import paramiko
import logging
import socket
import configparser

# Lecture du fichier config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration des logs
log_file = config['LOGGING']['log_file']
logging.basicConfig(filename=log_file, level=logging.INFO)

# Fonction pour télécharger le fichier zip
def download_file(url, filename):
    try:
        response = requests.get(url, allow_redirects=True, stream=True)
        response.raise_for_status()  # Vérifie les erreurs HTTP

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logging.info(f'Fichier {filename} téléchargé avec succès')
    except requests.RequestException as e:
        logging.error(f'Erreur lors du téléchargement du fichier {filename}: {e}')

# Fonction pour dézipper l'archive zip
def unzip_file(filename, extract_to):
    try:
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logging.info(f'Contenu de l\'archive {filename} extrait avec succès')
    except (zipfile.BadZipFile, FileNotFoundError) as e:
        logging.error(f'Erreur lors de l\'extraction du fichier {filename}: {e}')

# Fonction pour comparer deux fichiers
def compare_files(file1, file2):
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            content1 = f1.read()
            content2 = f2.read()

        if content1 == content2:
            logging.info(f'Les fichiers {file1} et {file2} sont identiques')
            return True
        else:
            logging.info(f'Les fichiers {file1} et {file2} sont différents')
            return False
    except FileNotFoundError as e:
        logging.error(f'Erreur lors de la comparaison des fichiers: {e}')
        return False

# Fonction pour créer une archive
def create_archive(source_dir, output_filename):
    if not os.path.exists(source_dir):
        logging.error(f'Le répertoire source {source_dir} n\'existe pas')
        return
    try:
        shutil.make_archive(output_filename, 'gztar', source_dir)
        logging.info(f'Archive {output_filename}.tar.gz créée avec succès')
    except Exception as e:
        logging.error(f'Erreur lors de la création de l\'archive {output_filename}: {e}')

# Fonction pour supprimer les anciens fichiers
def delete_old_files(directory, retention_days):
    now = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_time = os.path.getmtime(file_path)
            if (now - file_time) > retention_days * 86400:
                os.remove(file_path)
                logging.info(f'Fichier {filename} supprimé pour cause de dépassement de la durée de conservation')

# Fonction pour uploader un fichier via SFTP
def upload_file_sftp(local_file, remote_path, host, port, username, password):
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        # Vérifier si le répertoire distant existe, sinon le créer
        try:
            sftp.stat(os.path.dirname(remote_path))
        except FileNotFoundError:
            sftp.mkdir(os.path.dirname(remote_path))
            logging.info(f'Dossier distant {os.path.dirname(remote_path)} créé')

        sftp.put(local_file, remote_path)
        sftp.close()
        transport.close()
        logging.info(f'Fichier {local_file} uploadé avec succès vers {remote_path}')
    except (paramiko.SSHException, socket.gaierror) as e:
        logging.error(f'Erreur lors de l\'upload du fichier {local_file} via SFTP: {e}')

# Configuration depuis le fichier config.ini
url = config['DEFAULT']['url']
zip_filename = 'archive.zip'
extracted_folder = 'extracted_files'
sql_filename = config['DEFAULT']['sql_filename']
retention_days = int(config['DEFAULT']['retention_days'])

sftp_host = config['SFTP']['host']
sftp_port = int(config['SFTP']['port'])
sftp_username = config['SFTP']['username']
sftp_password = config['SFTP']['password']
remote_directory = config['SFTP']['remote_directory']  # Choisir la ligne correcte selon l'OS

# Processus principal
download_file(url, zip_filename)
unzip_file(zip_filename, extracted_folder)

if not compare_files(os.path.join(extracted_folder, sql_filename), sql_filename):
    current_date = datetime.datetime.now().strftime('%Y%d%m')  # Format AAAADDMM
    create_archive(extracted_folder, current_date)

    remote_path = os.path.join(remote_directory, f'{current_date}.tar.gz')
    upload_file_sftp(f'{current_date}.tar.gz', remote_path, sftp_host, sftp_port, sftp_username, sftp_password)

delete_old_files(remote_directory, retention_days)
