# 📧 Configuration Email - Instructions

## Pour recevoir les emails de commandes

Quand un client valide une précommande, vous recevrez automatiquement un email détaillé à **madouange48@gmail.com**.

**⚠️ IMPORTANT :** La section de configuration email n'est PAS visible aux clients (pour des raisons de sécurité). Seul le transitaire peut configurer.

### Configuration SMTP (Nécessaire pour l'envoi)

Pour que l'application puisse envoyer des emails, vous devez configurer les identifiants SMTP :

### Méthode 1 : Variables d'environnement (Recommandé)

Créez un fichier `.env` à la racine du projet avec :

```env
# Email où recevoir les notifications (déjà configuré)
TRANSITAIRE_EMAIL=madouange48@gmail.com

# Identifiants SMTP Gmail
SMTP_USER=madouange48@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-application-gmail
```

**Pour Gmail :**
1. Allez dans votre compte Google > Sécurité
2. Activez la validation en 2 étapes
3. Créez un "Mot de passe d'application"
4. Utilisez ce mot de passe dans `SMTP_PASSWORD`

**Serveurs SMTP courants :**
- Gmail: `smtp.gmail.com:587` (défaut)
- Outlook: `smtp-mail.outlook.com:587`
- Yahoo: `smtp.mail.yahoo.com:587`

### Installation de python-dotenv (optionnel)

Pour charger automatiquement le fichier `.env`, installez :
```bash
py -m pip install python-dotenv
```

Puis ajoutez au début de `app.py` :
```python
from dotenv import load_dotenv
load_dotenv()
```

### Test de l'envoi

1. Ajoutez un produit au panier
2. Cliquez sur "Valider la précommande"
3. Vérifiez votre boîte email (et les spams au début)

L'email contient :
- ✅ Informations du client (nom, email)
- ✅ Liste détaillée des produits commandés
- ✅ Quantités et descriptions
- ✅ Liens vers les produits (si fournis)
- ✅ Date et heure de la commande

