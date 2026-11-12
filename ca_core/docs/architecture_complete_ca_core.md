# Architecture métier de `ca_core`

## 1. Introduction

`ca_core` est le socle technique commun de Comptabilité Algérienne. Il ne contient pas de moteur comptable parallèle à Odoo et ne reproduit pas les fonctionnalités déjà fournies par les modules natifs.

Sa responsabilité est de préparer les éléments communs, transverses et extensibles nécessaires aux modules spécialisés futurs : configuration, paramètres par société, sécurité, référentiels, journalisation, dossiers, établissements et services techniques.

Odoo 20 Community reste la plateforme de référence. Les données comptables, fiscales et financières doivent être gérées par les modules natifs Odoo (`account`, `l10n_dz` et leurs dépendances), dans des modules spécialisés dépendant de `ca_core`.

## 2. Définitions fonctionnelles

### 2.1 Société cliente

Entité juridique pour laquelle une comptabilité est tenue. Elle est représentée principalement par `res.company` et son partenaire associé `res.partner`. Elle porte l'identité légale, la devise, le pays, la TVA, les identifiants légaux et le périmètre de données Odoo.

Une société cliente peut être une entreprise individuelle, une exploitation agricole individuelle ou collective, une EURL, une SARL, une SPA, une SNC ou une autre forme juridique reconnue en Algérie. Les caractéristiques juridiques, fiscales, comptables et organisationnelles doivent être séparées. Les règles réglementaires non vérifiées doivent être signalées comme points à valider.

### 2.2 Cabinet comptable

Structure professionnelle qui gère des dossiers pour plusieurs clients. Il peut être représenté par une société Odoo dédiée, avec ses propres utilisateurs et groupes. Le cabinet est un acteur organisationnel distinct des sociétés clientes.

### 2.3 Dossier comptable

Objet métier indépendant de la société juridique, du cabinet comptable et de l'exercice comptable.

Un dossier comptable est un objet de suivi et de gestion pour le cabinet. Il représente un engagement, une mission ou un périmètre de travail sur une société, pour une période donnée ou pour un besoin spécifique.

Ses responsabilités sont :

- suivre le statut du travail ;
- identifier le cabinet responsable ;
- identifier le responsable du dossier ;
- identifier les collaborateurs autorisés ;
- conserver les dates importantes ;
- conserver l'historique des transferts et des changements ;
- servir de point de rattachement pour les documents comptables futurs, dans les modules spécialisés.

Son cycle de vie est le suivant :

1. Création du dossier.
2. Affectation à une société, un cabinet et un responsable.
3. Travail collaboratif sur les documents autorisés.
4. Clôture du dossier.
5. Archivage du dossier.

Son statut peut être, par exemple : brouillon, actif, en revue, clôturé, archivé. Les statuts exacts seront validés lors de la conception détaillée.

Un dossier n'est pas automatiquement équivalent à un exercice comptable. Un dossier peut couvrir un exercice, plusieurs exercices ou une période spécifique.

### 2.4 Exercice comptable

Période comptable. Ce concept est fourni par les modules comptables natifs d'Odoo. `ca_core` ne doit pas le dupliquer. Un dossier peut être lié à un exercice, mais ne lui est pas équivalent.

### 2.5 Établissement ou site d'exploitation

Lieu physique d'activité. Il peut correspondre à une succursale Odoo (`res.company` enfant) ou à un modèle technique dédié si le besoin métier l'exige. Le choix doit être justifié par les contraintes de reporting et de sécurité.

### 2.6 Personne physique

Individu identifié dans Odoo par `res.partner`. Elle peut être un contact, un client, un fournisseur, un collaborateur ou un utilisateur. Elle ne doit pas être dupliquée par un modèle spécifique sans besoin avéré.

### 2.7 Entreprise individuelle

Forme d'activité exercée par une personne physique. Elle peut être représentée par une société Odoo liée à un partenaire personne physique, avec des attributs juridiques complémentaires dans un module spécialisé si nécessaire.

