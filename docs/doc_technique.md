# Documentation Technique

## Justification des choix techniques

### Serveur Web sous Nginx

Quelques lignes

### Serveur distant sous SFTP

Quelques lignes

## Fonctions

### `download_file(url, filename)`

Télécharge un fichier depuis une URL spécifiée et le sauvegarde localement.

- **Paramètres:**
  - `url` (str): L'URL du fichier à télécharger.
  - `filename` (str): Le nom du fichier local où le contenu sera sauvegardé.

### `compare_files(file1, file2)`

Compare le contenu de deux fichiers pour vérifier s'ils sont identiques.

- **Paramètres:**
  - `file1` (str): Chemin du premier fichier.
  - `file2` (str): Chemin du second fichier.
- **Retourne:**
  - `bool`: `True` si les fichiers sont identiques, `False` sinon.

### `create_archive(source_dir, output_filename)`

Crée une archive compressée d'un répertoire source.

- **Paramètres:**
  - `source_dir` (str): Chemin du répertoire source à archiver.
  - `output_filename` (str): Nom de l'archive de sortie (sans extension).

### `create_sftp_connection(host, port, username, password)`

Établit une connexion SFTP avec les informations fournies.

- **Paramètres:**
  - `host` (str): Adresse du serveur SFTP.
  - `port` (int): Port du serveur SFTP.
  - `username` (str): Nom d'utilisateur pour la connexion SFTP.
  - `password` (str): Mot de passe pour la connexion SFTP.
- **Retourne:**
  - `tuple`: Un tuple contenant l'objet SFTP et l'objet de transport.

### `upload_file_sftp(sftp, local_file, remote_path)`

Upload un fichier local vers un répertoire distant via SFTP.

- **Paramètres:**
  - `sftp` (paramiko.SFTPClient): Objet SFTP pour l'upload.
  - `local_file` (str): Chemin du fichier local à uploader.
  - `remote_path` (str): Chemin distant où le fichier sera uploadé.

### `delete_old_files_sftp(sftp, directory, retention_days)`

Supprime les fichiers anciens dans un répertoire distant SFTP selon une durée de rétention spécifiée.

- **Paramètres:**
  - `sftp` (paramiko.SFTPClient): Objet SFTP pour la suppression.
  - `directory` (str): Chemin du répertoire distant.
  - `retention_days` (int): Nombre de jours de rétention des fichiers.

### `send_email(subject, body, to_emails, from_email, log_file=None)`

Envoie un email avec un sujet et un corps spécifiés, et optionnellement attache un fichier de log.

- **Paramètres:**
  - `subject` (str): Sujet de l'email.
  - `body` (str): Corps de l'email.
  - `to_emails` (list): Liste des adresses email des destinataires.
  - `from_email` (str): Adresse email de l'expéditeur.
  - `log_file` (str, optionnel): Chemin du fichier de log à attacher.

## Processus Principal

Le processus principal d'archivage suit les étapes suivantes :

1. Téléchargement d'un fichier zip depuis une URL configurée.
2. Décompression du fichier zip téléchargé.
3. Établissement d'une connexion SFTP.
4. Récupération et comparaison des fichiers SQL locaux et distants.
5. Création et upload d'une nouvelle archive si des modifications sont détectées.
6. Suppression des anciens fichiers sur le serveur distant selon la durée de rétention configurée.
7. Envoi d'emails de notification en cas de succès ou d'échec du processus.
8. Nettoyage des fichiers temporaires.
