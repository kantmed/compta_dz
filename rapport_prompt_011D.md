# Rapport — Prompt 011-D : Finalisation et validation de l'architecture ca_core

## 1. Corrections et arbitrages effectués

- Définition définitive du dossier comptable comme objet métier indépendant.
- Clarification des relations entre société, cabinet, dossier, collaborateur, établissement et exercice.
- Architecture de sécurité multi-niveaux avec isolation par société et par dossier.
- Critères de choix pour les établissements et exploitations agricoles.
- Tableau des modèles de la première version.
- Confirmation que `ca_core` dépend uniquement de `base`.

## 2. Décisions retenues

- Le dossier comptable est indépendant de la société, du cabinet et de l'exercice.
- Une société peut avoir plusieurs dossiers.
- Un dossier peut avoir plusieurs collaborateurs.
- Plusieurs cabinets peuvent intervenir sur une même société.
- La sécurité combine l'isolation native par société et l'isolation complémentaire par dossier.
- Les documents comptables natifs devront être rattachés à un dossier dans les modules spécialisés futurs.
- `ca.accounting.folder` et `ca.audit.log` sont nécessaires en première version.
- `ca.referential` est nécessaire en version minimale.
- `ca.establishment` est conditionnel.
- `ca.legal.form` est fusionné dans `ca.referential`.
- `ca.config` est une extension de `res.config.settings`, pas un modèle séparé.

## 3. Sécurité

La sécurité est définie comme une architecture cible. Elle ne sera considérée comme garantie qu'après implémentation des règles `ir.access`, des champs de rattachement, des tests automatisés et des audits de sécurité.

Les mécanismes natifs protègent par société. L'isolation par dossier nécessitera des règles supplémentaires dans les modules spécialisés dépendant de `account`.

## 4. Fichiers examinés

- odoo/addons/base/models/res_company.py
- odoo/addons/base/models/res_partner.py
- odoo/addons/base/models/res_users.py
- odoo/addons/base/models/res_groups.py
- odoo/addons/base/models/ir_access.py
- odoo/addons/base/security/ir.access.csv
- odoo/addons/l10n_dz/__manifest__.py

## 5. Points encore ouverts

- Relation exacte entre dossier comptable et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Validation des référentiels juridiques et fiscaux algériens.

## 6. Confirmation

Aucun code métier n'a été développé. Aucun fichier Python, XML ou manifest n'a été modifié. Seuls les deux documents d'architecture et ce rapport ont été mis à jour ou créés.

## 7. Conclusion

Architecture finalisée au niveau documentaire. En attente de validation explicite.
