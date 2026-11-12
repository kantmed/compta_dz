# Décisions proposées — Prompt 014

## Décisions déjà validées

- `res.company` représente la société juridique.
- `res.partner` représente les personnes et entités.
- `res.users` et `res.groups` portent la sécurité.
- `ca.accounting.folder` représente le dossier comptable.
- `ca_core` dépend uniquement de `base`.
- Le dossier est fonctionnellement indépendant, mais obligatoirement rattaché à une seule société cliente par `company_id`.
- `ir.access` est le mécanisme natif de sécurité par domaine.

## Recommandations

1. Représenter le cabinet par `res.company`.
2. Ne pas créer `ca.accounting.firm` à ce stade.
3. Étudier `ca.accounting.mandate` dans un module spécialisé futur.
4. Conserver `ca.accounting.folder` comme objet indépendant.
5. Conserver `ca_core` dépendant uniquement de `base`.
6. Utiliser `ir.access` pour les restrictions par domaine.
7. Conserver l'isolation par société et par dossier.

## Hypothèses

- Un cabinet peut être représenté par une société Odoo dédiée.
- Les mandats pourront être gérés dans un module spécialisé.
- Les données comptables natives seront rattachées à un dossier dans les futurs modules.
- Les modalités techniques exactes des exercices comptables restent à confirmer.

## Points nécessitant une décision du propriétaire

- Représentation finale du cabinet.
- Nécessité d'un modèle `ca.accounting.mandate`.
- Gestion des mandats simultanés.
- Gestion des transferts de cabinet.
- Droits du portail client.
- Périmètre des cabinets secondaires.

## Fonctionnalités non encore développées

- cabinets et mandats ;
- portail client ;
- extensions comptables ;
- rattachement des documents comptables natifs à un dossier.
