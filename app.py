"""
CEREZA - Plateforme Complète
Version: Production + Admin Dashboard
Features:
- Clients: Commande fluide sans blocage
- Admin: Dashboard temps réel pour voir les commandes sans toucher au fichier Excel
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

# Mot de passe Admin (Simple pour MVP)
ADMIN_PASSWORD = "cereza_admin" 

@dataclass
class Product:
    name: str
    quantity: int
    description: str = ""
    link: str = ""

def init_session():
    if "cart" not in st.session_state: st.session_state.cart = []
    if "user" not in st.session_state: st.session_state.user = None
    if "is_admin" not in st.session_state: st.session_state.is_admin = False

# --- 2. CSS ---
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
        
        /* Elements */
        .profile-card {
            background: linear-gradient(135deg, var(--cold-primary) 0%, var(--cold-secondary) 100%);
            border-radius: 16px; padding: 20px; text-align: center; color: white;
            margin-bottom: 20px; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
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
        /* Admin Badge */
        .admin-badge {
            background-color: #ef4444; color: white; padding: 4px 8px; 
            border-radius: 4px; font-size: 0.7em; font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FONCTIONS DATA ---

def add_to_cart_callback():
    name = st.session_state.get("input_name", "")
    qty = st.session_state.get("input_qty", 1)
    link = st.session_state.get("input_link", "")
    desc = st.session_state.get("input_desc", "")
    if name:
        st.session_state.cart.append(Product(name, qty, desc, link))
        st.toast(f"✅ {name} ajouté !")

def clear_cart_callback():
    st.session_state.cart = []

def get_initials(fullname):
    parts = fullname.split()
    return f"{parts[0][0]}{parts[1][0]}".upper() if len(parts) >= 2 else fullname[:2].upper()

def log_client_access(name, email):
    try:
        exists = FILE_CLIENTS.exists()
        with open(FILE_CLIENTS, 'a', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            if not exists: w.writerow(["Date", "Nom", "Email"])
            w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name.upper(), email.lower()])
    except: pass

def save_order_excel(user, cart):
    try:
        exists = FILE_COMMANDES.exists()
        oid = datetime.now().strftime('%Y%m%d-%H%M%S')
        with open(FILE_COMMANDES, 'a', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f, delimiter=';')
            if not exists: w.writerow(["ID", "Date", "Client", "Email", "Produit", "Qte", "Desc", "Lien"])
            for i in cart:
                w.writerow([oid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user['name'], user['email'], i.name, i.quantity, i.description, i.link])
        return True, ""
    except PermissionError:
        return False, "⚠️ Fichier verrouillé par Excel."
    except Exception as e:
        return False, str(e)

def send_email_notification(user, cart):
    # (Code email identique - raccourci pour la lisibilité)
    try:
        user_smtp = st.secrets.get("SMTP_USER") or os.getenv("SMTP_USER")
        pwd_smtp = st.secrets.get("SMTP_PASSWORD") or os.getenv("SMTP_PASSWORD")
        if not user_smtp: return False
        
        msg = MIMEMultipart()
        msg['Subject'] = f"🍒 Commande Cereza: {user['name']}"
        msg['From'] = user_smtp
        msg['To'] = "madouange48@gmail.com"
        
        html = "<ul>" + "".join([f"<li>{p.name} (x{p.quantity})</li>" for p in cart]) + "</ul>"
        msg.attach(MIMEText(html, 'html'))
        
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls(); s.login(user_smtp, pwd_smtp)
        s.sendmail(user_smtp, "madouange48@gmail.com", msg.as_string())
        s.quit()
        return True
    except: return False

# --- 4. INTERFACE ADMIN ---

def admin_dashboard():
    st.markdown("## 🦅 Dashboard Superviseur")
    st.info("Vous visualisez les données en temps réel. Cela ne bloque pas les commandes clients.")
    
    tab1, tab2 = st.tabs(["Commandes Récentes", "Base Clients"])
    
    with tab1:
        if FILE_COMMANDES.exists():
            # Lecture avec Pandas (Lecture seule = Pas de lock)
            df = pd.read_csv(FILE_COMMANDES, sep=';', encoding='utf-8-sig')
            st.dataframe(df, use_container_width=True)
            
            # Bouton de téléchargement sûr
            with open(FILE_COMMANDES, "rb") as f:
                st.download_button(
                    label="📥 Télécharger Excel (Copie Sécurisée)",
                    data=f,
                    file_name="cereza_commandes.csv",
                    mime="text/csv"
                )
        else:
            st.warning("Aucune commande pour le moment.")
            
    with tab2:
        if FILE_CLIENTS.exists():
            df_clients = pd.read_csv(FILE_CLIENTS, sep=';', encoding='utf-8-sig')
            st.dataframe(df_clients, use_container_width=True)
        else:
            st.warning("Aucun client enregistré.")

# --- 5. INTERFACE CLIENT ---

def login_screen():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; color:#0f172a;'>CEREZA</h1>", unsafe_allow_html=True)
        with st.form("login"):
            name = st.text_input("Nom")
            email = st.text_input("Email")
            if st.form_submit_button("Entrer", type="primary", use_container_width=True):
                if name and email:
                    log_client_access(name, email)
                    st.session_state.user = {"name": name, "email": email}
                    st.rerun()

def app_interface():
    # Sidebar
    with st.sidebar:
        user = st.session_state.user
        
        # Carte Profil
        st.markdown(f"""
        <div class="profile-card">
            <div style="font-size:24px; font-weight:bold; margin-bottom:10px;">
                {get_initials(user['name'])}
            </div>
            <div>{user['name']}</div>
            <div style="font-size:0.8em; opacity:0.8;">{user['email']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.metric("📦 Panier", f"{len(st.session_state.cart)}")
        
        # Zone Admin Secrète
        with st.expander("🔐 Accès Admin"):
            pwd = st.text_input("Mot de passe", type="password")
            if st.button("Connexion Admin"):
                if pwd == ADMIN_PASSWORD:
                    st.session_state.is_admin = True
                    st.rerun()
                else:
                    st.error("Accès refusé")

        if st.session_state.is_admin:
            if st.button("🔴 Quitter Admin", type="primary"):
                st.session_state.is_admin = False
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Déconnexion"):
            st.session_state.user = None; st.session_state.is_admin = False
            st.rerun()

    # Si Admin est actif, on affiche le Dashboard au lieu du magasin
    if st.session_state.is_admin:
        admin_dashboard()
        return

    # Sinon, affichage Magasin normal
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
                st.markdown(f"""
                <div class="order-card">
                    <b>{item.name}</b> (x{item.quantity})<br>
                    <small>{item.description}</small>
                </div>""", unsafe_allow_html=True)
            
            c_a, c_b = st.columns([1,2])
            with c_a: st.button("Vider", on_click=clear_cart_callback)
            with c_b:
                if st.button("Commander", type="primary", use_container_width=True):
                    ok, err = save_order_excel(st.session_state.user, st.session_state.cart)
                    if ok:
                        send_email_notification(st.session_state.user, st.session_state.cart)
                        st.balloons(); st.success("Envoyé !")
                        st.session_state.cart = []
                    else: st.error(err)

if __name__ == "__main__":
    init_session()
    inject_css()
    if not st.session_state.user: login_screen()
    else: app_interface()