# Rapport — Prompt 004 : Utilisateur système et permissions Odoo 20

## 1. État initial

- Utilisateur admin : uid=1000 gid=1000
- Utilisateur odoo20 : absent avant l'opération.
- Groupe odoo20 : absent avant l'opération.
- Répertoires sources/addons : root:root, mode 755.
- /opt/python-3.12 : root:root, mode 755.
- /opt/odoo20-venv : admin:admin, mode 755.
- Odoo 16 : service inactive/disabled (état initial).

## 2. Compte créé

- odoo20 : uid=999, gid=995(odoo20)
- home : /var/lib/odoo20
- shell : /usr/sbin/nologin

## 3. Permissions finales

- /var/lib/odoo20 : odoo20:odoo20, 750
- /var/log/odoo20 : odoo20:odoo20, 750
- /etc/odoo20 : root:odoo20, 750
- /home/odoo20/addons/comptabilite : admin:odoo20, 2770

## 4. Tests

- Lecture sources par odoo20 : OK
- Lecture addons par odoo20 : OK
- Écriture /var/lib/odoo20 par odoo20 : OK
- Écriture /var/log/odoo20 par odoo20 : OK
- Pas d'écriture sur les sources par odoo20 : OK
- Exécution Python 3.12 par odoo20 : OK (Python 3.12.16)
- Odoo --version par odoo20 : OK (Odoo Server 20.0)
- Écriture admin dans addons : OK

## 5. Préservation

- Sources Odoo 20 non modifiées.
- Venv et Python 3.12 non modifiés.
- Odoo 16 inchangé (service inactive/disabled).

## 6. Conclusion

Étape réussie. En attente de validation explicite.