### 2.8 Exploitation agricole individuelle

Activité agricole exercée par une personne physique. Elle suit le même principe que l'entreprise individuelle, avec des caractéristiques sectorielles à traiter dans un module spécialisé, sans créer de modèle parallèle.

### 2.9 Exploitation agricole collective

Activité agricole exercée par plusieurs personnes ou une structure collective. Elle peut être représentée par une société Odoo et des partenaires associés. Les règles de gouvernance et de répartition devront être validées avant modélisation.

### 2.10 Collaborateur du cabinet

Utilisateur Odoo (`res.users`) disposant de groupes et d'autorisations selon son rôle. Il ne doit pas faire l'objet d'un modèle séparé si les groupes et les règles d'accès suffisent.

### 2.11 Client du cabinet

Entité juridique cliente, généralement représentée par une société Odoo distincte. Le cabinet peut être administrateur technique, mais les données du client restent isolées par société.

## 3. Audit des modèles natifs Odoo 20

### 3.1 `res.company`

Modèle central pour la société Odoo. Il gère le nom, la société parente et les succursales, la devise, le partenaire associé, les coordonnées, la TVA et les identifiants complémentaires, ainsi que le contexte multi-société.

Conclusion : `res.company` doit être réutilisé comme périmètre principal de données. Il ne faut pas créer un modèle parallèle de société.

### 3.2 `res.partner`

Modèle central pour les personnes et les entités. Il gère le nom, l'adresse, les contacts, la société liée, la TVA, les coordonnées bancaires, les images et les métadonnées.

Conclusion : les personnes physiques et les entités juridiques doivent être représentées par `res.partner`, éventuellement complétées par des données spécifiques dans des modules spécialisés.

### 3.3 `res.users`

Modèle des utilisateurs. Il gère le login, les groupes, la société principale, les sociétés autorisées, les contraintes de cohérence entre société principale et sociétés autorisées, et l'héritage depuis `res.partner`.

Conclusion : les collaborateurs et administrateurs doivent être des utilisateurs Odoo standard, différenciés par des groupes et des autorisations.

### 3.4 `res.groups`

Modèle des groupes de sécurité. Il gère l'appartenance des utilisateurs, les groupes implicites, les privilèges et les contraintes d'exclusivité.

Conclusion : la sécurité fonctionnelle doit s'appuyer sur des groupes Odoo, avec une hiérarchie claire.

### 3.5 Droits d'accès et règles

Odoo 20 utilise le modèle `ir.access` pour gérer à la fois :

- les permissions d'accès aux modèles ;
- les restrictions sur les enregistrements basées sur des domaines.

Le fichier `ir.access.csv` utilise les colonnes suivantes :

`id,name,model_id,group_id/id,operation,domain`

Un enregistrement peut être une permission pour un groupe et une opération, avec ou sans domaine. Un enregistrement sans groupe et avec un domaine constitue une restriction globale. Les deux notions sont distinctes même si elles sont gérées par le même modèle.

Conclusion : la séparation des données doit être implémentée avec `ir.access`, plutôt qu'avec une logique applicative parallèle.

### 3.6 Multi-société

Odoo fournit `company_id`, `company_ids`, les champs dépendants de la société, les contraintes de cohérence utilisateur/société et les contextes multi-société.

Conclusion : la multi-société doit être fondée sur `res.company` et les mécanismes natifs, sans recréer un système d'isolation parallèle.

### 3.7 `l10n_dz`

Le module natif algérien gère le plan comptable et les taxes. Il dépend de `account`.

Conclusion : `ca_core` ne doit pas dépendre de `account` ni de `l10n_dz`. Les fonctionnalités comptables et fiscales algériennes doivent être développées dans des modules spécialisés.

## 4. Architecture multi-société et multi-dossiers

### 4.1 Scénarios à couvrir

