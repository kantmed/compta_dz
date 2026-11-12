# Rapport — Prompt 014-C : Correction et harmonisation de l'architecture métier

## 1. Contradictions relevées

- Le statut des éléments reportés n'était pas toujours distingué des éléments implémentés.
- La cardinalité entre dossier et mandat devait autoriser plusieurs mandats successifs et simultanés.
- La sécurité future était présentée comme une possibilité, mais doit être distinguée de la sécurité actuellement implémentée.
- Le nombre de tests devait être corrigé à 48 tests exécutés.
- Le périmètre agricole devait rester limité à la comptabilité.
- Le rattachement juridique du dossier à la société devait être clarifié sans remettre en cause son indépendance fonctionnelle.

## 2. Corrections réalisées

- Mise à jour de `architecture_metier_ca_core.md`.
- Création de `decisions_architecture_ca_core.md`.
- Création de `diagramme_architecture_ca_core.mmd`.
- Correction de la cardinalité dossier -> mandat en `1 -> 0..*`.
- Distinction claire entre décisions validées, recommandations, hypothèses et éléments reportés.
- Mise à jour des informations de tests à 48 tests exécutés, 0 échec, 0 erreur.
- Confirmation que `ca_core` dépend uniquement de `base`.
- Clarification du rattachement obligatoire du dossier à une société cliente.

## 3. Décisions conservées

- `res.company` représente la société juridique.
- `res.partner`, `res.users` et `res.groups` sont réutilisés.
- `ca_core` dépend uniquement de `base`.
- `ir.access` gère les restrictions par domaine.
- L'isolation combine la société et le dossier.
- Le dossier est fonctionnellement indépendant, mais rattaché à une seule société cliente.

## 4. Points restant à confirmer

- Relation exacte entre dossier et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Référentiels juridiques et fiscaux algériens.

## 5. Liste des fichiers créés ou modifiés

Créés :
- `ca_core/docs/architecture_metier_ca_core.md`
- `ca_core/docs/decisions_architecture_ca_core.md`
- `ca_core/docs/diagramme_architecture_ca_core.mmd`
- `rapport_prompt_014C.md`
- `inventaire_fichiers_prompt014C.txt`
- `git_status_prompt014C.txt`
- `ca_architecture_prompt014C_audit.zip`

Modifiés :
- aucun fichier Python, XML, CSV ou manifeste.

## 6. Résultats des contrôles

- Cohérence des trois documents : vérifiée.
- Cardinalités du diagramme : corrigées.
- Tests mentionnés : 48 exécutés, 0 échec, 0 erreur.
- `ca_core` indépendant de `account` et `l10n_dz` : confirmé.
- Aucune décision non validée présentée comme définitive.
- Périmètre agricole limité à la comptabilité.

## 7. Confirmation

Aucun fichier Python, XML, CSV ou manifeste n'a été modifié. Aucun modèle n'a été créé. Aucune table ni donnée PostgreSQL n'a été modifiée. Aucun commit Git n'a été effectué.

## 8. Conclusion

PROMPT 014-C TERMINÉ — DOCUMENTATION EN ATTENTE DE VALIDATION INDÉPENDANTE.


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
| Le dossier est fonctionnellement indépendant, mais rattaché à une seule société par `company_id` | Évite la confusion entre identité métier et périmètre juridique |
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
- La relation exacte entre dossier et société.
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

- 48 tests automatisés exécutés pour `ca_core`.
- 0 échec.
- 0 erreur.

Ces résultats concernent `ca_core` et ne constituent pas une validation de la sécurité des futurs modules comptables.


## Annexe B — Contenu intégral de `ca_core/docs/diagramme_architecture_ca_core.mmd`

classDiagram
    class ResCompany {
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
    class IrAccess {
        +model_id
        +group_id
        +operation
        +domain
    }

    ResCompany "1" --> "0..*" CaAccountingFolder : owns
    ResCompany "1" --> "0..*" ResCompany : branches
    ResPartner "1" --> "0..1" ResCompany : partner
    ResUser "1" --> "1" ResPartner : inherits
    ResUser "0..*" --> "0..*" ResCompany : allowed companies
    CaAccountingFolder "0..*" --> "1" ResCompany : company
    CaAccountingFolder "0..*" --> "1" ResUser : manager
    CaAccountingFolder "0..*" --> "0..*" ResUser : collaborators
    CaAccountingFolder "1" --> "0..*" CaAccountingMandate : mandates
    CaAccountingMandate "0..*" --> "1" ResCompany : client company
    CaAccountingMandate "0..*" --> "1" ResCompany : firm
    CaAccountingMandate "0..*" --> "1" CaAccountingFolder : folder
    CaAccountingMandate "0..*" --> "1" ResUser : manager
    IrAccess "0..*" --> "1" ResCompany : domain company
    IrAccess "0..*" --> "0..1" CaAccountingFolder : domain folder
