# Rapport — Prompt 005 : PostgreSQL et base ca_dev

## 1. État initial PostgreSQL

- Service : postgresql / postgresql@15-main actifs.
- Version : PostgreSQL 15.16.
- Écoute : 127.0.0.1:5432.
- Bases initiales : postgres, template0, template1 (toutes UTF8, en_US.UTF-8).
- Rôles initiaux : odoo16 (superuser, createdb), postgres (superuser, etc.).
- Rôle odoo20 : absent initialement.
- Base ca_dev : absente initialement.

## 2. Authentification

- Règle existante applicable : `host all all 127.0.0.1/32 scram-sha-256`.
- Aucune modification de pg_hba.conf requise.
- Aucun rechargement PostgreSQL effectué.

## 3. Rôle PostgreSQL odoo20

- Créé : oui.
- Attributs : LOGIN=true, CREATEDB=true, SUPERUSER=false, CREATEROLE=false, REPLICATION=false.
- Mot de passe : non consigné.

## 4. Base ca_dev

- Créée : oui.
- Propriétaire : odoo20.
- Encodage : UTF8.
- Collation : C.UTF-8.
- Ctype : C.UTF-8.
- Template : template0.

## 5. Tests

- Connexion TCP 127.0.0.1:5432 avec odoo20 : OK.
- Création, insertion, lecture et suppression de table de test : OK.
- Vérification des attributs du rôle : OK.
- Vérification propriétaire/encodage/locale : OK.

## 6. Bases après opération

- ca_dev
- postgres
- template0
- template1

## 7. Préservation Odoo 16

- Service odoo16 : inactive/disabled (état initial).
- Aucune base Odoo 16 modifiée.
- Rôle odoo16 inchangé.

## 8. Conclusion

Étape réussie. En attente de validation explicite.
