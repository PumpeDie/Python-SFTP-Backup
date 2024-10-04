# Documentation Utilisateur

## Introduction

Ce projet est un utilitaire automatisé permettant de télécharger, comparer, archiver et transférer des fichiers sur un serveur distant via SFTP.
Il est conçu pour faciliter la gestion des fichiers, la rétention des données et l'envoi de notifications par email.
L'exécution est automatisée à l'aide d'une tâche **cron**.

## Prérequis

Avant d'utiliser cet utilitaire, assurez-vous que les conditions suivantes soient remplies :

- **Python 3 ou plus** installé
- Accès à un serveur **WEB** valide contenant une archive .zip
- Accès à un serveur **SFTP** valide
- Accès à un service **SMTP** pour l'envoi des emails

## Installation

### 1. Cloner le dépôt

Clonez le projet depuis le dépôt Git en utilisant la commande suivante :

```bash
git clone https://github.com/PumpeDie/Python-SFTP-Backup.git
cd Python-SFTP-Backup
```

### 2. Dépendances Python

Installer les modules Python nécessaires en utilisant la commande suivante :

```bash
pip install paramiko requests
```

## Configuration du fichier `config.ini`

**Serveur Web :**

- Entrer l'URL de votre serveur dans la variable url.
- Entrer le nom du fichier à archiver dans la variable sql_filename.
- Entrer la durée de conservation des archives (en jours) dans retention_days. Si vous ne souhaitez pas les conserver, réglez la variable enable_retention sur False.

**Serveur distant :**

- Entrer le nom d'hôte de votre serveur de sauvegarde dans la variable host.
- Entrer vos identifiants de connexion au serveur sftp dans les variables username et password.

**Mailing :**

- Pour activer la fonctionnalité d'envoi des rapports par mail, régler la variable enable_email sur True.
- Mettre votre adresse mail dans recipient_email. Si vous souhaitez recevoir les rapports sur plusieurs adresses e-mail, séparez-les par des virgules : mail1@gmail.com, mail2@gmail.com, mail3@gmail.com, ...
- Si vous souhaitez recevoir uniquement la notification d'échec ou de succès de la sauvegarde (sans le rapport d'exécution), réglez la variable attach_log sur False.

## Cron 

Les utilisateurs Linux ont la possibilité d'automatiser la procédure d'archivage à l'aide de **Cron** en utilisant la commande suivante :

```bash
crontab -e
```

Ajouter l'entrée suivante pour exécuter la procédure d'archivage tous les jours à 2h du matin :

```bash
0 2 * * * /usr/bin/python3 /chemin/vers/ton/script/archivage.py >> /chemin/vers/ton/log/archivage.log 2>&1
```
 et enregistrer la modification.

 Vérifier que la nouvelle tâche cron a bien été prise en compte en utilisant :

 ```bash
crontab -l
```