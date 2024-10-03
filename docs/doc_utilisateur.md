# Documentation Utilisateur

## Introduction

Ce projet est un utilitaire automatisé permettant de télécharger, comparer, archiver et transférer des fichiers sur un serveur distant via SFTP.
Il est conçu pour faciliter la gestion des fichiers, la rétention des données et l'envoi de notifications par email.
L'exécution est automatisée à l'aide d'une tâche **cron**.

## Prérequis

Avant d'utiliser cet utilitaire, assurez-vous que les conditions suivantes sont remplies :

- **Python 3 ou plus** installé
- Accès à un serveur **WEB** valide avec une archive .zip
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

Installer les modules Python nécessaires installés en utilisant la commande suivante :

```bash
pip install paramiko requests
```

### 3. Configuration du fichier `config.ini`
