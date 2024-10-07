# Documentation Utilisateur

## Introduction

Ce projet est un utilitaire automatisé permettant de télécharger, comparer, archiver et transférer des fichiers sur un serveur distant via SFTP.
Il est conçu pour faciliter la gestion des fichiers, la rétention des données et l'envoi de notifications par email.
L'exécution est automatisée à l'aide d'une tâche **cron**.

## Prérequis

Avant d'utiliser cet utilitaire, assurez-vous que les conditions suivantes soient remplies :

- **Python 3 ou plus** installé
- Accès à un serveur **WEB** valide contenant une archive `.zip`
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

Installez les modules Python nécessaires en utilisant la commande suivante :

```bash
pip install paramiko requests
```

## Configuration du fichier `config.ini`

**Serveur Web :**

- Entrez l'URL du serveur où est stocké l'archive à télécharger dans la variable _*url*_.
- Entrez le nom du fichier à archiver dans la variable _*sql_filename*_.
- Entrez la durée de conservation des archives (en jours) dans _*retention_days*_. Si vous ne souhaitez pas les supprimer, réglez la variable _*enable_retention*_ sur _*False*_.

**Serveur distant :**

- Entrez le nom d'hôte de votre serveur de sauvegarde dans la variable _*host*_.
- Entrez vos identifiants de connexion au serveur sftp dans les variables _*username*_ et _*password*_.
- Entrez le chemin de sauvegarde dans la variable _*remote_directory*_.
- Assurez-vous que l'utilisateur dispose des droits suffisants pour écrire et lire dans le dossier de sauvegarde.

**Mailing :**

- Pour activer la fonctionnalité d'envoi des rapports par mail, régler la variable _*enable_email*_ sur _*True*_.
- Saisissez votre adresse mail dans la variable _*recipient_email*_. Si vous souhaitez recevoir les rapports sur plusieurs adresses e-mail, séparez-les par des virgules : mail1@domaine.com, mail2@domaine.com, mail3@domaine.com, etc.
- Si vous souhaitez recevoir uniquement la notification d'échec ou de succès de la sauvegarde (sans le rapport d'exécution), réglez la variable _*attach_log*_ sur False.

## Cron

Les utilisateurs ont la possibilité d'automatiser la procédure d'archivage à l'aide de **Cron**.
Pour les utilisateurs Linux, il est recommandé d'utiliser un environnement virtuelle Python pour éviter les conflits de dépendance.

Pour activer l'automatisation, ouvrez la configuration des tâches cron en utilisant la commande suivante :

```bash
crontab -e
```

Ajoutez l'entrée suivante pour exécuter la procédure d'archivage tous les jours à 2h du matin :

```bash
0 2 * * * /usr/bin/python3 /chemin/vers/script/archivage.py >> /chemin/vers/logs/cron.log 2>&1
```

Pour vérifier que la nouvelle tâche cron a bien été prise en compte, utilisez la commande suivante :

```bash
crontab -l
```

## Gestion des erreurs

Si une erreur survient pendant l'exécution de l'utilitaire, les logs seront enregistrés dans le fichier spécifié dans la commande Cron et dans le fichier `cron.log`.
Les erreurs courantes incluent :

- **Erreur d'authentification SFTP** : Vérifiez que vos identifiants sont corrects et que vous avez bien configuré le serveur.
- **Erreur de connexion au serveur Web** : Assurez-vous que l'URL du serveur est valide et accessible.
- **Échec de l'envoi d'email** : Assurez-vous que vous avez configuré correctement les paramètres de votre service SMTP .

## Dépannage

- **Cron ne s'exécute pas** : Vérifiez que votre tâche cron a bien été enregistrée en utilisant `crontab -l`. Assurez-vous également que le chemin vers Python et votre fichier `config.ini` est correct.
- **Problème de droits d'accès** : Assurez-vous que votre utilisateur a les permissions nécessaires pour accéder au dossier de sauvegarde SFTP.
