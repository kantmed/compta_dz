# Architecture métier de `ca_core`

## 1. Introduction

`ca_core` est le socle technique commun de Comptabilité Algérienne. Il ne contient pas de moteur comptable parallèle à Odoo et ne reproduit pas les fonctionnalités déjà fournies par les modules natifs.

Sa responsabilité est de préparer les éléments communs, transverses et extensibles nécessaires aux modules spécialisés futurs : configuration, paramètres par société, sécurité, référentiels, journalisation et services techniques.

Odoo 20 Community reste la plateforme de référence. Les données comptables, fiscales et financières doivent être gérées par les modules natifs Odoo (`account`, `l10n_dz` et leurs dépendances), dans des modules spécialisés dépendant de `ca_core`.

## 2. Définitions fonctionnelles

### 2.1 Société juridique

Entité légale pour laquelle une comptabilité est tenue. Elle correspond principalement à `res.company` et à son partenaire associé (`res.partner`). Elle porte l'identité légale, la devise, le pays, la TVA et le périmètre de données Odoo.

### 2.2 Personne physique

Individu identifié dans Odoo par `res.partner`. Elle peut être un contact, un client, un fournisseur, un collaborateur ou un utilisateur. Elle ne doit pas être dupliquée par un modèle spécifique sans besoin avéré.

### 2.3 Entreprise individuelle

Forme d'activité exercée par une personne physique. Elle peut être représentée par une société Odoo (`res.company`) liée à un partenaire personne physique, avec des attributs juridiques complémentaires dans un module spécialisé si nécessaire.

### 2.4 Exploitation agricole individuelle

Activité agricole exercée par une personne physique. Elle suit le même principe que l'entreprise individuelle, avec des caractéristiques sectorielles à traiter dans un module spécialisé, sans créer de modèle parallèle.

### 2.5 Exploitation agricole collective

Activité agricole exercée par plusieurs personnes ou une structure collective. Elle peut être représentée par une société Odoo et des partenaires associés. Les règles de gouvernance et de répartition devront être validées avant modélisation.

### 2.6 EURL

Forme juridique à associer unique. Elle peut être représentée par `res.company` et son partenaire. Les attributs juridiques propres (capital, gérant, statut) peuvent être stockés comme données complémentaires dans un module spécialisé.

### 2.7 SARL

Forme juridique à plusieurs associés. Même principe que l'EURL : réutilisation de `res.company`, données complémentaires dans un module spécialisé.

### 2.8 SPA

Forme juridique à capital divisé en actions. Réutilisation de `res.company`; les données propres à la gouvernance seront traitées dans un module spécialisé.

### 2.9 SNC

Forme juridique avec plusieurs associés responsables. Réutilisation de `res.company`; les règles de responsabilité et de gouvernance devront être précisées par module spécialisé.

### 2.10 Autres formes juridiques

Les autres formes juridiques reconnues en Algérie doivent être gérées par un référentiel de données, pas par des modèles séparés pour chaque forme. Les règles réglementaires devront être vérifiées avant implémentation.

### 2.11 Établissement ou site d'exploitation

Lieu physique d'activité. Il peut correspondre à une succursale Odoo (`res.company` enfant) ou à un modèle technique dédié si le besoin métier l'exige. Le choix doit être justifié par les contraintes de reporting et de sécurité.

### 2.12 Cabinet comptable

Structure professionnelle qui gère des dossiers pour plusieurs clients. Elle peut être représentée par une société Odoo dédiée au cabinet, avec des utilisateurs et des groupes spécifiques.

### 2.13 Collaborateur du cabinet

Utilisateur Odoo (`res.users`) disposant de groupes et d'autorisations selon son rôle. Il ne doit pas faire l'objet d'un modèle séparé si les groupes et les règles d'accès suffisent.

### 2.14 Client du cabinet

Entité juridique cliente, généralement représentée par une société Odoo distincte. Le cabinet peut être administrateur technique, mais les données du client restent isolées par société.

### 2.15 Exercice comptable

Période comptable. Ce concept est fourni par les modules comptables natifs d'Odoo. `ca_core` ne doit pas le dupliquer. Un module spécialisé pourra l'étendre si nécessaire.

### 2.16 Dossier comptable

Objet de gestion propre au cabinet : suivi, statut, responsabilité, dates, archivage et organisation. Il n'est pas équivalent à une société Odoo ni à un exercice. Il peut être lié à une société et à un exercice.

## 3. Audit des modèles natifs Odoo 20

### 3.1 `res.company`

Modèle central pour la société Odoo. Il gère :