- Un cabinet gère plusieurs sociétés clientes.
- Une société cliente possède plusieurs dossiers.
- Une société possède plusieurs exercices comptables.
- Plusieurs collaborateurs travaillent sur un même dossier.
- Un collaborateur travaille sur plusieurs dossiers.
- Plusieurs cabinets interviennent sur une même société.
- Un dossier est transféré d'un cabinet à un autre.
- Un dossier est clôturé puis archivé.
- Une société cliente change de cabinet sans perdre son historique.

### 4.2 Relations et contraintes

- `res.company` représente la société juridique et le périmètre natif de données.
- `ca.accounting.folder` représente le dossier de travail du cabinet.
- Un dossier est lié à une société, à un cabinet, à un responsable et éventuellement à un exercice.
- Un dossier n'est pas automatiquement équivalent à un exercice comptable.
- Une société peut avoir plusieurs dossiers.
- Un dossier peut avoir plusieurs collaborateurs autorisés.
- Un collaborateur peut être autorisé sur plusieurs dossiers.
- Plusieurs cabinets peuvent intervenir sur une même société, avec des dossiers distincts.
- Un dossier peut être transféré, clôturé et archivé sans suppression.
- Le changement de cabinet doit conserver l'historique et les traces d'audit.

### 4.3 Cardinalités proposées

- `res.company` 1..n `ca.accounting.folder`
- `ca.accounting.folder` n..1 `res.company`
- `ca.accounting.folder` n..1 cabinet (`res.company` ou modèle spécialisé)
- `ca.accounting.folder` n..1 responsable (`res.users`)
- `ca.accounting.folder` n..0..1 exercice comptable natif
- `ca.accounting.folder` n..m collaborateurs autorisés (`res.users`)
- `ca.establishment` n..1 `res.company`
- `ca.establishment` n..0..1 `ca.accounting.folder`
- `ca.audit.log` n..1 `res.users`
- `ca.audit.log` n..0..1 `res.company`
- `ca.audit.log` n..0..1 objet audité

Les cardinalités exactes seront validées lors de la conception détaillée.

### 4.4 Recommandation

Recommander une société Odoo par entité juridique pour l'isolation native des données, complétée par un dossier comptable transverse pour le suivi métier.

Cette approche évite une relation un-à-un injustifiée entre société et dossier.

## 5. Architecture de sécurité

### 5.1 Isolation entre sociétés

La société (`res.company`) est le premier niveau d'isolation. Les documents natifs doivent porter un `company_id` et être protégés par des règles `ir.access` limitant l'accès aux sociétés autorisées de l'utilisateur.

### 5.2 Isolation entre dossiers

Un champ `company_id` seul n'est pas suffisant. Les factures, écritures et autres documents natifs doivent également être rattachés à un dossier lorsque le besoin métier l'exige. Les règles `ir.access` doivent alors combiner la société et le dossier autorisé.

### 5.3 Limites des mécanismes natifs

Les mécanismes multi-société natifs protègent par société, mais ne protègent pas automatiquement par dossier. Un collaborateur autorisé sur une société pourrait accéder à tous ses documents. Les règles `ir.access` et les champs de rattachement au dossier sont donc nécessaires.

### 5.4 Données comptables à rattacher à un dossier

Les documents suivants devront être rattachés à un dossier dans les modules spécialisés futurs :

- factures et avoirs ;
- écritures comptables ;
- journaux ;
- paiements ;
- pièces justificatives ;
- déclarations.

Le rattachement doit être fait par un champ dédié, avec une valeur obligatoire ou contrôlée selon le cas, et protégé par des règles `ir.access`.

### 5.5 Éviter les accès indirects

Pour éviter les accès indirects non autorisés :

- limiter les champs relationnels exposés ;
- protéger `ir.attachment` par des règles adaptées ;
- contrôler les exports, impressions et rapports ;
- éviter les accès `sudo()` non contrôlés ;
- journaliser les opérations sensibles ;
- tester la sécurité avec des utilisateurs représentatifs.

### 5.6 Groupes proposés

