# ca_audit_log

Module de traçabilité des opérations sensibles pour Comptabilité Algérienne.

## Fonctionnalités

- Journal central `ca.audit.log`.
- Journalisation des créations, modifications, suppressions et changements d'état.
- Intégration avec `ca.accounting.folder`, `account.move`, `account.move.line`, `account.payment` et `ir.attachment`.
- Protection contre la modification et la suppression des journaux.
- Interface de consultation.

## Dépendances

- `ca_core`
- `ca_accounting_folder`

## Confidentialité

Les champs sensibles sont masqués dans les journaux. Le contenu binaire des pièces jointes n'est jamais journalisé.

## Performance

La journalisation est synchrone. Les champs techniques et binaires sont exclus pour limiter la charge.

## Conservation

Les journaux sont conservés dans la base. Aucune suppression automatique n'est effectuée.
