import time
import requests
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

# Configuration depuis le fichier config.ini
url = config['DEFAULT']['url']
zip_filename = 'archive.zip'
extracted_folder = 'extracted_files'
sql_filename = config['DEFAULT']['sql_filename']
retention_days = int(config['DEFAULT']['retention_days'])
enable_retention = config.getboolean('DEFAULT', 'enable_retention')

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
recipient_email = config['EMAIL']['recipient_email'].split(',')
recipient_email = [email.strip() for email in recipient_email]  # Nettoyer les espaces
subject_success = config['EMAIL']['subject_success']
subject_failure = config['EMAIL']['subject_failure']
attach_log = config.getboolean('EMAIL', 'attach_log')

log_file = config['LOGGING']['log_file']

# Configuration des logs
# Creer un fichier archive.log dans le dossier logs si il n'existe pas
# Vérifier si le dossier logs existe, sinon le créer
if not os.path.exists('logs'):
    os.makedirs('logs')
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

# Fonction pour télécharger le fichier zip
def download_file(url, filename):
    try:
        response = requests.get(url, allow_redirects=True, stream=True, verify=False)
        response.raise_for_status()  # Vérifie les erreurs HTTP

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logging.info(f'Fichier {filename} téléchargé avec succès')
    except requests.RequestException as e:
        logging.error(f'Erreur lors du téléchargement du fichier {filename}: {e}')

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
        
# Fonction pour établir une connexion SFTP
def create_sftp_connection(host, port, username, password):
    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        logging.info("Connexion SFTP établie avec succès")
        return sftp, transport
    except (paramiko.SSHException, socket.gaierror) as e:
        logging.error(f'Erreur lors de la connexion SFTP: {e}')
        return None, None

# Fonction pour uploader un fichier via SFTP
def upload_file_sftp(sftp, local_file, remote_path):
    try:
        # Vérifier si le répertoire distant existe, sinon le créer
        try:
            sftp.stat(os.path.dirname(remote_path))
        except FileNotFoundError:
            sftp.mkdir(os.path.dirname(remote_path))
            logging.info(f'Dossier distant {os.path.dirname(remote_path)} créé')

        sftp.put(local_file, remote_path)
        logging.info(f'Fichier {local_file} uploadé avec succès vers {remote_path}')
    except Exception as e:
        logging.error(f'Erreur lors de l\'upload du fichier {local_file} via SFTP: {e}')

# Fonction pour supprimer les anciens fichiers via SFTP
def delete_old_files_sftp(sftp, directory, retention_days):
    now = time.time()
    try:
        # Lister les fichiers dans le répertoire distant
        for filename in sftp.listdir(directory):
            file_path = os.path.join(directory, filename)
            # Obtenir les informations sur le fichier
            file_info = sftp.stat(file_path)
            file_time = file_info.st_mtime  # Temps de dernière modification

            # Vérifier si le fichier doit être supprimé
            if (now - file_time) > retention_days * 86400:
                sftp.remove(file_path)
                logging.info(f'Fichier {filename} supprimé pour cause de dépassement de la durée de conservation')
    except Exception as e:
        logging.error(f'Erreur lors de la suppression des anciens fichiers: {e}')

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

