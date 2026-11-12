# Rapport — Prompt 014-H : Correction finale de la cardinalité et du périmètre des tests

## 1. Corrections réalisées

- La relation `ResUser --> ResPartner` est représentée comme une association via `partner_id`, sans cardinalité imposée.
- Les résultats de tests sont précisés comme concernant le périmètre de `ca_core`.
- Les 48 tests, 0 échec et 0 erreur sont conservés comme résultats validés.
- Aucune prétention de validation des futurs modules comptables, mandats ou portails n'est faite.

## 2. Contrôles effectués

- Absence de cardinalité imposée à `partner_id` : vérifiée.
- Association technique correctement représentée : vérifiée.
- Résultats des 48 tests correctement délimités : vérifiés.
- Absence de contradiction entre les trois documents : vérifiée.
- Préservation de l'état Git : vérifiée.
- Absence de modification du code et de la base : vérifiée.

## 3. Justificatif des tests

Les résultats de 48 tests, 0 échec et 0 erreur sont repris des rapports et journaux précédents. Ils concernent exclusivement le périmètre développé de `ca_core`, notamment `ca.accounting.folder`, sa sécurité et ses contraintes.

## 4. Fichiers créés ou modifiés

Modifiés :
- `ca_core/docs/architecture_metier_ca_core.md`
- `ca_core/docs/decisions_architecture_ca_core.md`
- `ca_core/docs/diagramme_architecture_ca_core.mmd`

Créés :
- `rapport_prompt_014H.md`
- `inventaire_prompt014H.txt`
- `git_status_prompt014H.txt`
- `ca_architecture_prompt014H_audit.zip`

## 5. Confirmation

Aucun fichier Python, XML, CSV ou manifeste n'a été modifié. Aucun modèle n'a été créé. Aucune table ni donnée PostgreSQL n'a été modifiée. Aucun commit Git n'a été effectué.

## 6. Conclusion

PROMPT 014-H TERMINÉ — DOCUMENTATION EN ATTENTE DE VALIDATION INDÉPENDANTE.


## Annexe A — Contenu intégral de `ca_core/docs/decisions_architecture_ca_core.md`

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
| `ca.config` | Extension de `res.config.settings` |

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


## Annexe B — Contenu intégral de `ca_core/docs/diagramme_architecture_ca_core.mmd`

classDiagram
    class ResCompanyClient {
        <<res.company>>
        +name
        +currency_id
        +parent_id
    }
    class ResCompanyFirm {
        <<res.company>>
        +name
        +currency_id
        +parent_id
    }
    class ResPartner {
        +name
        +is_company
    }
    class ResUser {
        +login
        +company_id
        +company_ids
        +partner_id
    }
    class CaAccountingFolder {
        +name
        +code
        +company_id
        +manager_id
        +collaborator_ids
        +state
    }
    class CaAccountingMandate {
        +firm_company_id
        +folder_id
        +client_company_id
        +mission_type
        +start_date
        +end_date
        +status
        +is_primary
        +manager_id
    }

    ResCompanyClient "1" --> "0..*" CaAccountingFolder : owns
    ResCompanyClient "1" --> "0..*" ResCompanyClient : branches
    ResPartner "1" --> "0..1" ResCompanyClient : partner
    ResUser --> ResPartner : partner_id
    ResUser "0..*" --> "0..*" ResCompanyClient : allowed companies
    CaAccountingFolder "0..*" --> "1" ResUser : manager
    CaAccountingFolder "0..*" --> "0..*" ResUser : collaborators
    CaAccountingFolder "1" --> "0..*" CaAccountingMandate : mandates
    CaAccountingMandate "0..*" --> "1" ResCompanyClient : client company
    CaAccountingMandate "0..*" --> "1" ResCompanyFirm : firm
    CaAccountingMandate "0..*" --> "1" CaAccountingFolder : folder
    CaAccountingMandate "0..*" --> "1" ResUser : manager

    note for ResCompanyClient "Société cliente (res.company)"
    note for ResCompanyFirm "Cabinet comptable (res.company)"
    note for CaAccountingMandate "Modèle futur — non développé"
