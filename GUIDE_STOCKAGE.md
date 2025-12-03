# 💾 Guide de Configuration du Stockage

## Options de Sauvegarde Disponibles

Quand un client valide une commande, les données sont **toujours sauvegardées** (même si l'email échoue).

### 📋 Option 1 : CSV Local (Recommandé - Défaut)

**Avantages :**
- ✅ Simple et rapide
- ✅ Ouvrable dans Excel/Google Sheets
- ✅ Pas de configuration nécessaire

**Où :** Fichiers sauvegardés dans le dossier `commandes/`
- Format : `commandes_YYYYMM.csv` (un fichier par mois)

**Configuration :**
1. Allez dans "💾 Stockage" dans la sidebar
2. Sélectionnez "csv" comme méthode
3. Sauvegardez

---

### 📄 Option 2 : JSON Local

**Avantages :**
- ✅ Format structuré avec toutes les informations
- ✅ Facile à traiter programmatiquement
- ✅ Un fichier par commande

**Où :** Fichiers sauvegardés dans le dossier `commandes/`
- Format : `commande_YYYYMMDD_HHMMSS.json`

**Configuration :**
1. Allez dans "💾 Stockage" dans la sidebar
2. Sélectionnez "json" comme méthode
3. Sauvegardez

---

### 📊 Option 3 : Google Sheets

**Avantages :**
- ✅ Accès depuis n'importe où
- ✅ Partage facile avec votre équipe
- ✅ Visualisation directe des commandes

**Configuration :**

1. **Créer un Google Sheet**
   - Créez un nouveau sheet sur Google Sheets
   - Notez l'ID dans l'URL : `https://docs.google.com/spreadsheets/d/[ID_ICI]/edit`

2. **Créer un compte de service Google**
   - Allez sur https://console.cloud.google.com
   - Créez un nouveau projet (ou utilisez un existant)
   - Activez l'API "Google Sheets API" et "Google Drive API"
   - Créez un "Compte de service" dans IAM & Admin > Service Accounts
   - Téléchargez le fichier JSON de credentials

3. **Partager le Sheet**
   - Dans votre Google Sheet, cliquez sur "Partager"
   - Ajoutez l'email du compte de service (trouvé dans le fichier JSON)
   - Donnez-lui les droits "Éditeur"

4. **Configurer dans l'app**
   - Allez dans "💾 Stockage" dans la sidebar
   - Sélectionnez "google_sheets"
   - Ajoutez l'ID du sheet et le chemin vers le fichier JSON
   - Sauvegardez

**Installation des dépendances :**
```bash
py -m pip install gspread oauth2client google-api-python-client
```

---

### 🔄 Option 4 : CSV + JSON (Tout sauvegarder)

Sauvegarde à la fois en CSV ET en JSON pour avoir les deux formats.

**Configuration :**
1. Allez dans "💾 Stockage" dans la sidebar
2. Sélectionnez "csv+json"
3. Sauvegardez

---

## Structure des Données

### Format CSV

| Date | Heure | Client | Email | Produit | Quantité | Description | Lien |
|------|-------|--------|-------|---------|----------|-------------|------|
| 2024-01-15 | 14:30:00 | Jean Dupont | jean@example.com | Produit A | 10 | Description... | https://... |

### Format JSON

```json
{
  "date": "2024-01-15T14:30:00",
  "client": {
    "name": "Jean Dupont",
    "email": "jean@example.com"
  },
  "produits": [
    {
      "name": "Produit A",
      "quantity": 10,
      "description": "Description...",
      "link": "https://...",
      "has_image": true
    }
  ]
}
```

---

## Localisation des Fichiers

Tous les fichiers locaux sont sauvegardés dans :
```
C:\Users\LENOVO\Documents\ECOM\commandes\
```

Vous pouvez :
- ✅ Ouvrir les CSV dans Excel
- ✅ Importer les JSON pour traitement
- ✅ Transférer sur Google Drive manuellement si besoin

---

## Recommandation

Pour un MVP, utilisez **CSV** :
- Simple et fonctionne immédiatement
- Pas de configuration complexe
- Compatible avec tous les outils

Pour une solution plus professionnelle, utilisez **Google Sheets** :
- Accès cloud
- Partage avec équipe
- Mise à jour automatique