# Processus principal d'archivage
try:
    # Téléchargement du fichier zip depuis l'URL configurée
    download_file(url, zip_filename)
    
    # Décompression du fichier zip téléchargé
    shutil.unpack_archive(zip_filename, extracted_folder)
    
    # Chemin du fichier SQL provenant du serveur Web
    try: 
        local_sql_file = os.path.join(extracted_folder, sql_filename)
        logging.info(f'Fichier SQL local extrait: {local_sql_file}')
    except FileNotFoundError as e:
        logging.error(f'Erreur lors de la récupération du fichier SQL local: {e}')
        raise FileNotFoundError('Fichier SQL local non trouvé')
    
    # Établir la connexion SFTP
    sftp, transport = create_sftp_connection(sftp_host, sftp_port, sftp_username, sftp_password)
    
    # Récupérer la liste des fichiers dans le répertoire distant
    remote_files = sftp.listdir(remote_directory)
    
    # Filtrer les fichiers .tar.gz et trier par date de modification
    tar_files = [f for f in remote_files if f.endswith('.tar.gz')]
    tar_files.sort(key=lambda x: sftp.stat(os.path.join(remote_directory, x)).st_mtime, reverse=True)
    
    if tar_files:
        # Récupérer le dernier fichier .tar.gz
        latest_tar_file = tar_files[0]
        remote_tar_file = os.path.join(extracted_folder, latest_tar_file)
        
        # Télécharger le dernier fichier .tar.gz
        sftp.get(os.path.join(remote_directory, latest_tar_file), remote_tar_file)
    else:
        logging.error('Aucune archive .tar.gz trouvée sur le serveur distant')
        raise FileNotFoundError('Aucune archive .tar.gz trouvée sur le serveur distant')
    
    # Decompresser le fichier .tar.gz
    shutil.unpack_archive(remote_tar_file, extracted_folder)
    
    # Chemin des fichiers SQL locaux et distants
    remote_sql_file = os.path.join(extracted_folder, 'remote_dumpfile.sql')
    
    # Date actuelle pour nommer l'archive
    current_date = datetime.datetime.now().strftime('%Y%d%m')  # Format de la date pour nommer l'archive
        
    # Comparaison du fichier SQL extrait avec celui du serveur distant
    if not compare_files(local_sql_file, remote_sql_file):

        try:
            # Suppression de l'archive locale si elle existe
            os.remove(remote_sql_file)
            os.remove(remote_tar_file)
            # Renommage fichier SQL extrait
            os.rename(os.path.join(extracted_folder, sql_filename), os.path.join(extracted_folder,'remote_dumpfile.sql'))
            # Création de l'archive avec la date du jour
            create_archive(extracted_folder, current_date)
        except Exception as e:
            logging.error(f'Erreur lors de la création de l\'archive: {e}')
            raise

        # Chemin de l'archive à uploader sur le serveur distant
        remote_path = os.path.join(remote_directory, f'{current_date}.tar.gz')

        if sftp:
            try:
                # Upload de l'archive via SFTP
                upload_file_sftp(sftp, f'{current_date}.tar.gz', remote_path)
            except Exception as e:
                logging.error(f'Erreur lors de l\'upload du fichier via SFTP: {e}')

            finally:
                # Fermeture de la connexion SFTP
                sftp.close()
                transport.close()
            
            # Suppression des anciens fichiers sur le serveur distant si nécessaire
            if enable_retention:
                delete_old_files_sftp(sftp, remote_directory, retention_days)

        # Envoi d'un email en cas de succès avec option d'attacher le fichier de log
        if email_enabled:
            try:
                send_email(
                    subject=subject_success,
                    body="Modification des fichiers du serveur Web détectée. Nouvelle archive créée sur le serveur distant.",
                    to_emails=recipient_email,
                    from_email=sender_email,
                    log_file=log_file if attach_log else None  # Attacher le fichier de log si activé
                )
            except Exception as e:
                logging.error(f'Erreur lors de l\'envoi de l\'email: {e}')
                raise
        
    else:
        # Si aucune modification n'est détectée, envoi d'un email d'absence de nouvelle archive
        if email_enabled:
            logging.info("Aucune modification détectée, aucune nouvelle archive créée.")
            send_email(
                subject="Archivage : Aucune modification détectée",
                body="Aucune modification détectée dans les fichiers du serveur Web. Pas de nouvelle archive créée.",
                to_emails=recipient_email,
                from_email=sender_email,
                log_file=log_file if attach_log else None  # Attacher le fichier de log si activé
            )
except Exception as e:
    # En cas d'erreur dans le processus, envoi d'un email d'alerte
    logging.error(f'Erreur dans le processus d\'archivage: {e}')
    if email_enabled:
        send_email(
            subject=subject_failure,
            body=f"Erreur détectée lors du processus d'archivage : {e}. Veuillez consulter les logs pour plus d'informations.",
            to_emails=recipient_email,
            from_email=sender_email,
            log_file=log_file if attach_log else None  # Attacher le fichier de log si activé
        )
    
finally:
    # Suppression des fichiers temporaires
    for file in [zip_filename, f'{current_date}.tar.gz']:
        if os.path.exists(file):
            os.remove(file)
            logging.info(f'Fichier temporaire {file} supprimé avec succès')
    if os.path.exists(extracted_folder):
        shutil.rmtree(extracted_folder)
        logging.info(f'Répertoire temporaire {extracted_folder} supprimé avec succès')