- le nom ;
- la société parente et les succursales ;
- la devise ;
- le partenaire associé ;
- les coordonnées ;
- la TVA et les identifiants complémentaires ;
- le contexte multi-société.

Conclusion : `res.company` doit être réutilisé comme périmètre principal de données. Il ne faut pas créer un modèle parallèle de société.

### 3.2 `res.partner`

Modèle central pour les personnes et les entités. Il gère :

- le nom ;
- l'adresse ;
- les contacts ;
- la société liée ;
- la TVA ;
- les coordonnées bancaires ;
- les images et les métadonnées.

Conclusion : les personnes physiques et les entités juridiques doivent être représentées par `res.partner`, éventuellement complétées par des données spécifiques dans des modules spécialisés.

### 3.3 `res.users`

Modèle des utilisateurs. Il gère :

- le login ;
- les groupes ;
- la société principale ;
- les sociétés autorisées ;
- les contraintes de cohérence entre société principale et sociétés autorisées ;
- l'héritage depuis `res.partner`.

Conclusion : les collaborateurs et administrateurs doivent être des utilisateurs Odoo standard, différenciés par des groupes et des autorisations.

### 3.4 `res.groups`

Modèle des groupes de sécurité. Il gère :

- l'appartenance des utilisateurs ;
- les groupes implicites ;
- les privilèges ;
- les contraintes d'exclusivité.

Conclusion : la sécurité fonctionnelle doit s'appuyer sur des groupes Odoo, avec une hiérarchie claire.

### 3.5 Droits d'accès et règles

Odoo 20 utilise :

- `ir.model.access` pour les droits CRUD par modèle et par groupe ;
- `ir.access` pour les règles basées sur des domaines, avec permissions et restrictions.

Conclusion : la séparation des données doit être implémentée avec les mécanismes natifs, notamment les domaines d'accès, plutôt qu'avec une logique applicative parallèle.

### 3.6 Multi-société

Odoo fournit :

- `company_id` ;
- `company_ids` ;
- les champs dépendants de la société ;
- les contraintes de cohérence utilisateur/société ;
- les contextes multi-société.

Conclusion : la multi-société doit être fondée sur `res.company` et les mécanismes natifs, sans recréer un système d'isolation parallèle.

### 3.7 `l10n_dz`

Le module natif algérien gère le plan comptable et les taxes. Il dépend de `account`.

Conclusion : `ca_core` ne doit pas dépendre de `account` ni de `l10n_dz`. Les fonctionnalités comptables et fiscales algériennes doivent être développées dans des modules spécialisés.

## 4. Architecture multi-société et multi-dossiers

### 4.1 Option A — Une société Odoo par entité juridique

Chaque entité juridique cliente est une `res.company`. Le cabinet est également une société Odoo. Les collaborateurs reçoivent l'accès aux sociétés concernées via `company_ids`.

Avantages :

- réutilisation native de l'isolation multi-société ;
- sécurité et filtrage natifs ;
- compatibilité avec les modules comptables ;
- gestion native de la devise et de la TVA.

Inconvénients :

- nécessite une gouvernance claire des sociétés ;
- les utilisateurs peuvent accéder à plusieurs sociétés selon leurs autorisations.

### 4.2 Option B — Un modèle `ca.accounting.folder` transverse

Un dossier comptable est un objet de suivi lié à une société, un cabinet et un exercice.

Avantages :

- suivi métier du dossier ;
- statut, responsabilité, dates et archivage ;
- séparation entre société technique et dossier de travail.

Inconvénients :

- risque de duplication conceptuelle si le dossier est confondu avec la société ;
- nécessite des règles d'accès supplémentaires.

### 4.3 Recommandation

Recommander l'option A pour l'isolation des données, complétée par l'option B pour le suivi métier.

Autrement dit :

- `res.company` représente la société juridique et le périmètre de données ;
- `ca.accounting.folder` représente le dossier de travail du cabinet ;
- un dossier est lié à une société, à un cabinet, à un responsable et à un exercice ;
- les établissements sont liés à la société et éventuellement au dossier.

Cette approche évite une relation un-à-un injustifiée entre société et dossier, car un cabinet peut gérer plusieurs dossiers pour une même société ou pour des exercices différents.

## 5. Architecture de sécurité

### 5.1 Groupes proposés

- `ca_core_user` : utilisateur interne de base.
- `ca_core_manager` : gestionnaire de dossiers.
- `ca_core_admin` : administrateur technique du socle.

Les groupes doivent être hiérarchisés par implication.

### 5.2 Accès par modèle

Utiliser `ir.model.access` pour définir les droits CRUD par modèle et par groupe.

