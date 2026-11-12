# Décisions d'architecture — `ca_core`

## 1. Décision : réutiliser `res.company` comme périmètre principal

- Décision : utiliser `res.company` pour représenter la société juridique et le périmètre de données.
- Justification : Odoo fournit nativement la multi-société, la devise, les coordonnées et l'isolation.
- Alternative examinée : créer un modèle `ca.legal.entity` distinct.
- Statut : recommandé.

## 2. Décision : réutiliser `res.partner` pour les personnes et entités

- Décision : utiliser `res.partner` pour les personnes physiques et les entités.
- Justification : évite la duplication des contacts, adresses et identifiants.
- Alternative examinée : créer des modèles `ca.person` et `ca.entity`.
- Statut : recommandé.

## 3. Décision : réutiliser `res.users` et `res.groups`

- Décision : utiliser les utilisateurs et groupes natifs.
- Justification : Odoo gère déjà l'authentification, les groupes implicites et les contraintes.
- Alternative examinée : créer des modèles de collaborateurs et de rôles.
- Statut : recommandé.

## 4. Décision : ne pas dupliquer les exercices comptables

- Décision : laisser la gestion des exercices aux modules comptables natifs.
- Justification : évite une duplication fonctionnelle et des incohérences.
- Alternative examinée : créer `ca.fiscal.year`.
- Statut : recommandé.

## 5. Décision : `ca_core` indépendant de `account` et `l10n_dz`

- Décision : `ca_core` dépend uniquement de `base`.
- Justification : évite les dépendances circulaires et garde le socle léger.
- Alternative examinée : dépendre directement de `account`.
- Statut : recommandé.

## 6. Décision : utilisation d'`ir.access` pour les règles par domaine

- Décision : utiliser `ir.access` pour les restrictions basées sur des domaines.
- Justification : mécanisme natif d'Odoo 20. Le format `ir.access.csv` est `id,name,model_id,group_id/id,operation,domain`.
- Alternative examinée : logique applicative personnalisée.
- Statut : recommandé.

## 7. Décision : séparation des attributs

- Décision : séparer les caractéristiques juridiques, fiscales, comptables et organisationnelles.
- Justification : facilite la maintenance et la conformité.
- Alternative examinée : modèle unique avec tous les champs.
- Statut : recommandé.

## 8. Décision : référentiels de données

- Décision : stocker les formes juridiques et données de référence dans des données, pas dans le code.
- Justification : facilite la maintenance et la localisation.
- Alternative examinée : constantes Python.
- Statut : recommandé.

## 9. Décision : sécurité multi-niveaux

- Décision : combiner l'isolation par société et l'isolation par dossier.
- Justification : un champ `company_id` seul ne protège pas les documents natifs par dossier.
- Alternative examinée : se baser uniquement sur le multi-société natif.
- Statut : recommandé.

## 10. Décision : définition du dossier comptable

- Décision : le dossier est un objet métier indépendant de la société, du cabinet et de l'exercice.
- Justification : permet le suivi, le transfert, la clôture et l'archivage sans confondre les périmètres.
- Alternative examinée : équivalence dossier = société ou dossier = exercice.
- Statut : recommandé.

## 11. Décision : modèles de la première version

| Modèle | Rôle | Nécessité en première version | Dépendances | Justification |
|---|---|---|---|---|
| `ca.accounting.folder` | Dossier comptable | Oui | `base` | Suivi métier non fourni par Odoo natif |
| `ca.audit.log` | Journalisation sensible | Oui | `base` | Traçabilité des opérations sensibles |
| `ca.referential` | Référentiels communs | Oui, version minimale | `base` | Formes juridiques et données de référence |
| `ca.establishment` | Établissement ou site | Conditionnel | `base` | À créer si le besoin de site distinct est confirmé |
| `ca.legal.form` | Forme juridique | Non en première version | `base` | Fusionné dans `ca.referential` |
| `ca.config` | Paramètres | Non comme modèle séparé | `base` | Extension de `res.config.settings` |

## 12. Points à arbitrer

- Relation exacte entre dossier comptable et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Validation des référentiels juridiques et fiscaux algériens.

## 13. Implémentation réelle

- `ca.accounting.folder` est le premier modèle métier implémenté.
- Les contraintes sont implémentées côté serveur.
- La sécurité utilise `ir.access` avec des domaines par société et par dossier.
- Les tests automatisés couvrent les contraintes et l'isolation.
- Les cabinets, mandats, exercices, établissements et journalisation sont reportés.


## 13. Statut des fonctionnalités

### Implémentées

- `ca.accounting.folder`
- sécurité de base par société et par dossier
- vues et menus
- tests automatisés

### Futures

- cabinets et mandats
- portail client
- extensions comptables

### Reportées

- `ca.audit.log`
- `ca.referential`
- `ca.establishment`
- gestion des exercices
