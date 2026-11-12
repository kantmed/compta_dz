# Rapport — Prompt 013 : Première implémentation contrôlée de `ca.accounting.folder`

## 1. Résumé

Le modèle `ca.accounting.folder` a été implémenté dans `ca_core`. Le module reste dépendant uniquement de `base`. Les tests automatisés passent.

## 2. Fichiers créés et modifiés

Créés :
- `ca_core/models/accounting_folder.py`
- `ca_core/security/ca_core_groups.xml`
- `ca_core/security/ir.access.csv`
- `ca_core/views/accounting_folder_views.xml`
- `ca_core/tests/__init__.py`
- `ca_core/tests/test_accounting_folder.py`

Modifiés :
- `ca_core/models/__init__.py`
- `ca_core/__manifest__.py`
- `ca_core/docs/architecture_metier_ca_core.md`
- `ca_core/docs/decisions_architecture.md`

## 3. Modèle et champs

Modèle : `ca.accounting.folder`

Champs :
- `name`
- `code`
- `company_id`
- `manager_id`
- `state`
- `description`
- `collaborator_ids`
- `opening_date`
- `closing_date`

## 4. Contraintes SQL et Python

- unicité de `code` par `company_id` ;
- société obligatoire ;
- responsable obligatoire ;
- cohérence société / responsable ;
- cohérence société / collaborateurs ;
- date de clôture non antérieure à la date d'ouverture ;
- société non modifiable après création ;
- transitions de statut contrôlées ;
- dossier archivé non modifiable par un utilisateur ordinaire.

## 5. Groupes et règles de sécurité

Groupes :
- `ca_core.group_ca_core_user`
- `ca_core.group_ca_core_manager`
- `ca_core.group_ca_core_admin`

Hiérarchie :
- manager implique user ;
- admin implique manager.

`ir.access.csv` :
- utilisateur : lecture des dossiers autorisés ;
- gestionnaire : CRUD dans les sociétés autorisées ;
- administrateur : CRUD dans les sociétés autorisées.

Domaines :
- utilisateur : société autorisée et responsable ou collaborateur ;
- gestionnaire et administrateur : société autorisée.

## 6. Commande de mise à jour Odoo

```bash
/opt/odoo20-venv/bin/python /home/odoo20/odoo/odoo-bin -c /etc/odoo20.conf -d ca_dev -u ca_core --test-enable --stop-after-init
```

Exécutée sous l'utilisateur système `odoo20`.

## 7. État du module dans `ca_dev`

- `ca_core` : installed, version 20.0.1.0.0.
- `base` : installed.

## 8. Contrôles multi-société et multi-dossier

Tests automatisés réussis :
- création valide ;
- refus sans société ;
- refus sans responsable ;
- code unique par société ;
- code identique dans deux sociétés ;
- cohérence société / responsable ;
- cohérence société / collaborateurs ;
- dates incohérentes ;
- transitions de statut ;
- dossier archivé non modifiable ;
- création et modification par le gestionnaire ;
- lecture par utilisateur autorisé ;
- refus de lecture non autorisée ;
- refus de création non autorisée ;
- refus de modification non autorisée ;
- refus de changement de société ;
- refus d'ajout de collaborateur non autorisé ;
- refus inter-sociétés ;
- droits du gestionnaire ;
- droits de l'administrateur.

## 9. Erreurs rencontrées et corrections

- Syntaxe XML de la vue de recherche corrigée : les filtres de regroupement sont déclarés directement.
- `_sql_constraints` remplacé par `models.Constraint`.
- Validation explicite des champs obligatoires dans `create`.
- Correction du nom de champ `group_ids` dans les tests.
- Correction du décorateur de `_check_manager_company`.

## 10. Limites restantes

- Pas de gestion des cabinets et mandats.
- Pas de gestion des exercices.
- Pas d'établissements.
- Pas de journalisation dans `ca.audit.log`.
- Pas de portail client.
- L'avertissement `Missing author key` reste non bloquant.

## 11. Confirmation

- Les modules natifs n'ont pas été modifiés.
- Aucun commit Git n'a été effectué.
- Le module `ca_core` reste dépendant uniquement de `base`.

## 12. Statut

IMPLÉMENTATION VALIDÉE
