"""
CEREZA - Plateforme de Précommande
Version: Senior Production V7 (Persistance & Stabilité Dashboard)
Fix: Intégration de la lecture sécurisée des fichiers CSV pour éviter les pages Admin vierges sur Cloud.
"""
import streamlit as st
import pandas as pd
import csv
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import urllib.parse
from pandas.errors import EmptyDataError # Nécessaire pour gérer les fichiers vides

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Cereza | Espace Privé", 
    page_icon="🍒", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Chemins
DATA_DIR = Path("data_store")
DATA_DIR.mkdir(exist_ok=True)
FILE_CLIENTS = DATA_DIR / "base_clients.csv"
FILE_COMMANDES = DATA_DIR / "historique_commandes.csv"

# CLÉS DE SÉCURITÉ
ADMIN_PASSWORD = "cereza_admin" 
ADMIN_KEY_NAME = "ADMIN"
ADMIN_KEY_CONTACT = "2002"

@dataclass
class Product:
    name: str
    quantity: int
    description: str = ""
    link: str = ""

# --- 2. GESTION DE SESSION (PERSISTANCE) ---

def init_session():
    """Initialise la session, gère la persistance et l'étape de connexion."""
    st.session_state.setdefault("cart", [])
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("is_admin", False)
    st.session_state.setdefault("login_stage", 'input')

    # AUTO-LOGIN via URL (Persistence)
    if not st.session_state.user:
        try:
            query_params = st.query_params
            if "uid" in query_params:
                decoded_uid = urllib.parse.unquote(query_params["uid"])
                parts = decoded_uid.split("|")
                if len(parts) == 3:
                    name, contact, is_admin_str = parts
                    st.session_state.user = {"name": name, "contact": contact}
                    st.session_state.is_admin = (is_admin_str == 'True')
                    st.session_state.login_stage = 'complete'
        except Exception:
            pass

def persist_login(name, contact, is_admin=False):
    """Sauvegarde l'utilisateur et son statut d'admin dans l'URL"""
    combined = f"{name}|{contact}|{is_admin}"
    encoded = urllib.parse.quote(combined)
    st.query_params["uid"] = encoded

def clear_login():
    """Nettoie la session et l'URL"""
    st.session_state.user = None
    st.session_state.is_admin = False
    st.session_state.cart = []
    st.session_state.login_stage = 'input'
    st.query_params.clear()

# --- 3. CSS (Identique) ---

