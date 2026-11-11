# Rapport — Prompt 007 : Configuration sécurisée d'Odoo 20

## 1. Fichier de configuration

- Chemin : /etc/odoo20.conf
- Propriétaire : root:odoo20
- Permissions : 640
- Lecture par odoo20 : OK
- Placeholders : aucun

## 2. Paramètres principaux

- Base : ca_dev
- Hôte PostgreSQL : 127.0.0.1
- Port PostgreSQL : 5432
- Utilisateur PostgreSQL : odoo20
- Filtre de base : ^ca_dev$
- list_db : False
- addons_path : /home/odoo20/odoo/addons,/home/odoo20/addons/comptabilite
- http_interface : 127.0.0.1
- http_port : 8069
- data_dir : /var/lib/odoo20
- logfile : /var/log/odoo20/odoo20.log
- log_level : info
- proxy_mode : False
- workers : 0
- max_cron_threads : 1

## 3. Mots de passe

- Mot de passe PostgreSQL : configuré et non affiché.
- Mot de passe maître Odoo (admin_passwd) : configuré et non affiché.

## 4. Vérifications

- Lecture de /etc/odoo20.conf par odoo20 : OK.
- Connexion PostgreSQL TCP à ca_dev avec le rôle odoo20 : OK.
- Odoo avec configuration : Odoo Server 20.0.
- Aucun placeholder restant.

## 5. Préservation

- Odoo 16 non modifié.
- Dépôt Git projet propre (commit 309208d...).
- Aucun service systemd créé.
- Aucun démarrage de serveur effectué.

## 6. Conclusion

Étape réussie. En attente de validation explicite.
