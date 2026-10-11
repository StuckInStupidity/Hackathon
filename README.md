# 🧾 Vérification automatisée des factures d'iMSA

## 🎯 Objectif
Automatiser la vérification des factures et de leurs justificatifs pour la détection des erreurs et les tentatives de fraude.

## ⚙️ Fonctionnalités

- **Import par lots** : chargement des factures `.txt` à vérifier et des justificatifs `.json` associées par nom.
- **Gestion des doublons** : détection des fichiers déjà importés.
- **Extraction des données** : parsing des fichiers `.txt`.
- **Structuration des données** : conversion des informations extraites en objets `class` / JSON pour faciliter les comparaisons.
- **Comparaison automatique** : validation des factures ou détection des écarts de zone à vérifier.
- **Vérification humaine** : affichage détaillé des anomalies, comparaison des écarts et possibilité de valider manuellement les résultats.
- **Rapports d'erreurs** : classement décroissant des anomalies les plus fréquentes par catégorie (cliniques / sources d'erreurs).
- **Statistiques globales** :
  - Pourcentage de factures présentant des anomalies.
  - Montant total des écarts financiers.
  - Évolution des statistiques au fil des vérifications, avec retrait des anomalies corrigées et validées.

## 💡 Idées

- **Extraction OCR** : extraction des données du jpeg via l'API gemini et du prompt system
- **Rapports automatisés** : envoyer au manager un rapport hebdomadaire des enregistrements d'anomalies

<img width="2560" height="1500" alt="Screenshot 2026-10-11 145647" src="https://github.com/user-attachments/assets/5dcbbbe5-8bc5-400f-a20c-fa80c6701961" />

<img width="2560" height="1500" alt="Screenshot 2026-10-11 145720" src="https://github.com/user-attachments/assets/233a694e-48fb-461d-bc83-285eed656372" />