def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
        :root {
            --cold-primary: #0f172a; --cold-secondary: #334155;
            --warm-accent: #f97316; --warm-light: #fff7ed; --white: #ffffff;
        }
        .stApp { background-color: var(--warm-light); font-family: 'Plus Jakarta Sans', sans-serif; }
        [data-testid="stSidebar"] { background-color: var(--white); border-right: 1px solid #e2e8f0; }
        
        .profile-card {
            background: linear-gradient(135deg, var(--cold-primary) 0%, var(--cold-secondary) 100%);
            border-radius: 16px; padding: 20px; text-align: center; color: white;
            margin-bottom: 20px; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        }
        .profile-avatar {
            width: 60px; height: 60px; background-color: var(--warm-accent); color: white;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 24px; font-weight: 700; margin: 0 auto 12px auto;
            border: 3px solid rgba(255,255,255,0.2);
        }
        .hero-cereza {
            background: var(--cold-primary); color: white; padding: 2.5rem;
            border-radius: 20px; margin-bottom: 2rem;
        }
        .order-card {
            background: var(--white); border-left: 4px solid var(--warm-accent);
            border-radius: 12px; padding: 1.2rem; margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        div.stButton > button[kind="primary"] {
            background-color: var(--warm-accent); border: none; color: white; font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FONCTIONS DATA ---

def add_to_cart_callback():
    name = st.session_state.get("input_name", ""); qty = st.session_state.get("input_qty", 1)
    link = st.session_state.get("input_link", ""); desc = st.session_state.get("input_desc", "")
    if name:
        st.session_state.cart.append(Product(name, qty, desc, link)); st.toast(f"✅ {name} ajouté !")
    else: st.warning("Le nom du produit est obligatoire.")
def clear_cart_callback(): st.session_state.cart = []
def get_initials(fullname):
    if not fullname: return "C"
    parts = fullname.strip().split()
    if len(parts) >= 2: return f"{parts[0][0]}{parts[1][0]}".upper()
    return fullname[:2].upper()
def log_client_access(name, contact):
    try:
        exists = FILE_CLIENTS.exists()
        with open(FILE_CLIENTS, 'a', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            if not exists: w.writerow(["Date", "Nom", "Contact"])
            w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name.upper(), contact])
    except: pass
def save_order_excel(user, cart):
    try:
        exists = FILE_COMMANDES.exists(); oid = datetime.now().strftime('%Y%m%d-%H%M%S')
        with open(FILE_COMMANDES, 'a', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            if not exists: w.writerow(["ID", "Date", "Client", "Contact", "Produit", "Qte", "Desc", "Lien"])
            for i in cart: w.writerow([oid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user['name'], user['contact'], i.name, i.quantity, i.description, i.link])
        return True, ""
    except PermissionError: return False, "⚠️ Fichier verrouillé par Excel."
    except Exception as e: return False, str(e)
def send_email_notification(user, cart):
    try:
        user_smtp = st.secrets.get("SMTP_USER") or os.getenv("SMTP_USER")
        pwd_smtp = st.secrets.get("SMTP_PASSWORD") or os.getenv("SMTP_PASSWORD")
        if not user_smtp: return False
        msg = MIMEMultipart()
        msg['Subject'] = f"🍒 Commande Cereza: {user['name']}"; msg['From'] = user_smtp
        msg['To'] = "madouange48@gmail.com"
        html = "<ul>" + "".join([f"<li>{p.name} (x{p.quantity})</li>" for p in cart]) + "</ul>"
        msg.attach(MIMEText(html, 'html')); s = smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); s.login(user_smtp, pwd_smtp)
        s.sendmail(user_smtp, "madouange48@gmail.com", msg.as_string()); s.quit(); return True
    except: return False


# --- 5. INTERFACE ADMIN (VERSION SÉCURISÉE) ---

def load_data_safe(file_path: Path) -> pd.DataFrame:
    """Tente de charger les données CSV. Retourne un DataFrame vide avec colonnes si échec."""
    # Définition des colonnes par défaut pour éviter un plantage si le fichier n'existe pas
    if file_path == FILE_COMMANDES:
        cols = ["ID", "Date", "Client", "Contact", "Produit", "Qte", "Desc", "Lien"]
    elif file_path == FILE_CLIENTS:
        cols = ["Date", "Nom", "Contact"]
    else:
        cols = []

    if not file_path.exists():
        # Si le fichier n'existe pas (cas typique après redémarrage Cloud)
        return pd.DataFrame(columns=cols)

    try:
        # Tente la lecture
        df = pd.read_csv(file_path, sep=';', encoding='utf-8-sig')
        # Vérifie si le fichier est vide ou seulement des headers
        if df.empty:
             return pd.DataFrame(columns=cols)
        return df
    except EmptyDataError:
        # Fichier vide, retourne un DF avec les headers
        return pd.DataFrame(columns=cols)
    except Exception as e:
        # Autre erreur (corruption, etc.)
        st.error(f"Erreur de lecture de {file_path.name}: {e}")
        return pd.DataFrame(columns=cols)


def admin_dashboard():
    """Affiche le Dashboard Admin robuste."""
    st.markdown("## 🦅 Dashboard Superviseur")
    st.info("Mode Administrateur. Accès total aux données de commandes.")
    
    tab1, tab2 = st.tabs(["Commandes", "Clients"])
    
    with tab1:
        st.markdown("### Historique des Commandes")
        df_commandes = load_data_safe(FILE_COMMANDES)
        
        if df_commandes.empty:
            st.warning("Historique de commandes vide. Passez une commande test pour créer le fichier.")
        else:
            st.dataframe(df_commandes, use_container_width=True)
            # Le fichier DOIT exister ici car on l'a sauvegardé
            with open(FILE_COMMANDES, "rb") as f:
                st.download_button("📥 Télécharger CSV", f, "cereza_commandes.csv", "text/csv")
            
    with tab2:
        st.markdown("### Liste des Clients Enregistrés")
        df_clients = load_data_safe(FILE_CLIENTS)

        if df_clients.empty:
            st.warning("Base clients vide. Connectez-vous en tant que client normal pour enregistrer les données.")
        else:
            st.dataframe(df_clients, use_container_width=True)

# --- 6. INTERFACE CLIENT ---

def login_screen():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        st.markdown("<h1 style='text-align:center; color:#0f172a;'>CEREZA</h1>", unsafe_allow_html=True)

        # --- Étape 2: Mot de passe Admin ---
        if st.session_state.login_stage == 'password':
            st.warning("Accès Administrateur détecté. Veuillez entrer le mot de passe.")
            with st.form("admin_pwd_form"):
                admin_pwd = st.text_input("Mot de passe ADMIN", type="password")
                submitted = st.form_submit_button("Valider l'accès", type="primary", use_container_width=True)
                
                if submitted:
                    if admin_pwd == ADMIN_PASSWORD:
                        name = st.session_state.temp_admin_name
                        contact = st.session_state.temp_admin_contact
                        st.session_state.is_admin = True
                        st.session_state.user = {"name": name, "contact": contact}
                        persist_login(name, contact, is_admin=True)
                        st.session_state.login_stage = 'complete'
                        st.rerun()
                    else:
                        st.error("Mot de passe incorrect. Recommencez la connexion.")
                        st.session_state.login_stage = 'input'
                        st.rerun()
        
        # --- Étape 1: Nom et Contact ---
        else:
            with st.form("auth_form"):
                name = st.text_input("Nom complet")
                contact = st.text_input("Contact (Tél / Email)")
                submitted = st.form_submit_button("Entrer", type="primary", use_container_width=True)
                
                if submitted:
                    if not name or not contact:
                        st.toast("Champs requis.")
                        return

                    # CHECK ADMIN
                    if name.upper() == ADMIN_KEY_NAME and contact == ADMIN_KEY_CONTACT:
                        st.session_state.login_stage = 'password'
                        st.session_state.temp_admin_name = name
                        st.session_state.temp_admin_contact = contact
                        st.rerun()
                    
                    # CLIENT NORMAL
                    else:
                        log_client_access(name, contact)
                        st.session_state.user = {"name": name, "contact": contact}
                        persist_login(name, contact)
                        st.session_state.login_stage = 'complete'
                        st.rerun()


def app_interface():
    # Sidebar
    with st.sidebar:
        user = st.session_state.user
        
        # Carte Profil
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-avatar">{get_initials(user['name'])}</div>
            <div style="font-weight:600; font-size:1.1em;">{user['name']}</div>
            <div style="font-size:0.85em; opacity:0.8;">{user['contact']}</div>
            {f'<div style="font-size:0.8em; margin-top:5px; background:#f97316; padding: 4px; border-radius:4px;">ADMIN MODE</div>' if st.session_state.is_admin else ''}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()

        if st.session_state.is_admin:
            st.markdown("### 🛠️ Gestion")
            if st.button("🚪 Retour au Login / Déconnexion"):
                clear_login()
                st.rerun()
            return
        
        # Interface Client: suite
        st.metric("📦 Panier", f"{len(st.session_state.cart)} articles")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Déconnexion", use_container_width=True):
            clear_login()
            st.rerun()

    if st.session_state.is_admin:
        admin_dashboard()
        return

    # Magasin
    st.markdown("""
    <div class="hero-cereza">
        <h1>Bienvenue sur Cereza.</h1>
        <p>Espace de commande privé.</p>
    </div>
    """, unsafe_allow_html=True)

    c_form, c_cart = st.columns([1.3, 1], gap="large")
    
    with c_form:
        st.subheader("Nouvelle demande")
        with st.form("add", clear_on_submit=True):
            st.text_input("Produit", key="input_name")
            c1, c2 = st.columns(2)
            with c1: st.number_input("Qté", 1, key="input_qty")
            with c2: st.text_input("Lien", key="input_link")
            st.text_area("Détails", key="input_desc")
            st.form_submit_button("Ajouter", type="primary", on_click=add_to_cart_callback)

    with c_cart:
        st.subheader("Votre sélection")
        if not st.session_state.cart:
            st.info("Vide.")
        else:
            for item in st.session_state.cart:
                html_card = f"""
<div class="order-card">
    <div style="font-weight:700; color:#0f172a; font-size:1.05rem;">{item.name}</div>
    <div style="font-size:0.9rem; color:#64748b; margin-top:5px;">
        Quantité: <b>{item.quantity}</b> • {item.description}
    </div>
</div>
"""
                st.markdown(html_card, unsafe_allow_html=True)
            
            c_a, c_b = st.columns([1,2])
            with c_a: st.button("Vider", on_click=clear_cart_callback)
            with c_b:
                if st.button("Commander", type="primary", use_container_width=True):
                    ok, err = save_order_excel(st.session_state.user, st.session_state.cart)
                    if ok:
                        send_email_notification(st.session_state.user, st.session_state.cart)
                        st.success("✅ Commande enregistrée avec succès !")
                        st.session_state.cart = []
                    else: st.error(err)

if __name__ == "__main__":
    init_session()
    inject_css()
    if not st.session_state.user: login_screen()
    else: app_interface()
