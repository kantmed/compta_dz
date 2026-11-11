# Rapport — Prompt 011 : Étude et conception de l'architecture métier de ca_core

## 1. Fichiers natifs Odoo examinés

- odoo/addons/base/models/res_company.py
- odoo/addons/base/models/res_partner.py
- odoo/addons/base/models/res_users.py
- odoo/addons/base/models/res_groups.py
- odoo/addons/base/models/ir_access.py
- odoo/addons/l10n_dz/__manifest__.py

## 2. Modèles réutilisables identifiés

- res.company : société, succursales, devise, TVA, multi-société.
- res.partner : personnes physiques et entités, adresses, identifiants.
- res.users : utilisateurs, groupes, sociétés autorisées.
- res.groups : groupes et implications.
- ir.model.access : droits CRUD par modèle et groupe.
- ir.access : règles par domaine dans Odoo 20.
- l10n_dz : plan comptable et taxes algériens, via account.

## 3. Options d'architecture étudiées

- Option A : une société Odoo par entité juridique.
- Option B : un modèle ca.accounting.folder transverse pour le suivi métier.
- Recommandation : combiner A et B.

## 4. Architecture recommandée

- res.company représente la société juridique et le périmètre de données.
- ca.accounting.folder représente le dossier de travail du cabinet.
- Les établissements sont liés à la société.
- Les utilisateurs et groupes natifs portent la sécurité.
- ir.access fournit les restrictions par domaine.
- ca_core reste indépendant de account et l10n_dz.

## 5. Relations entre les objets

- res.company 1..n ca.accounting.folder
- ca.accounting.folder n..1 res.company
- ca.accounting.folder n..1 responsable (res.users)
- ca.establishment n..1 res.company
- ca.audit.log n..1 res.users et n..0..1 res.company

## 6. Décisions prises

- Réutiliser res.company, res.partner, res.users et res.groups.
- Ne pas dupliquer les exercices comptables.
- Garder ca_core indépendant de account et l10n_dz.
- Utiliser ir.access pour les règles par domaine.
- Séparer les attributs juridiques, fiscaux, comptables et organisationnels.
- Stocker les référentiels dans des données.

## 7. Points à valider

- Définition exacte du dossier comptable.
- Relation dossier / société.
- Gestion des établissements.
- Gestion des cabinets et collaborateurs.
- Droits d'accès par dossier.
- Extension future du portail client.
- Référentiels juridiques et fiscaux algériens.

## 8. Risques identifiés

- Duplication de fonctionnalités natives.
- Isolation insuffisante.
- Dépendances circulaires.
- Sur-conception.
- Incertitudes réglementaires.

## 9. Confirmation

Aucun code métier n'a été développé. Seuls les deux documents demandés ont été créés. Aucun fichier Python, XML ou manifest n'a été modifié.

## 10. Conclusion

Étude documentaire terminée. En attente de validation explicite.