- `ca_core_user` : utilisateur interne de base.
- `ca_core_manager` : gestionnaire de dossiers.
- `ca_core_admin` : administrateur technique du socle.

Les groupes doivent être hiérarchisés par implication.

### 5.7 Accès par modèle

Les droits CRUD par modèle et par groupe sont définis par des enregistrements `ir.access` avec un groupe et une opération.

### 5.8 Accès par enregistrement

Les restrictions par enregistrement sont définies par des enregistrements `ir.access` avec un domaine, avec ou sans groupe.

### 5.9 Portail client

Le portail client doit être prévu comme extension future. Il devra utiliser les groupes portail d'Odoo et des règles `ir.access` strictement limitées aux données du client.

### 5.10 Journalisation

Les opérations sensibles doivent être consignées dans `ca.audit.log`, avec utilisateur, société, action, ancienne et nouvelle valeur, date et contexte.

### 5.11 Limites de la garantie de sécurité

La sécurité n'est pas garantie par la seule définition de l'architecture. Elle devra être validée par l'implémentation des règles `ir.access`, des champs de rattachement, des tests automatisés et des audits de sécurité.

## 6. Établissements et exploitations agricoles

### 6.1 Critères de choix

- Utiliser `res.company` ou une succursale Odoo lorsqu'un site constitue une entité comptable ou fiscale distincte.
- Utiliser `ca.establishment` lorsqu'il s'agit d'un lieu d'exploitation rattaché à une société, sans autonomie comptable complète.
- Utiliser un simple lieu d'exploitation lorsqu'aucune gestion comptable distincte n'est requise.

### 6.2 Exploitations agricoles

Les exploitations agricoles individuelles et collectives doivent être traitées comme des activités ou des caractéristiques d'entités juridiques. Ce projet ne doit pas introduire de fonctionnalités de gestion technique agricole.

## 7. Modèles personnalisés envisagés

Les modèles suivants sont envisagés, mais ne sont pas créés à cette étape :

- `ca.accounting.folder` : dossier comptable.
- `ca.establishment` : établissement ou site.
- `ca.legal.form` : référentiel de formes juridiques, si nécessaire.
- `ca.referential` : référentiels communs.
- `ca.audit.log` : journalisation des opérations sensibles.
- `ca.config` ou extension de `res.config.settings` : paramètres par société.

`res.company`, `res.partner`, `res.users` et `res.groups` restent les modèles natifs de référence.

Pour chaque modèle futur, son utilité, sa nécessité dans la première version, ses relations et les fonctionnalités natives réutilisables devront être précisées avant implémentation.

## 8. Dépendances

`ca_core` conserve uniquement :

```python
'depends': ['base']
```

Ne pas ajouter `account` ou `l10n_dz` à `ca_core`.

## 9. Compatibilité avec les besoins algériens

L'architecture doit pouvoir accueillir les différentes formes juridiques et activités privées en Algérie, notamment les entreprises individuelles, les exploitations agricoles, les sociétés à responsabilité limitée, les sociétés par actions et les sociétés en nom collectif.

Les caractéristiques juridiques, fiscales et comptables doivent être séparées. Toute règle réglementaire non vérifiée doit être signalée comme point à valider avant implémentation.

## 10. Points nécessitant une validation

- Définition exacte du dossier comptable.
- Relation entre dossier et société.
- Gestion des établissements.
- Gestion des cabinets et des collaborateurs.
- Droits d'accès par dossier.
- Extension future du portail client.
- Référentiels juridiques et fiscaux algériens.

## 11. Risques et mesures préventives

- Risque de duplication de fonctionnalités natives : mitigation par réutilisation prioritaire.
- Risque d'isolation insuffisante : mitigation par tests de sécurité automatisés.
- Risque de dépendances circulaires : mitigation par dépendances explicites et contrôlées.
- Risque de sur-conception : mitigation par développement progressif et minimal.
- Risque réglementaire : mitigation par validation avec références officielles.

## 13. Implémentation réelle de `ca.accounting.folder`

