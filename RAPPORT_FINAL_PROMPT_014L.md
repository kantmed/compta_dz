# Rapport final — Prompt 014-L : Levée des dernières réserves documentaires

## 1. Décisions validées

- `ca_core` dépend uniquement de `base`.
- `res.company` représente la société juridique.
- `res.partner`, `res.users` et `res.groups` sont réutilisés.
- `ir.access` gère les restrictions par domaine.
- Le dossier est fonctionnellement indépendant, mais rattaché à une seule société cliente par `company_id`.
- L'isolation combine la société et le dossier.
- Les exercices comptables ne sont pas développés dans `ca_core`.
- `ca.audit.log` et `ca.referential` sont reportés.
- `ca.establishment` est conditionnel.
- La représentation du cabinet par `res.company` reste une recommandation à confirmer.

## 2. Recommandations et hypothèses restantes

- Gestion des établissements.
- Représentation et périmètre du cabinet comptable.
- Modalités détaillées des droits d'accès par dossier.
- Extension future du portail client.
- Référentiels juridiques et fiscaux algériens.
- Modalités techniques exactes des exercices comptables.

## 3. Périmètre développé et non développé

Implémenté :
- `ca.accounting.folder`
- ses contraintes
- ses groupes et règles d'accès
- ses vues et menus
- ses tests

Non développé ou reporté :
- `ca.audit.log`
- `ca.referential`
- `ca.establishment`
- gestion des exercices
- cabinets et mandats
- portail client
- extensions comptables
- rattachement des documents comptables natifs

## 4. Résultat vérifiable des tests

Les journaux d'exécution disponibles indiquent pour la dernière exécution pertinente :

- 48 tests exécutés.
- 0 échec.
- 0 erreur.

Ces résultats concernent exclusivement le périmètre développé de `ca_core`, notamment `ca.accounting.folder`, ses contraintes et sa sécurité. Ils ne valident pas les futurs modules comptables, mandats ou portails.

## 5. Contrôles documentaires

- La relation société-dossier est validée et n'est plus présentée comme une hypothèse.
- La distinction entre société cliente et cabinet est conservée.
- Le mandat est identifié comme un modèle futur non développé.
- La sécurité actuelle est distinguée de la sécurité cible.
- Le périmètre agricole reste limité à la comptabilité.
- Aucune cardinalité définitive n'est imposée pour les exercices comptables.
- Aucune décision non validée n'est présentée comme définitive.

## 6. Réserves éventuelles

- Les référentiels juridiques et fiscaux algériens doivent être validés avec des sources officielles.
- Les règles détaillées d'accès par dossier devront être implémentées et testées.
- Les modalités techniques exactes des exercices comptables restent à confirmer.

## 7. Conclusion

VALIDÉ
