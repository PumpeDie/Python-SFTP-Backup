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
import configparser

# Lecture du fichier config.ini
config = configparser.ConfigParser()
config.read('config/config.ini')

# Configuration des logs
log_file = config['LOGGING']['log_file']
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.info(f'Le répertoire source {source_dir} n\'existe pas')
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
    username = config['EMAIL']['smtp_username']
    password = config['EMAIL']['smtp_password']

    if isinstance(to_emails, str):
        to_emails = [to_emails]  # Convertir en liste si c'est une seule adresse email

    # Créer le message email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ', '.join(to_emails)
    msg['Subject'] = subject

    # Ajouter le corps de l'email
    msg.attach(MIMEText(body, 'plain'))

    # Joindre le fichier log si fourni
    if log_file and os.path.exists(log_file):
        with open(log_file, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(log_file)}'
            )
            msg.attach(part)

    try:
        # Gmail requiert une connexion SSL sécurisée
        context = ssl.create_default_context()

        # Connexion au serveur SMTP de Gmail avec SSL sur le port 465
        with smtplib.SMTP_SSL(config['EMAIL']['smtp_host'], config['EMAIL']['smtp_port'], context=context) as server:
            server.login(username, password)
            server.sendmail(from_email, to_emails, msg.as_string())

        logging.info(f"Email envoyé avec succès à {', '.join(to_emails)}")

    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email: {e}")

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
remote_directory = config['SFTP']['remote_directory']

email_enabled = config.getboolean('EMAIL', 'enable_email')
smtp_host = config['EMAIL']['smtp_host']
smtp_port = int(config['EMAIL']['smtp_port'])
smtp_username = config['EMAIL']['smtp_username']
smtp_password = config['EMAIL']['smtp_password']
sender_email = config['EMAIL']['sender_email']
recipient_email = config['EMAIL']['recipient_email']
subject_success = config['EMAIL']['subject_success']
subject_failure = config['EMAIL']['subject_failure']
attach_log = config.getboolean('EMAIL', 'attach_log')

# Processus principal
try:
    download_file(url, zip_filename)
    unzip_file(zip_filename, extracted_folder)

    if not compare_files(os.path.join(extracted_folder, sql_filename), sql_filename):
        current_date = datetime.datetime.now().strftime('%Y%d%m')
        
        try:
            create_archive(extracted_folder, current_date)
        except Exception as e:
            logging.error(f'Erreur lors de la création de l\'archive: {e}')
            raise
        
        remote_path = os.path.join(remote_directory, f'{current_date}.tar.gz')
        
        try:
            upload_file_sftp(f'{current_date}.tar.gz', remote_path, sftp_host, sftp_port, sftp_username, sftp_password)
        except Exception as e:
            logging.error(f'Erreur lors de l\'upload du fichier via SFTP: {e}')
            raise
        
        if email_enabled:
            try:
                send_email(
                    subject=subject_success,
                    body="Modification des fichiers du serveur Web détectée. Nouvelle archive a été créée sur le serveur distant.",
                    to_emails=recipient_email,
                    from_email=sender_email,
                    log_file=log_file if attach_log else None
                )
            except Exception as e:
                logging.error(f'Erreur lors de l\'envoi de l\'email: {e}')
                raise
    else:
        if email_enabled:
            logging.info("Aucune modification détectée, aucune nouvelle archive créée.")
            send_email(
                subject=subject_failure,
                body="Aucune modification détectée dans les fichiers du serveur Web. Pas de nouvelle archive créée.",
                to_emails=recipient_email,
                from_email=sender_email,
                log_file=log_file if attach_log else None
            )
except Exception as e:
    logging.error(f'Erreur dans le processus d\'archivage: {e}')
    if email_enabled:
        send_email(
            subject="Archivage : Erreur d'archivage",
            body="Erreur détectée lors du processus d'archivage. Veuillez consulter les logs pour plus d'informations.",
            to_emails=recipient_email,
            from_email=sender_email,
            log_file=log_file if attach_log else None
        )

delete_old_files(remote_directory, retention_days)
