# Documentation Technique

## Justification des choix techniques

### Serveur Web sous Nginx

Le choix de Nginx comme serveur web repose sur sa capacité à gérer de manière efficace les requêtes HTTP pour servir des fichiers statiques, ainsi que sa fiabilité et sa performance.
Nginx est très utilisé dans des environnements à forte charge, ce qui en fait un choix robuste pour la gestion des fichiers d'archive.

### Serveur distant sous SFTP

SFTP (SSH File Transfer Protocol) est choisi pour son niveau de sécurité élevé en comparaison aux autres protocoles comme FTP. Son port unique (22) permet d'éviter les problèmes de pare-feu et simplifie la configuration réseau.

En utilisant SFTP, les fichiers sont transférés via une connexion SSH, garantissant la confidentialité et l'intégrité des données pendant leur transfert et des mécanismes d'authentification forts par des clés SSH, facilitant la mise en place de connexions automatisées sécurisées (cas de notre projet).

De plus, le protocole SFTP est très bien géré sur différents systèmes, ce qui le rend plus portatif.

## Fonctions

### `download_file(url, filename)`

Télécharge un fichier depuis une URL spécifiée et le sauvegarde localement.

- **Paramètres:**
  - `url` (str): L'URL du fichier à télécharger.
  - `filename` (str): Le nom du fichier local où le contenu sera sauvegardé.

Le téléchargement est réalisé via le module `requests`, qui permet de gérer les connexions HTTP de manière simple et efficace.

### `compare_files(file1, file2)`

Compare le contenu de deux fichiers pour vérifier s'ils sont identiques.

- **Paramètres:**
  - `file1` (str): Chemin du premier fichier.
  - `file2` (str): Chemin du second fichier.
- **Retourne:**
  - `bool`: `True` si les fichiers sont identiques, `False` sinon.

Cette fonction est essentielle pour éviter de transférer des fichiers inchangés, optimisant ainsi l'utilisation des ressources.

### `create_archive(source_dir, output_filename)`

Crée une archive compressée d'un répertoire source.

- **Paramètres:**
  - `source_dir` (str): Chemin du répertoire source à archiver.
  - `output_filename` (str): Nom de l'archive de sortie (sans extension).

L'archivage est réalisé avec `shutil` pour créer un fichier `.tar.gz` de manière simple et portable.

### `create_sftp_connection(host, port, username, password)`

Établit une connexion SFTP avec les informations fournies.

- **Paramètres:**
  - `host` (str): Adresse du serveur SFTP.
  - `port` (int): Port du serveur SFTP.
  - `username` (str): Nom d'utilisateur pour la connexion SFTP.
  - `password` (str): Mot de passe pour la connexion SFTP.
- **Retourne:**
  - `tuple`: Un tuple contenant l'objet SFTP et l'objet de transport.

Utilisation de `paramiko` pour gérer la connexion SSH/SFTP de manière sécurisée.

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

Cette fonction permet de gérer la rétention des fichiers en évitant l'encombrement du serveur distant.

### `send_email(subject, body, to_emails, from_email, log_file=None)`

Envoie un email avec un sujet et un corps spécifiés, et optionnellement attache un fichier de log.

- **Paramètres:**
  - `subject` (str): Sujet de l'email.
  - `body` (str): Corps de l'email.
  - `to_emails` (list): Liste des adresses email des destinataires.
  - `from_email` (str): Adresse email de l'expéditeur.
  - `log_file` (str, optionnel): Chemin du fichier de log à attacher.

L'envoi d'emails via SMTP permet de notifier l'utilisateur sur le succès ou l'échec de l'archivage.

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

## Organisation du code

Le projet est structuré comme suit :

- `src/archivage.py`: Contient le script principal qui orchestre l'ensemble du processus.
- `config/config.ini`: Fichier de configuration pour les paramètres du serveur Web, SFTP et les notifications email.
- `logs/`: Dossier où les logs d'exécution et de cron sont stockés.

## Conclusion

L'automatisation du processus d'archivage permet d'assurer une gestion efficace des fichiers, tout en garantissant la sécurité des transferts et une maintenance minimale grâce à la suppression automatisée des fichiers obsolètes. Les choix de SFTP et de Python permettent de répondre aux exigences de sécurité et de flexibilité.