### 5.3 Accès par enregistrement

Utiliser `ir.access` pour restreindre les enregistrements selon :

- la société ;
- le dossier ;
- le cabinet ;
- le statut ;
- le rôle de l'utilisateur.

### 5.4 Multi-société

Les règles doivent empêcher l'accès aux données d'une société non autorisée. Le filtrage doit être vérifiable par des tests automatisés.

### 5.5 Accès collaborateurs

Un collaborateur peut intervenir sur plusieurs dossiers. Ses droits doivent être déterminés par ses groupes et par les règles d'accès, pas par des exceptions manuelles.

### 5.6 Accès clients

Le portail client doit être prévu comme extension future. Il devra utiliser les groupes portail d'Odoo et des règles d'accès strictement limitées aux données du client.

### 5.7 Journalisation

Les opérations sensibles doivent être consignées dans `ca.audit.log`, avec utilisateur, société, action, ancienne et nouvelle valeur, date et contexte.

## 6. Modèles personnalisés envisagés

Les modèles suivants sont envisagés, mais ne sont pas créés à cette étape :

- `ca.accounting.folder` : dossier comptable.
- `ca.establishment` : établissement ou site.
- `ca.legal.form` : référentiel de formes juridiques, si nécessaire.
- `ca.referential` : référentiels communs.
- `ca.audit.log` : journalisation des opérations sensibles.
- `ca.config` ou extension de `res.config.settings` : paramètres par société.

`res.company`, `res.partner`, `res.users` et `res.groups` restent les modèles natifs de référence.

## 7. Relations entre les modèles

Relations proposées :

- `res.company` 1..n `ca.accounting.folder`
- `ca.accounting.folder` n..1 `res.company`
- `ca.accounting.folder` n..1 responsable (`res.users`)
- `ca.accounting.folder` n..1 cabinet (`res.company` ou modèle spécialisé)
- `ca.establishment` n..1 `res.company`
- `ca.establishment` n..0..1 `ca.accounting.folder`
- `ca.audit.log` n..1 `res.users`
- `ca.audit.log` n..0..1 `res.company`
- `ca.audit.log` n..0..1 objet audité

Les relations exactes seront validées lors de la conception détaillée.

## 8. Découpage des modules

### 8.1 `ca_core`

Responsabilités :

- configuration générale ;
- paramètres par société ;
- sécurité commune ;
- référentiels communs ;
- services techniques ;
- journalisation ;
- dossiers et établissements, si validés.

Dépendances :

- `base`.

### 8.2 Modules spécialisés futurs

Responsabilités :

- comptabilité ;
- fiscalité ;
- déclarations ;
- portail client ;
- intégrations.

Dépendances attendues :

- `ca_core`
- `account`
- `l10n_dz`

## 9. Décisions techniques recommandées

1. Ne pas créer de modèle parallèle de société : réutiliser `res.company`.
2. Ne pas créer de modèle parallèle de personne : réutiliser `res.partner`.
3. Ne pas créer de modèle parallèle d'utilisateur : réutiliser `res.users`.
4. Ne pas dupliquer les exercices comptables natifs.
5. Conserver `ca_core` indépendant de `account` et `l10n_dz`.
6. Utiliser `ir.access` pour les règles par domaine, conformément à Odoo 20.
7. Séparer les attributs juridiques, fiscaux, comptables et organisationnels.
8. Stocker les formes juridiques et référentiels dans des données, pas dans du code dur.

## 10. Compatibilité avec les besoins algériens

L'architecture doit pouvoir accueillir les différentes formes juridiques et activités privées en Algérie, notamment les entreprises individuelles, les exploitations agricoles, les sociétés à responsabilité limitée, les sociétés par actions et les sociétés en nom collectif.

Les caractéristiques juridiques, fiscales et comptables doivent être séparées. Toute règle réglementaire non vérifiée doit être signalée comme point à valider avant implémentation.

## 11. Points nécessitant une validation

- Définition exacte du dossier comptable.
- Relation entre dossier et société.
- Gestion des établissements.
- Gestion des cabinets et des collaborateurs.
- Droits d'accès par dossier.
- Extension future du portail client.
- Référentiels juridiques et fiscaux algériens.

## 12. Risques et mesures préventives

- Risque de duplication de fonctionnalités natives : mitigation par réutilisation prioritaire.
- Risque d'isolation insuffisante : mitigation par tests de sécurité automatisés.
- Risque de dépendances circulaires : mitigation par dépendances explicites et contrôlées.
- Risque de sur-conception : mitigation par développement progressif et minimal.
- Risque réglementaire : mitigation par validation avec références officielles.
