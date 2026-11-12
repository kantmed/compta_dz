# Rapport — Prompt 011-C : Consolidation et correction de l'architecture métier de ca_core

## 1. Corrections effectuées

- Correction de la sécurité Odoo 20 : utilisation de `ir.access` comme modèle actif.
- Clarification de la distinction entre permissions d'accès aux modèles et restrictions sur les enregistrements.
- Vérification du format réel de `ir.access.csv` : `id,name,model_id,group_id/id,operation,domain`.
- Clarification des concepts métier : société cliente, cabinet, dossier, exercice, établissement, personne physique, entreprise individuelle, exploitations agricoles, collaborateur, client.
- Documentation des scénarios multi-société et multi-dossiers.
- Renforcement de la stratégie de sécurité et d'isolation.
- Clarification des critères pour les établissements et exploitations agricoles.
- Réexamen des modèles personnalisés envisagés.
- Confirmation que `ca_core` dépend uniquement de `base`.

## 2. Décisions retenues

- Réutiliser `res.company` comme périmètre principal.
- Réutiliser `res.partner`, `res.users` et `res.groups`.
- Ne pas dupliquer les exercices comptables natifs.
- Garder `ca_core` indépendant de `account` et `l10n_dz`.
- Utiliser `ir.access` pour les règles par domaine.
- Séparer les attributs juridiques, fiscaux, comptables et organisationnels.
- Stocker les référentiels dans des données.
- Combiner l'isolation par société et l'isolation par dossier.

## 3. Questions encore ouvertes

- Définition exacte du dossier comptable.
- Relation entre dossier et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Validation des référentiels juridiques et fiscaux algériens.

## 4. Fichiers examinés

- odoo/addons/base/models/res_company.py
- odoo/addons/base/models/res_partner.py
- odoo/addons/base/models/res_users.py
- odoo/addons/base/models/res_groups.py
- odoo/addons/base/models/ir_access.py
- odoo/addons/base/security/ir.access.csv
- odoo/addons/test_web/ir.access.csv
- odoo/addons/test_inherit/security/ir.access.csv
- odoo/addons/l10n_dz/__manifest__.py

## 5. Limites techniques

- La sécurité par dossier nécessitera des extensions dans des modules spécialisés dépendant de `account`.
- `ca_core` ne dépend pas de `account`, donc il ne peut pas modifier directement les modèles comptables natifs.
- Les référentiels juridiques et fiscaux algériens doivent être validés avec des sources officielles.
- Les règles `ir.access` devront être testées avec des utilisateurs représentatifs.

## 6. Confirmation

Aucun code métier n'a été développé. Aucun fichier Python, XML ou manifest n'a été modifié. Seuls les deux documents d'architecture et ce rapport ont été mis à jour ou créés.

## 7. Conclusion

Consolidation et correction terminées. En attente de validation explicite.