Le modèle `ca.accounting.folder` a été implémenté dans `ca_core/models/accounting_folder.py`.

Champs :
- `name` : nom du dossier.
- `code` : référence unique par société.
- `company_id` : société propriétaire, obligatoire.
- `manager_id` : responsable principal, obligatoire.
- `state` : brouillon, actif, en revue, clôturé, archivé.
- `description` : description.
- `collaborator_ids` : collaborateurs autorisés.
- `opening_date` : date d'ouverture.
- `closing_date` : date de clôture.

Contraintes :
- unicité de `code` par `company_id` ;
- société obligatoire ;
- responsable obligatoire ;
- cohérence entre le responsable et la société ;
- cohérence entre les collaborateurs et la société ;
- date de clôture non antérieure à la date d'ouverture ;
- société non modifiable après création ;
- transitions de statut contrôlées ;
- dossier archivé non modifiable par un utilisateur ordinaire.

Sécurité :
- groupes `ca_core_user`, `ca_core_manager`, `ca_core_admin` ;
- `ir.access.csv` avec permissions et restrictions par domaine ;
- isolation par société et par dossier pour les utilisateurs ;
- gestionnaires et administrateurs limités aux sociétés autorisées.

Vues :
- liste, formulaire et recherche ;
- menu « Comptabilité Algérienne » / « Dossiers comptables » ;
- filtres et regroupements.

Tests :
- 20 tests automatisés réussis.
- couverture des contraintes et de l'isolation multi-société et multi-dossier.

Limites :
- pas de gestion des cabinets et mandats ;
- pas de gestion des exercices ;
- pas d'établissements ;
- pas de journalisation dans `ca.audit.log` ;
- pas de portail client.


## 14. Statut des fonctionnalités

### 14.1 Fonctionnalités effectivement implémentées

- Modèle `ca.accounting.folder`.
- Champs et contraintes du dossier comptable.
- Groupes `ca_core_user`, `ca_core_manager`, `ca_core_admin`.
- Règles `ir.access` pour l'isolation par société et par dossier.
- Vues liste, formulaire et recherche.
- Menu « Comptabilité Algérienne » / « Dossiers comptables ».
- Tests automatisés du modèle et de la sécurité.

### 14.2 Décisions d'architecture validées

- Réutilisation de `res.company`, `res.partner`, `res.users` et `res.groups`.
- `ca_core` dépend uniquement de `base`.
- Utilisation d'`ir.access` pour les restrictions par domaine.
- Combinaison de l'isolation par société et par dossier.
- Dossier indépendant de la société, du cabinet et de l'exercice.

### 14.3 Fonctionnalités futures

- Gestion avancée des cabinets et mandats.
- Portail client.
- Extensions comptables dans des modules spécialisés.
- Rattachement des documents comptables natifs à un dossier.

### 14.4 Fonctionnalités reportées

- `ca.audit.log`
- `ca.referential`
- `ca.establishment`
- gestion des exercices comptables
- gestion complète des établissements


===== DOCUMENT 2 : DÉCISIONS D’ARCHITECTURE =====

# Décisions d'architecture — `ca_core`

## 1. Décision : réutiliser `res.company` comme périmètre principal

- Décision : utiliser `res.company` pour représenter la société juridique et le périmètre de données.
- Justification : Odoo fournit nativement la multi-société, la devise, les coordonnées et l'isolation.
- Alternative examinée : créer un modèle `ca.legal.entity` distinct.
- Statut : recommandé.

## 2. Décision : réutiliser `res.partner` pour les personnes et entités

- Décision : utiliser `res.partner` pour les personnes physiques et les entités.
- Justification : évite la duplication des contacts, adresses et identifiants.
- Alternative examinée : créer des modèles `ca.person` et `ca.entity`.
- Statut : recommandé.

## 3. Décision : réutiliser `res.users` et `res.groups`

