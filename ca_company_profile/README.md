# ca_company_profile

Module de profil juridique, administratif et fiscal des sociétés.

## Fonctionnalités

- Enrichissement du modèle natif `res.company`.
- Forme juridique liée à `ca.legal.form`.
- Identifiants administratifs et fiscaux.
- Informations fiscales.
- Informations administratives.
- Documents justificatifs.

## Dépendances

- `base`
- `ca_core`
- `ca_referential`
- `ca_audit_log`

## Installation

Installer les dépendances, puis installer `ca_company_profile`.

## Sécurité

Le module respecte les droits natifs de `res.company` et l'isolation multi-sociétés.

## Traductions

Français et arabe sont fournis. L'anglais est la langue source.

## Limites

- Pas de gestion multi-établissements.
- Pas de validation officielle des identifiants algériens.
- Pas de portail client.
