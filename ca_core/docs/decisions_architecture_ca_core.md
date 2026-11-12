# Décisions d'architecture — `ca_core`

## 1. Décisions validées

| Décision | Justification |
|---|---|
| `ca_core` dépend uniquement de `base` | Garde le socle léger et évite les dépendances circulaires |
| `res.company` représente la société juridique | Réutilise la multi-société et l'isolation native |
| `res.partner` représente les personnes et entités | Évite la duplication des contacts et identifiants |
| `res.users` et `res.groups` portent la sécurité | Authentification et groupes natifs |
| `ir.access` gère les permissions et restrictions par domaine | Mécanisme natif d'Odoo 20 |
| `ca.accounting.folder` est le premier modèle métier implémenté | Suivi métier non fourni par Odoo natif |
| Le dossier est fonctionnellement indépendant, mais rattaché à une seule société cliente par `company_id` | Évite la confusion entre identité métier et périmètre juridique |
| Combinaison de l'isolation par société et par dossier | Un champ `company_id` seul est insuffisant |
| Les attributs juridiques, fiscaux, comptables et organisationnels sont séparés | Facilite la maintenance et la conformité |

## 2. Recommandations d'architecture

| Recommandation | Justification |
|---|---|
| Représenter le cabinet par `res.company` | Réutilise l'isolation native et la devise |
| Utiliser `ir.access` pour les restrictions par domaine | Mécanisme natif d'Odoo 20 |
| Conserver `ca.accounting.folder` comme objet indépendant | Permet plusieurs dossiers par société |
| Stocker les formes juridiques et référentiels dans des données | Facilite la maintenance et la localisation |
| Distinguer société juridique, établissement, site et dossier | Clarifie les périmètres |
| Combiner isolation par société et par dossier | Protège les documents natifs |

## 2.4 Sécurité actuellement implémentée

- Groupes `ca_core_user`, `ca_core_manager`, `ca_core_admin`.
- Règles `ir.access` pour `ca.accounting.folder`.
- Isolation par société et par dossier pour les tests exécutés.
- Responsable et collaborateurs.
- Immutabilité de `company_id`.

## 2.5 Sécurité cible

- Protection des factures, écritures, paiements, pièces jointes, rapports et exports.
- Isolation par mandat.
- Droits des cabinets et collaborateurs.
- Protection du portail client.
- Chaque module spécialisé devra implémenter et tester ses propres règles.


## 3. Hypothèses à confirmer

- La représentation finale du cabinet par `res.company`.
- La gestion des établissements.
- Le périmètre du cabinet comptable.
- Les droits d'accès par dossier.
- L'extension future du portail client.
- Les référentiels juridiques et fiscaux algériens.
- Les modalités techniques exactes des exercices comptables.

## 4. Fonctionnalités non encore développées

- `ca.audit.log`
- `ca.referential`
- `ca.establishment`
- gestion des exercices comptables
- gestion complète des établissements
- cabinets et mandats
- portail client
- extensions comptables
- rattachement des documents comptables natifs à un dossier

## 5. Statut des modèles

| Modèle | Statut |
|---|---|
| `ca.accounting.folder` | Implémenté |
| `ca.audit.log` | Reporté |
| `ca.referential` | Reporté |
| `ca.establishment` | Conditionnel |
| `ca.legal.form` | Fusionné dans `ca.referential` |
| `ca.config` | Non développé |

## 6. Tests

- 48 tests automatisés exécutés pour le périmètre de `ca_core`.
- 0 échec.
- 0 erreur.
- Ces résultats concernent le modèle actuellement développé et ne valident pas les futurs modules comptables.

Ces résultats concernent `ca_core` et ne constituent pas une validation de la sécurité des futurs modules comptables.


## 2.1 Décision validée : rattachement société-dossier

- Décision : un dossier est fonctionnellement indépendant, mais obligatoirement rattaché à une seule société cliente par `company_id`.
- Justification : le dossier possède son identité, son code, son responsable, ses collaborateurs, son état et son périmètre de travail, tout en restant juridiquement lié à la société.
- Statut : validé.
