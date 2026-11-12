# Rapport — Prompt 014 : Étude d'architecture des cabinets comptables et des mandats

## 1. Objet de l'étude

Étude fonctionnelle et technique de la gestion des cabinets comptables et des mandats, avant toute implémentation.

Aucun modèle n'a été créé et aucun code n'a été modifié.

## 2. Documents et fichiers examinés

- `ca_core/docs/architecture_metier_ca_core.md`
- `ca_core/docs/decisions_architecture_ca_core.md`
- `ca_core/models/accounting_folder.py`
- `ca_core/__manifest__.py`
- Rapports précédents du projet
- Code source Odoo 20 pour `res.company`, `res.partner`, `res.users`, `res.groups` et `ir.access`

## 3. Constats principaux

- `res.company` représente la société juridique et le périmètre natif de données.
- `res.partner` représente les personnes et entités.
- `res.users` et `res.groups` portent la sécurité.
- `ca.accounting.folder` représente le dossier comptable.
- Odoo 20 utilise `ir.access` pour les permissions et restrictions par domaine.
- `ca_core` dépend uniquement de `base`.

## 4. Scénarios métier étudiés

1. Un cabinet comptable gère plusieurs sociétés clientes.
2. Une société cliente peut avoir plusieurs dossiers comptables.
3. Une société peut être suivie par plusieurs cabinets.
4. Plusieurs cabinets peuvent intervenir pour des missions différentes.
5. Un dossier possède un cabinet principal à un instant donné.
6. Le cabinet principal peut changer.
7. Un cabinet peut être remplacé sans perte d'historique.
8. Un mandat peut être limité à une période ou à une mission.
9. Un cabinet peut avoir plusieurs responsables et collaborateurs.
10. Un collaborateur peut intervenir sur plusieurs dossiers et clients selon ses autorisations.

## 5. Représentation du cabinet

### Option A — Société Odoo (`res.company`)

Avantages :
- réutilise l'isolation multi-société native ;
- gère la devise, la TVA et le périmètre de données ;
- compatible avec les modules comptables.

Inconvénients :
- nécessite une gouvernance claire des sociétés ;
- les utilisateurs peuvent accéder à plusieurs sociétés selon leurs autorisations.

### Option B — Partenaire (`res.partner`)

Avantages :
- simple pour représenter une personne ou une structure ;
- réutilise les contacts et adresses.

Inconvénients :
- ne fournit pas seul l'isolation multi-société ;
- insuffisant pour les droits et le périmètre de données.

### Option C — Modèle spécifique `ca.accounting.firm`

Avantages :
- modèle métier explicite ;
- meilleure lisibilité fonctionnelle.

Inconvénients :
- risque de duplication avec `res.company` ;
- complexité supplémentaire ;
- nécessite des règles d'accès supplémentaires.

### Recommandation

Recommander la représentation du cabinet par `res.company`, complétée par des données métier si nécessaire. Un modèle spécifique `ca.accounting.firm` n'est pas justifié à ce stade.

## 6. Gestion des mandats

Un éventuel modèle `ca.accounting.mandate` devrait contenir :

- société cliente ;
- cabinet concerné ;
- dossier concerné ;
- type de mission ;
- date de début ;
- date de fin ;
- statut ;
- caractère principal ou secondaire ;
- responsable du mandat ;
- collaborateurs autorisés ;
- motif de transfert ou de résiliation ;
- historique des changements.

Contraintes à étudier :

- absence de chevauchement incompatible entre mandats principaux ;
- un seul cabinet principal par dossier et par période ;
- cohérence entre société, dossier et cabinet ;
- impossibilité de supprimer un mandat historique ;
- conservation des mandats terminés ou résiliés ;
- gestion des changements de responsable.

Les mandats simultanés peuvent être compatibles si leurs missions et périmètres sont distincts.

## 7. Relations proposées

- `res.company` (société cliente) 1..n `ca.accounting.folder`
- `ca.accounting.folder` n..1 `res.company` (société cliente)
- `ca.accounting.folder` n..1 cabinet (`res.company` ou modèle spécialisé)
- `ca.accounting.folder` n..1 responsable (`res.users`)
- `ca.accounting.folder` n..0..1 exercice comptable natif
- `ca.accounting.folder` n..m collaborateurs autorisés (`res.users`)
- `ca.establishment` n..1 `res.company`
- `ca.establishment` n..0..1 `ca.accounting.folder`
- `ca.audit.log` n..1 `res.users`
- `ca.audit.log` n..0..1 `res.company`
- `ca.audit.log` n..0..1 objet audité
- `ca.accounting.mandate` n..1 société cliente
- `ca.accounting.mandate` n..1 cabinet
- `ca.accounting.mandate` n..1 dossier
- `ca.accounting.mandate` n..1 responsable

Le dossier est fonctionnellement indépendant, mais obligatoirement rattaché à une société cliente par `company_id`.

## 8. Sécurité

La sécurité doit combiner :

- l'isolation native par société ;
- l'isolation complémentaire par dossier ;
- les droits des collaborateurs ;
- les droits du cabinet ;
- les droits du portail client.

Risques à étudier :

- accès indirect aux données d'un autre cabinet ;
- accès aux documents comptables natifs ;
- exports, impressions et rapports ;
- accès via relations Many2one et Many2many ;
- accès RPC et appels serveur.

La sécurité devra s'appuyer sur `ir.access` et les mécanismes natifs Odoo, avec des tests automatisés.

## 9. Compatibilité avec l'architecture existante

Respecter :

- `res.company` représente l'entité juridique.
- `res.partner` représente les personnes et entités.
- `res.users` représente les utilisateurs.
- `ca.accounting.folder` représente le dossier comptable.
- `ca_core` dépend uniquement de `base`.
- Aucun moteur comptable parallèle.
- Aucun doublon des fonctionnalités natives Odoo.
- Préfixe `ca_` pour les nouveaux modules.
- Ne pas modifier les modules natifs Odoo.
- Ne pas ajouter `account` ou `l10n_dz` à `ca_core`.

## 10. Décisions recommandées

1. Représenter le cabinet par `res.company`.
2. Ne pas créer `ca.accounting.firm` à ce stade.
3. Étudier `ca.accounting.mandate` dans un module spécialisé futur.
4. Conserver `ca.accounting.folder` comme objet indépendant.
5. Conserver `ca_core` dépendant uniquement de `base`.
6. Utiliser `ir.access` pour les restrictions par domaine.
7. Conserver l'isolation par société et par dossier.

## 11. Points nécessitant une décision du propriétaire

- Représentation finale du cabinet.
- Nécessité d'un modèle `ca.accounting.mandate`.
- Gestion des mandats simultanés.
- Gestion des transferts de cabinet.
- Droits du portail client.
- Périmètre des cabinets secondaires.

## 12. Conclusion

Étude d'architecture terminée. Aucun code, modèle, vue, sécurité ou base de données n'a été modifié.

ÉTUDE D'ARCHITECTURE TERMINÉE — EN ATTENTE DE VALIDATION DU PROPRIÉTAIRE DU PROJET.


## Annexe A — Contenu intégral de `decisions_prompt_014.md`

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


## Annexe B — Contenu intégral de `diagramme_prompt_014.mmd`

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
    ResUser "1" --> "1" ResPartner : partner_id
    ResUser "0..*" --> "0..*" ResCompanyClient : allowed companies
    CaAccountingFolder "0..*" --> "1" ResCompanyClient : company
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
