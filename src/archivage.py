import time
import requests
import zipfile
import os
import datetime
import shutil
import paramiko
import logging
import socket
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase

# Configuration des logs
with open('archivage.log', 'w'):
    pass

logging.basicConfig(filename='archivage.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

# Fonction pour envoyer un email
def send_email(subject, body, to_emails, from_email, log_file=None):
    # Hardcoded Gmail credentials
    username = "silvaraynal@gmail.com"  # Replace with your Gmail email
    password = "vgjj mdaw imii vzkb"  # Replace with your Gmail password or App Password

    # Ensure to_emails is a list, even if it's a single email address
    if isinstance(to_emails, str):
        to_emails = [to_emails]  # Convert to list if it's a string

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = subject

    # Add the email body
    msg.attach(MIMEText(body, 'plain'))

    # Attach the log file if provided
    if log_file and os.path.exists(log_file):
        with open(log_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(log_file)}'
            )
            msg.attach(part)

    try:
        # Gmail requires a secure SSL connection
        context = ssl.create_default_context()

        # Connect to Gmail's SMTP server with SSL on port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(username, password)
            # Send the email
            server.sendmail(from_email, to_emails, msg.as_string())

        print(f"Email successfully sent to {', '.join(to_emails)}")

    except Exception as e:
        print(f"Error sending email: {e}")

# Configuration
url = 'http://localhost/archive.zip'
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

try:
    if not compare_files(os.path.join(extracted_folder, sql_filename), sql_filename):
        current_date = datetime.datetime.now().strftime('%Y%d%m')
        
        try:
            create_archive(extracted_folder, current_date)
        except Exception as e:
            logging.error(f'Erreur lors de la création de l\'archive: {e}')
            raise
        
        remote_path = f'{remote_directory}/{current_date}.tar.gz'
        
        try:
            upload_file_sftp(f'{current_date}.tar.gz', remote_path, sftp_host, sftp_port, sftp_username, sftp_password)
        except Exception as e:
            logging.error(f'Erreur lors de l\'upload du fichier via SFTP: {e}')
            raise
        
        try:
            send_email(
                subject="Archivage : Nouvelle archive créée",
                body="Modification des fichiers du serveur Web détectée. Nouvelle archive a été créée sur le serveur distant.",
                to_emails="silvaraynal@gmail.com",  # Or a list of recipients
                from_email="silvaraynal@gmail.com",
                log_file="archivage.log"  # Optional log file attachment
            )
        except Exception as e:
            logging.error(f'Erreur lors de l\'envoi de l\'email: {e}')
            raise
except Exception as e:
    logging.error(f'Erreur dans le processus d\'archivage: {e}')
    send_email(
                subject="Archivage : Erreur d'archivage",
                body="Erreur détectée lors du processus d'archivage. Veuillez consulter les logs pour plus d'informations.",
                to_emails="silvaraynal@gmail.com",  # Or a list of recipients
                from_email="silvaraynal@gmail.com",
                log_file="archivage.log"  # Optional log file attachment
            )

else:
    logging.info("Fin de la procédure d'archivage")
    send_email(
    subject="Archivage : Aucune modification des fichiers",
    body="Aucune modification détectée dans les fichiers du serveur Web. Pas de nouvelle archive créée.",
    to_emails="silvaraynal@gmail.com",  # Or a list of recipients
    from_email="silvaraynal@gmail.com",
    log_file="archivage.log"  # Optional log file attachment
    )

delete_old_files(remote_directory, retention_days)
