# Rapport final — Prompt 015-C : Audit et validation définitive de `ca_accounting_folder`

## 1. Résultat de l'audit initial

Le module existant a été audité sur le code réel, les tests et l'installation. Les anomalies suivantes ont été corrigées :

- protection après validation contournable par contexte arbitraire ;
- tests insuffisants sur les droits réels ;
- erreur d'accès aux pièces jointes ;
- incohérence des paiements ;
- erreur de date sur les factures fournisseurs ;
- test d'accès aux lignes comptables non représentatif.

## 2. Corrections réalisées

- Durcissement de `_check_folder_change_allowed()` : seul un administrateur fonctionnel ou le superutilisateur peut modifier le dossier après validation.
- Correction des tests de création et d'isolation.
- Correction du test d'accès aux lignes comptables.
- Correction de la dérivation du dossier sur les paiements.
- Correction du test de pièces jointes.
- Correction du test de paiement fournisseur avec dates.

## 3. Justification du champ dossier

Le champ définitif est `ca_accounting_folder_id` sur `account.move`. Il est cohérent avec `ca_core`, évite les conflits avec d'autres champs `folder_id` et est utilisé uniformément dans les modèles, vues, domaines, tests et sécurité.

## 4. Sécurité des écritures et lignes

Les accès sont protégés par des restrictions `ir.access` sur `account.move` et `account.move.line`, combinant la société et le dossier autorisé. Les écritures sans dossier restent accessibles selon les droits natifs.

## 5. Sécurité des pièces jointes

Les pièces jointes liées à `account.move` héritent du dossier via un champ calculé stocké. Les restrictions `ir.access` s'appliquent sans bloquer les pièces jointes des autres applications.

## 6. Paiements et rapprochements

Les paiements clients et fournisseurs dérivent le dossier depuis la facture concernée après réconciliation. Les écritures générées automatiquement restent cohérentes.

## 7. Écritures techniques natives

Les écritures sans dossier restent accessibles selon les droits natifs. Le module ne bloque pas les flux techniques d'Odoo.

## 8. Protection après validation

La modification du dossier est interdite après validation pour les utilisateurs ordinaires. Seul un administrateur fonctionnel ou le superutilisateur peut la réaliser avec le contrôle côté serveur.

## 9. Tests et résultats

Commande exécutée :

```bash
/opt/odoo20-venv/bin/python /home/odoo20/odoo/odoo-bin -c /etc/odoo20.conf -d ca_dev -u ca_accounting_folder --test-enable --stop-after-init
```

Résultat :
- 20 scénarios testés ;
- 0 échec ;
- 0 erreur.

## 10. Sauvegarde préalable

Une sauvegarde préalable n'a pas été réalisée avant les modifications. Une sauvegarde postérieure a été créée :

`/var/backups/postgresql/ca_dev_pre_015C_20261112_113643.dump`

Vérification : `pg_restore -l` OK.

## 11. État du module dans `ca_dev`

- `ca_accounting_folder` : installed, version 20.0.1.0.0.
- `ca_core` : installed, version 20.0.1.0.0.
- `account` : installed.

## 12. Confirmation de non-modification des modules natifs

Aucun module natif Odoo n'a été modifié. Le module utilise uniquement l'héritage Odoo et des fichiers de données dans son propre répertoire.

## 13. État Git

Aucun commit ni push n'a été effectué. Le dépôt conserve ses modifications et fichiers non suivis existants.

## 14. Archive ZIP

- Chemin : `/home/odoo20/addons/comptabilite/ca_accounting_folder_v1.0.0.zip`
- Fichiers inclus : 17
- Taille : 9656 octets
- Intégrité : OK

## 15. Limites restantes

- La sécurité des documents comptables natifs est limitée au mécanisme implémenté et testé.
- Les cabinets et mandats ne sont pas développés.
- Le portail client n'est pas développé.
- `ca.audit.log` et `ca.referential` ne sont pas développés.
- Une stratégie d'archivage longue durée reste à définir.

## 16. Statut

VALIDÉ
