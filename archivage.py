# Vous devez réaliser un système d'archivage qui permet de récupérer un fichier .zip en https sur un serveur Web 
# et de l'archiver sur un serveur distant avec une durée de conservation paramètrable. 
# L'URL du fichier .zip à récupérer est toujours la même.


import requests;
import zipfile;
import os;
import datetime;
import time;
import shutil;

# Fonction pour télécharger le fichier zip
def download_file(url, filename):
    response = requests.get(url, allow_redirects=True, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Write the contents of the response to a file in binary mode
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f'Fichier {filename} téléchargé avec succès')
    else:
        print(f'Erreur lors du téléchargement du fichier {filename} avec le code de statut {response.status_code}')


# Fonction pour dezipper l'archive zip
def unzip_file(filename, extract_to):
    # Check if the file is a zip file
    if filename.endswith('.zip'):
        # Verify if the file is a valid zip file
        try:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f'Contenu de l\'archive {filename} extrait avec succès')
        except zipfile.BadZipFile:
            print(f'Le fichier {filename} n\'est pas un fichier zip valide')
    else:
        print(f'Le fichier {filename} n\'est pas un fichier zip')


# Fonction pour comparer deux fichiers
def compare_files(file1, file2):
    # Read the contents of the files in binary mode
    with open(file1, 'rb') as f1:
        content1 = f1.read()
    
    with open(file2, 'rb') as f2:
        content2 = f2.read()
    
    # Compare the contents
    if content1 == content2:
        print(f'Les fichiers {file1} et {file2} sont identiques')
        return True
    else:
        print(f'Les fichiers {file1} et {file2} sont différents')
        return False

#L'URL du fichier .zip à récupérer est toujours la même.

#Ce fichier .zip contient un dump SQL (le fichier a toujours le même nom dans le zip).

#Une fois le fichier dézippé, il faut le contrôler (que ce ne soit pas le même que la veille) et créer une nouvelle archive au format AAAADDMM.tgz que l'on va aller poser sur un serveur distant pour archivage.

#Le serveur de destination pouvant être un serveur SMB/CIFS (Windows), NFS (Linux),  WEBDAV (cloud), serveur FTPS ou SFTP à votre convenance.

#La durée de conservation des archives sur le serveur de destination sera paramètrable et vous devrez gérer la suppression des versions dépassant la durée de conservation.


# URL of the zip file to download

url = 'https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-large-zip-file.zip'

# Step 1: Download the file

download_file(url,'archive.zip')

# Step 2: Unzip the file

unzip_file('archive.zip','extracted_files')

# Step 3: Compare the SQL dump with the file from the previous day

if (compare_files('extracted_files/sample-mpg-file.mpg','sample-mpg-file.mpg') == False):
    # Step 4: Create a new archive with the current date

    current_date = datetime.datetime.now().strftime('%Y%d%m')
    shutil.make_archive(current_date, 'gztar', 'extracted_files')

    # Step 5: Copy the archive to the destination server

    shutil.copy(f'{current_date}.tar.gz', 'destination_server')

