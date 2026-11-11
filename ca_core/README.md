# ca_core — Socle technique commun

## Présentation

`ca_core` est le module socle technique de Comptabilité Algérienne, basé sur Odoo 20 Community.

## Rôle dans l'architecture

Ce module fournit les éléments techniques communs nécessaires aux futurs modules spécialisés. Il ne contient pas de logique métier comptable.

## Version actuelle

- Version : 20.0.1.0.0

## Dépendances

- `base`

## Licence

- LGPL-3

## Règles de développement

- Réutiliser prioritairement les applications natives Odoo.
- Ne pas créer de moteur parallèle de comptabilité.
- Développer les fonctionnalités métier dans des modules spécialisés dépendant de `ca_core`.
- Respecter les conventions Odoo 20 et la compatibilité multi-société.

## Modules futurs prévus

- Modules comptables spécialisés.
- Modules de référentiels communs.
- Modules de sécurité et de paramétrage.
