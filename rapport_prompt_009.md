# Rapport — Prompt 009 : Création du module socle ca_core

## 1. Structure créée

```text
ca_core/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   └── __init__.py
├── security/
├── views/
├── data/
└── tests/
```

## 2. Manifest

- name : Comptabilité Algérienne — Core
- version : 20.0.1.0.0
- category : Accounting
- summary : Socle technique commun de Comptabilité Algérienne
- license : LGPL-3
- depends : ['base']
- application : False
- installable : True
- auto_install : False

## 3. Vérifications statiques

- Syntaxe Python : OK (`py_compile`).
- Manifest Python valide : OK (`ast.literal_eval`).
- Version : 20.0.1.0.0.
- Licence : LGPL-3.
- Dépendance unique : base.
- Aucune dépendance à account ou l10n_dz.
- Structure des répertoires : OK.

## 4. Détection Odoo

- Addons path personnalisé détecté par Odoo : `/home/odoo20/addons/comptabilite`.
- Module détecté et installable.

## 5. Installation

Commande exécutée sous `odoo20` :

`/opt/odoo20-venv/bin/python /home/odoo20/odoo/odoo-bin -c /etc/odoo20.conf -d ca_dev -i ca_core --stop-after-init`

Résultat : succès, code de sortie 0.

## 6. Mise à jour

Commande exécutée sous `odoo20` :

`/opt/odoo20-venv/bin/python /home/odoo20/odoo/odoo-bin -c /etc/odoo20.conf -d ca_dev -u ca_core --stop-after-init`

Résultat : succès, code de sortie 0.

## 7. Vérifications PostgreSQL

- ca_core dans ir_module_module : state = installed, version = 20.0.1.0.0.
- base : state = installed.
- Aucun module non demandé installé par cette étape.
- Aucun modèle métier créé.

## 8. État Git

- Branche : main.
- Commit de référence : 309208d...
- `git diff --check` : OK.
- Fichiers non suivis : ca_core/ et les rapports précédents.
- Aucun commit effectué (identité Git non configurée).

## 9. Fichiers créés

- ca_core/__init__.py
- ca_core/__manifest__.py
- ca_core/README.md
- ca_core/models/__init__.py
- ca_core/security/ (vide)
- ca_core/views/ (vide)
- ca_core/data/ (vide)
- ca_core/tests/ (vide)

## 10. Problèmes rencontrés

- Aucun problème bloquant.
- Le répertoire addons personnalisé était initialement marqué invalide tant qu'aucun module n'y était présent ; cette situation est résolue.

## 11. Respect des interdictions

- Aucun modèle métier créé.
- Aucun plan comptable, journal, facture, fiscalité ou tiers développé.
- Modules natifs non modifiés.
- l10n_dz non modifié.
- Aucun autre module installé.
- PostgreSQL, Nginx, sources Odoo et services non modifiés.

## 12. Conclusion

Étape réussie : squelette `ca_core` créé, validé, installé et mis à jour sur Odoo 20. En attente de validation explicite.
