# Documentation Technique

## Justification des choix techniques

### Serveur Web sous Nginx

Le choix de Nginx comme serveur web repose sur sa capacité à gérer de manière efficace les requêtes HTTP pour servir des fichiers statiques, ainsi que sa fiabilité et sa performance.
Nginx est très utilisé dans des environnements à forte charge, ce qui en fait un choix robuste pour la gestion des fichiers d'archive.

### Serveur distant sous SFTP

SFTP (SSH File Transfer Protocol) est choisi pour son niveau de sécurité élevé en comparaison aux autres protocoles comme FTP.
En utilisant SFTP, les fichiers sont transférés via une connexion SSH, garantissant la confidentialité et l'intégrité des données pendant leur transfert.
Le choix de SFTP permet également d'utiliser des mécanismes d'authentification forts, tels que les clés SSH.
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

Cette fonction est chargée d'envoyer des notifications par email, ce qui est essentiel pour informer les utilisateurs des résultats du processus d'archivage (succès, échec ou absence de modifications).
Elle prend en charge l'envoi d'un email à un ou plusieurs destinataires et peut également inclure un fichier de log en pièce jointe, permettant aux administrateurs de vérifier les détails du processus.

#### Détails de l'implémentation :

1. **Création du message :**

   - La fonction construit un email en ajoutant un sujet, un corps de message, ainsi que les adresses des destinataires.
   - Elle utilise la classe `MIMEMultipart` pour permettre l'ajout d'un fichier en pièce jointe, si nécessaire.

2. **Gestion des destinataires :**

   - La fonction accepte à la fois une seule adresse email sous forme de chaîne de caractères et plusieurs adresses sous forme de liste.
     Si une seule adresse est fournie, elle est convertie en liste pour uniformiser le traitement des destinataires.

3. **Ajout d'une pièce jointe (facultatif) :**

   - Si un chemin de fichier est fourni dans `log_file`, la fonction vérifie si le fichier existe et l'attache à l'email.
     Ce fichier, souvent un fichier de log, permet aux administrateurs d'examiner le déroulement du processus d'archivage.

4. **Connexion au serveur SMTP :**

   - La fonction supporte l'envoi d'emails via une connexion sécurisée utilisant soit STARTTLS (TLS), soit SSL. La méthode utilisée dépend de la configuration choisie (`use_tls`).
   - Les paramètres SMTP (serveur, port, nom d'utilisateur et mot de passe) sont utilisés pour se connecter au serveur de messagerie et authentifier l'envoi de l'email.

5. **Envoi de l'email :**

   - Une fois le message prêt, la fonction utilise `server.sendmail` pour envoyer l'email aux destinataires.

6. **Gestion des erreurs :**

   - En cas d'échec (par exemple, une mauvaise configuration du serveur SMTP ou une erreur d'envoi), la fonction capture l'exception et enregistre une erreur dans le fichier de log.
     Cela permet de suivre les éventuelles erreurs dans le processus de notification.

7. **Nettoyage :**
   - Enfin, que l'envoi ait réussi ou échoué, la fonction ferme la connexion SMTP.

## Processus Principal

Le processus principal d'archivage suit plusieurs étapes séquentielles, permettant de télécharger, comparer, archiver et transférer des fichiers vers un serveur distant via SFTP. Voici les étapes détaillées :

1. **Téléchargement du fichier ZIP**

   - Le processus commence par le téléchargement d'un fichier ZIP depuis une URL configurée, qui est stocké dans une variable.
     Si le fichier n'est pas disponible ou si le téléchargement échoue, une erreur est loguée et le processus s'arrête.

2. **Décompression du fichier ZIP**

   - Une fois le fichier ZIP téléchargé, il est décompressé dans un dossier temporaire pour extraire son contenu, notamment un fichier SQL à comparer.

3. **Établissement de la connexion SFTP**

   - Le script établit une connexion SFTP avec le serveur distant en utilisant les informations d'authentification configurées (adresse du serveur, port, nom d'utilisateur et mot de passe).

4. **Récupération et comparaison des fichiers**

   - Le fichier SQL téléchargé est comparé à la dernière archive `.tar.gz` disponible sur le serveur distant.
     Si le fichier local diffère du fichier distant, cela indique une modification dans les fichiers du serveur web.

5. **Création et upload de la nouvelle archive**

   - Si des modifications sont détectées, une nouvelle archive `.tar.gz` est créée avec un nom basé sur la date du jour.
     Cette archive est ensuite uploadée sur le serveur distant via la connexion SFTP établie.

6. **Suppression des anciens fichiers sur le serveur distant**

   - Si la fonctionnalité de rétention des fichiers est activée, les anciens fichiers présents sur le serveur distant sont supprimés en fonction de la durée de rétention configurée (exprimée en jours).

7. **Envoi d'un email de notification**

   - Une notification est envoyée par email pour indiquer le succès du processus d'archivage et le transfert de la nouvelle archive sur le serveur distant.
     Si aucune modification n'est détectée, un email distinct indiquant qu'aucune nouvelle archive n'a été créée est envoyé.
     Il est également possible d'attacher le fichier de log à l'email.

8. **Nettoyage des fichiers temporaires**
   - À la fin du processus, tous les fichiers temporaires (fichiers ZIP, archives, répertoires extraits) sont supprimés pour éviter l'encombrement du système.

En cas d'erreur à n'importe quelle étape, une notification d'échec est envoyée par email, incluant une description de l'erreur et, éventuellement, le fichier de log pour plus de détails.

## Organisation du code

Le projet est structuré comme suit :

- `src/archivage.py`: Contient le script principal qui orchestre l'ensemble du processus.
- `config/config.ini`: Fichier de configuration pour les paramètres du serveur Web, SFTP et les notifications email.
- `logs/`: Dossier où les logs d'exécution et de cron sont stockés.

## Conclusion

L'automatisation du processus d'archivage permet d'assurer une gestion efficace des fichiers, tout en garantissant la sécurité des transferts et une maintenance minimale grâce à la suppression automatisée des fichiers obsolètes.
Les choix de SFTP et de Python permettent de répondre aux exigences de sécurité et de flexibilité.
