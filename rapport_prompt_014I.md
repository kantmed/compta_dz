# Rapport — Prompt 014-I : Audit final du document d'architecture métier

## 1. Document contrôlé

`ca_core/docs/architecture_metier_ca_core.md`

## 2. Contradictions trouvées

- La relation `partner_id` était présentée comme une association avec une cardinalité absolue.
- La sécurité actuelle et la sécurité cible devaient être distinguées plus explicitement.
- Le mandat devait être identifié comme un modèle futur et non développé.
- Le rattachement société-dossier devait être présenté comme validé.
- Les résultats de tests devaient être délimités au périmètre actuellement développé.

## 3. Corrections effectuées

- Clarification de l'association `partner_id` sans cardinalité absolue.
- Ajout des sections de sécurité actuellement implémentée et sécurité cible.
- Correction des informations de tests à 48 tests exécutés, 0 échec, 0 erreur.
- Conservation du rattachement obligatoire du dossier à une société cliente.
- Mise à jour des documents d'architecture et du diagramme Mermaid.

## 4. Points restant à confirmer

- Relation exacte entre dossier et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Référentiels juridiques et fiscaux algériens.

## 5. Liste des fichiers créés ou modifiés

Créés :
- `rapport_prompt_014I.md`
- `inventaire_prompt014I.txt`
- `git_status_prompt014I.txt`
- `ca_architecture_prompt014I_audit.zip`

Modifiés :
- `ca_core/docs/architecture_metier_ca_core.md`
- `ca_core/docs/decisions_architecture_ca_core.md`
- `ca_core/docs/diagramme_architecture_ca_core.mmd`

## 6. Résultats des contrôles

- Cohérence des trois documents : vérifiée.
- Cardinalités du diagramme : corrigées.
- Absence de l'ancienne hypothèse société-dossier : vérifiée.
- Relation `partner_id` : présentée comme association.
- Mandat : identifié comme futur et non développé.
- Tests : 48 exécutés, 0 échec, 0 erreur.
- Absence de cardinalité définitive pour les exercices : vérifiée.
- Une seule définition `classDiagram` : vérifiée.
- Préservation de l'état Git : vérifiée.
- Archive ZIP : intégrité OK.

## 7. Confirmation

Aucun fichier Python, XML, CSV ou manifeste n'a été modifié. Aucun modèle n'a été créé. Aucune table ni donnée PostgreSQL n'a été modifiée. Aucun commit Git n'a été effectué.

## 8. Conclusion

VALIDÉ


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
