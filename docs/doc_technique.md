# Mémoire Technique du Système d'Archivage Automatisé

## Table des matières

1. [Introduction](doc_technique.md#introduction)
2. [Fonctionnalité du système](doc_technique.md#fonctionnalité-du-système)
3. [Justification des choix techniques](doc_technique.md#justification-des-choix-techniques)
4. [Organisation du code](doc_technique.md#organisation-du-code)
5. [Modules importés](doc_technique.md#modules-importés)
6. [Fichier de configuration](doc_technique.md#fichier-de-configuration)
7. [Fonctions](doc_technique.md#fonctions)
8. [Processus Principal](doc_technique.md#processus-principal)
9. [Conclusion](doc_technique.md#conclusion)

## Introduction

Ce projet a pour objectif de développer un système d’archivage automatisé capable de récupérer un fichier au format `.zip` depuis un serveur web via le protocole _HTTPS_, de l'archiver sur un serveur distant via _SFTP_, et de gérer l’historique de ces archives sur le même serveur. Le script télécharge le fichier, le décompresse, compare son contenu avec les archives existantes, et crée une nouvelle archive si des modifications sont détectées. Il envoie également des notifications par email pour informer de l'état du processus et supprime les anciennes archives selon une politique de rétention configurable.

## Fonctionnalité du système

Les fonctionnalités attendues du système d’archivage comprennent :

- **Récupération sécurisée des fichiers** : Téléchargement de fichiers `.zip` depuis un serveur web via le protocole _HTTPS_.
- **Dézippage et contrôle du contenu** : Extraction des fichiers contenus dans l'archive et validation de leur contenu.
- **Archivage et historique** : Création de nouvelles archives compressées au format `.tar.gz` et gestion de l'historique des versions sauvegardées.
- **Transfert vers le serveur distant** : Envoi des fichiers archivés sur un serveur distant en utilisant le protocole _SFTP_ pour garantir la sécurité des transferts.
- **Notifications par e-mail** : Envoi de notifications par e-mail aux administrateurs avec les rapports de log en pièce jointe, pour informer de l'état du processus.
- **Gestion de la durée de conservation** : Suppression des fichiers anciens sur le serveur distant selon une politique de rétention configurable.

## Justification des choix techniques

### Serveur Web sous Nginx

Le choix de Nginx comme serveur web repose sur sa capacité à gérer de manière efficace les requêtes HTTP pour servir des fichiers statiques, ainsi que sa fiabilité et sa performance.
Nginx est très utilisé dans des environnements à forte charge, ce qui en fait un choix robuste pour la gestion des fichiers d'archive.

### Serveur distant sous SFTP

SFTP (SSH File Transfer Protocol) est choisi pour son niveau de sécurité élevé en comparaison aux autres protocoles comme FTP. Son port unique (22) permet d'éviter les problèmes de pare-feu et simplifie la configuration réseau.

En utilisant SFTP, les fichiers sont transférés via une connexion SSH, garantissant la confidentialité et l'intégrité des données pendant leur transfert et des mécanismes d'authentification forts par des clés SSH, facilitant la mise en place de connexions automatisées sécurisées (cas de notre projet).

De plus, le protocole SFTP est très bien géré sur différents systèmes, ce qui le rend plus portatif.

## Organisation du code

Le projet est structuré comme suit :

- `src/archivage.py`: Contient le script principal qui orchestre l'ensemble du processus.
- `config/config.ini`: Fichier de configuration pour les paramètres du serveur Web, SFTP et les notifications email.
- `logs/`: Dossier où les logs d'exécution et de cron sont stockés.

Schéma de l'arborescence du projet :

```bash
.
├── config
│   └── config.ini
├── docs
│   ├── doc_technique.md
│   └── doc_utilisateur.md
├── logs
│   └── archive.log
├── src
│   └── archivage.py
└── README.md
```

## Modules importés

Le script utilise plusieurs modules Python pour accomplir ses différentes tâches. Voici une brève explication de chaque module importé :

- `time`: Fournit des fonctions pour manipuler le temps, comme obtenir l'heure actuelle.
- `requests`: Permet d'envoyer des requêtes HTTP pour télécharger des fichiers depuis le web.
- `os`: Fournit des fonctions pour interagir avec le système d'exploitation, comme la gestion des fichiers et des répertoires.
- `datetime`: Permet de manipuler des dates et des heures de manière simple et efficace.
- `shutil`: Offre des fonctions pour la manipulation de fichiers et de répertoires, y compris la création d'archives.
- `paramiko`: Fournit des outils pour établir des connexions SSH et SFTP sécurisées.
- `logging`: Utilisé pour enregistrer des messages de log, facilitant le suivi et le débogage du script.
- `socket`: Permet de créer des connexions réseau et de gérer les communications via IP et ports.
- `smtplib`: Utilisé pour envoyer des emails via le protocole SMTP.
- `ssl`: Offre des fonctions pour gérer les connexions sécurisées SSL/TLS.
- `email.mime.multipart`, `email.mime.text`, `email.encoders`, `email.mime.base`: Fournissent des outils pour créer et manipuler des emails avec des pièces jointes.
- `configparser`: Permet de lire et de gérer les fichiers de configuration au format `.ini`.

Ces modules sont essentiels pour assurer le bon fonctionnement du script, en permettant la gestion des fichiers, la communication sécurisée avec les serveurs, et l'envoi de notifications par email.

## Fichier de configuration

Le fichier `config.ini` contient les paramètres de configuration nécessaires pour le bon fonctionnement du script d'archivage. Voici une explication de chaque variable et comment les configurer :

### [DEFAULT]

- **url**: L'URL du fichier ZIP à télécharger. Par exemple, `https://example.com/archive.zip`.
- **sql_filename**: Le nom du fichier SQL à extraire du fichier ZIP. Par exemple, `dumpfile.sql`.
- **retention_days**: Le nombre de jours pendant lesquels les fichiers doivent être conservés sur le serveur distant. Par exemple, `7`.
- **enable_retention**: Active ou désactive la suppression automatique des anciens fichiers. Utilisez `True` pour activer et `False` pour désactiver.

### [SFTP]

- **host**: L'adresse IP ou le nom de domaine du serveur SFTP. Par exemple, `sftp.example.com`.
- **port**: Le port utilisé pour la connexion SFTP. Par défaut, `22`.
- **username**: Le nom d'utilisateur pour la connexion SFTP. Par exemple, `user`.
- **password**: Le mot de passe pour la connexion SFTP. Par exemple, `password`.
- **remote_directory**: Le répertoire distant où les fichiers seront uploadés. Par exemple, `data`.

### [EMAIL]

- **enable_email**: Active ou désactive l'envoi d'emails de notification. Utilisez `True` pour activer et `False` pour désactiver.
- **use_tls**: Active ou désactive l'utilisation de TLS pour la connexion SMTP. Utilisez `True` pour activer et `False` pour désactiver.
- **smtp_server**: L'adresse du serveur SMTP. Par exemple, `smtp.gmail.com`.
- **smtp_port**: Le port utilisé pour la connexion SMTP. Par exemple, `465`.
- **smtp_username**: Le nom d'utilisateur pour la connexion SMTP. Par exemple, `user@gmail.com`.
- **smtp_password**: Le mot de passe pour la connexion SMTP. Par exemple, `password`.
- **sender_email**: L'adresse email de l'expéditeur. Par exemple, `user@gmail.com`.
- **recipient_email**: Les adresses email des destinataires, séparées par des virgules. Par exemple, `recipient1@gmail.com, recipient2@gmail.com`.
- **subject_success**: Le sujet de l'email en cas de succès. Par exemple, `Sauvegarde réussie`.
- **subject_failure**: Le sujet de l'email en cas d'échec. Par exemple, `Échec de la sauvegarde`.
- **attach_log**: Active ou désactive l'attachement du fichier de log à l'email. Utilisez `True` pour activer et `False` pour désactiver.

### [LOGGING]

- **log_file**: Le chemin du fichier de log. Par exemple, `logs/archive.log`.

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

## Conclusion

L'automatisation du processus d'archivage permet d'assurer une gestion efficace des fichiers, tout en garantissant la sécurité des transferts et une maintenance minimale grâce à la suppression automatisée des fichiers obsolètes.
Les choix de SFTP et de Python permettent de répondre aux exigences de sécurité et de flexibilité.
