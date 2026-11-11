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
- Justification : mécanisme natif d'Odoo 20.
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

## 9. Points à arbitrer

- Relation exacte entre dossier comptable et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Validation des référentiels juridiques et fiscaux algériens.
