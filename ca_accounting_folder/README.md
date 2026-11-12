# ca_accounting_folder

Module de rattachement des documents comptables natifs d'Odoo à un dossier comptable `ca.accounting.folder`.

## Fonctionnalités

- Champ `ca_accounting_folder_id` sur `account.move`.
- Champ dérivé stocké sur `account.move.line` et `account.payment`.
- Champ calculé stocké sur `ir.attachment`.
- Restrictions d'accès par dossier via `ir.access`.
- Vues et filtres comptables.

## Dépendances

- `ca_core`
- `account`

## Installation

Install `ca_core` and `account` first, then install `ca_accounting_folder`.

## Configuration

No dedicated configuration is required. The module extends native accounting documents with an optional accounting folder.

## Security

Access to accounting folders and related documents is restricted by company and folder assignments through `ca_core` groups and `ir.access` rules.

## Translations

French and Arabic translations are provided in `i18n/`.

## Known limitations

- Payment folder assignment is derived from reconciliation when available.
- Attachment folder resolution currently covers attachments linked to `account.move`.
- No native accounting engine is duplicated.