- Décision : utiliser les utilisateurs et groupes natifs.
- Justification : Odoo gère déjà l'authentification, les groupes implicites et les contraintes.
- Alternative examinée : créer des modèles de collaborateurs et de rôles.
- Statut : recommandé.

## 4. Décision : ne pas dupliquer les exercices comptables

- Décision : laisser la gestion des exercices aux modules comptables natifs.
- Justification : évite une duplication fonctionnelle et des incohérences.
- Alternative examinée : créer `ca.fiscal.year`.
- Statut : recommandé.

## 5. Décision : `ca_core` indépendant de `account` et `l10n_dz`

- Décision : `ca_core` dépend uniquement de `base`.
- Justification : évite les dépendances circulaires et garde le socle léger.
- Alternative examinée : dépendre directement de `account`.
- Statut : recommandé.

## 6. Décision : utilisation d'`ir.access` pour les règles par domaine

- Décision : utiliser `ir.access` pour les restrictions basées sur des domaines.
- Justification : mécanisme natif d'Odoo 20. Le format `ir.access.csv` est `id,name,model_id,group_id/id,operation,domain`.
- Alternative examinée : logique applicative personnalisée.
- Statut : recommandé.

## 7. Décision : séparation des attributs

- Décision : séparer les caractéristiques juridiques, fiscales, comptables et organisationnelles.
- Justification : facilite la maintenance et la conformité.
- Alternative examinée : modèle unique avec tous les champs.
- Statut : recommandé.

## 8. Décision : référentiels de données

- Décision : stocker les formes juridiques et données de référence dans des données, pas dans le code.
- Justification : facilite la maintenance et la localisation.
- Alternative examinée : constantes Python.
- Statut : recommandé.

## 9. Décision : sécurité multi-niveaux

- Décision : combiner l'isolation par société et l'isolation par dossier.
- Justification : un champ `company_id` seul ne protège pas les documents natifs par dossier.
- Alternative examinée : se baser uniquement sur le multi-société natif.
- Statut : recommandé.

## 10. Décision : définition du dossier comptable

- Décision : le dossier est un objet métier indépendant de la société, du cabinet et de l'exercice.
- Justification : permet le suivi, le transfert, la clôture et l'archivage sans confondre les périmètres.
- Alternative examinée : équivalence dossier = société ou dossier = exercice.
- Statut : recommandé.

## 11. Décision : modèles de la première version

| Modèle | Rôle | Nécessité en première version | Dépendances | Justification |
|---|---|---|---|---|
| `ca.accounting.folder` | Dossier comptable | Oui | `base` | Suivi métier non fourni par Odoo natif |
| `ca.audit.log` | Journalisation sensible | Oui | `base` | Traçabilité des opérations sensibles |
| `ca.referential` | Référentiels communs | Oui, version minimale | `base` | Formes juridiques et données de référence |
| `ca.establishment` | Établissement ou site | Conditionnel | `base` | À créer si le besoin de site distinct est confirmé |
| `ca.legal.form` | Forme juridique | Non en première version | `base` | Fusionné dans `ca.referential` |
| `ca.config` | Paramètres | Non comme modèle séparé | `base` | Extension de `res.config.settings` |

## 12. Points à arbitrer

- Relation exacte entre dossier comptable et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Validation des référentiels juridiques et fiscaux algériens.

## 13. Implémentation réelle

- `ca.accounting.folder` est le premier modèle métier implémenté.
- Les contraintes sont implémentées côté serveur.
- La sécurité utilise `ir.access` avec des domaines par société et par dossier.
- Les tests automatisés couvrent les contraintes et l'isolation.
- Les cabinets, mandats, exercices, établissements et journalisation sont reportés.


## 13. Statut des fonctionnalités

### Implémentées

- `ca.accounting.folder`
- sécurité de base par société et par dossier
- vues et menus
- tests automatisés

### Futures

- cabinets et mandats
- portail client
- extensions comptables

### Reportées

- `ca.audit.log`
- `ca.referential`
- `ca.establishment`
- gestion des exercices
