# Rapport — Prompt 008A : Installation parallèle de PostgreSQL 16

## 1. État initial

- Debian : 12 (bookworm)
- PostgreSQL 15.16 actif sur 127.0.0.1:5432
- Cluster 15/main : en ligne
- Base ca_dev sur PG15 : présente, propriétaire odoo20, UTF8
- Espace disque : disponible (~943 Go)
- Aucun dépôt PGDG configuré initialement

## 2. Sauvegarde

- Fichier : /var/backups/postgresql/ca_dev_pg15_20261111_092328.dump
- Format : pg_dump custom (Fc)
- Taille : 16059 octets
- Vérification : archive lisible (pg_restore -l OK)
- Base originale PG15 non modifiée

## 3. Installation PostgreSQL 16

- Dépôt PGDG configuré pour bookworm-pgdg
- Paquets installés : postgresql-16, postgresql-client-16
- Binaire : /usr/lib/postgresql/16/bin/postgres (16.15)

## 4. Cluster PostgreSQL 16

- Cluster : 16/main
- Port : 5433
- Écoute : 127.0.0.1
- Locale : C.UTF-8
- Encodage : UTF8
- État : online

## 5. Rôle et base PostgreSQL 16

- Rôle odoo20 : existant/vérifié, LOGIN=true, CREATEDB=true, SUPERUSER=false, CREATEROLE=false, REPLICATION=false
- Base ca_dev : propriétaire odoo20, UTF8, C.UTF-8
- Test SQL CREATE/INSERT/SELECT/DROP : OK
- Connexion TCP 127.0.0.1:5433 : OK

## 6. Configuration Odoo 20

- /etc/odoo20.conf : modifié uniquement pour db_port = 5433
- Permissions : root:odoo20, 640
- Lecture par odoo20 : OK

## 7. Tests finaux

- PostgreSQL 15 : actif sur 5432
- PostgreSQL 16 : actif sur 5433
- Venv Python : Python 3.12.16
- odoo-bin --version : Odoo Server 20.0
- Port 8069 : libre
- Aucun processus Odoo 20 démarré
- Aucun service Odoo 20 créé
- Odoo 16 : service inactive/disabled, inchangé

## 8. Préservation

- PostgreSQL 15 et ses bases non modifiés
- Odoo 16 non modifié
- Sources Odoo 20 non modifiées
- Dépôt Git projet : commit 309208d...; fichiers rapport non suivis

## 9. Conclusion

PostgreSQL 16 est installé et opérationnel en parallèle de PostgreSQL 15. Odoo 20 est configuré pour utiliser le port 5433. Aucune initialisation Odoo n'a été lancée. En attente de validation explicite.
