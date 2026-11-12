# Rapport final — Prompt 014-K : Harmonisation finale de l'architecture

## 1. Objet et périmètre

Cette étape finalise la cohérence documentaire de l'architecture `ca_core` sans modifier le code, les modules natifs, la base de données ni la configuration.

## 2. Documents examinés

- `ca_core/docs/architecture_metier_ca_core.md`
- `ca_core/docs/decisions_architecture_ca_core.md`
- `ca_core/docs/diagramme_architecture_ca_core.mmd`

## 3. Contradictions corrigées

- Le rattachement société-dossier est présenté comme une décision validée : une société cliente peut posséder plusieurs dossiers et chaque dossier appartient à une seule société cliente.
- La distinction entre société cliente et cabinet comptable est clarifiée.
- Le mandat est identifié comme un modèle futur non développé.
- La sécurité actuellement implémentée est distinguée de la sécurité cible.
- Les résultats de tests sont limités au périmètre développé de `ca_core`.
- `ca.config` n'est plus présenté comme une extension existante.
- Le périmètre agricole reste limité à la comptabilité.

## 4. Extraits corrigés utiles

### Architecture métier

Le dossier est fonctionnellement indépendant, mais obligatoirement rattaché à une seule société cliente par `company_id`.

La sécurité actuellement implémentée concerne uniquement `ca.accounting.folder`, ses contraintes, ses groupes, ses règles d'accès, le responsable, les collaborateurs et les tests disponibles.

La sécurité cible concerne les futurs documents comptables : factures, écritures, paiements, pièces jointes, rapports, exports et portail client.

Les tests concernent le périmètre actuellement développé de `ca_core` et ne valident pas les futurs modules comptables.

### Décisions d'architecture

- `ca_core` dépend uniquement de `base`.
- `res.company` représente la société juridique.
- `res.partner`, `res.users` et `res.groups` sont réutilisés.
- `ir.access` gère les restrictions par domaine.
- Le dossier est fonctionnellement indépendant, mais rattaché à une seule société cliente.
- `ca.config` n'est pas un modèle développé ; la configuration générale utilise `res.config.settings`.
- `ca.audit.log` et `ca.referential` sont reportés.
- `ca.establishment` est conditionnel.

### Diagramme Mermaid

- `ResCompanyClient "1" --> "0..*" CaAccountingFolder : owns`
- `ResUser --> ResPartner : partner_id`
- `CaAccountingFolder "1" --> "0..*" CaAccountingMandate : mandates`
- `CaAccountingMandate` est annoté comme modèle futur non développé.
- `IrAccess` n'est pas présenté comme une relation métier directe.

## 5. Liste des fichiers créés ou modifiés

Modifiés :
- `ca_core/docs/architecture_metier_ca_core.md`
- `ca_core/docs/decisions_architecture_ca_core.md`
- `ca_core/docs/diagramme_architecture_ca_core.mmd`

Créés :
- `RAPPORT_FINAL_PROMPT_014K.md`

## 6. Contrôles effectués

- Cohérence des trois documents : vérifiée.
- Cardinalités du diagramme : vérifiées.
- Absence de l'ancienne hypothèse société-dossier : vérifiée.
- Distinction sécurité actuelle / sécurité cible : vérifiée.
- Tests : 48 exécutés, 0 échec, 0 erreur.
- `ca_core` indépendant de `account` et `l10n_dz` : confirmé.
- Aucun fichier Python, XML, CSV ou manifeste modifié.
- Aucun commit Git effectué.

## 7. Points restant à confirmer

- Relation exacte entre dossier et société.
- Gestion des établissements.
- Périmètre du cabinet comptable.
- Droits d'accès par dossier.
- Extension future du portail client.
- Référentiels juridiques et fiscaux algériens.

## 8. Conclusion

VALIDÉ
