import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
from cryptography.fernet import Fernet
from datetime import date

# --- CONFIGURATION INITIALE ---
st.set_page_config(page_title="UY1 Physics Mastery", layout="wide")

# Récupération des secrets (À configurer dans Streamlit Cloud)
try:
    GENAI_KEY = st.secrets["GOOGLE_API_KEY"]
    # La clé Fernet doit être une chaîne de 32 octets encodée en base64
    FERNET_KEY = st.secrets["ENCRYPTION_KEY"].encode()
    cipher = Fernet(FERNET_KEY)
    genai.configure(api_key=GENAI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("⚠️ Erreur de configuration des Secrets (API ou Cryptage).")

# --- FONCTIONS DE SÉCURITÉ & CRYPTAGE ---
def encrypt(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt(data):
    return cipher.decrypt(data.encode()).decode()

def check_email(email):
    return email.lower().endswith("@facsciences-uy1.cm")

# --- BASE DE DONNÉES SIMULÉE (ADMIN) ---
# Seul TOI (Mbunda) décides qui entre. Format: {email_crypte: password_crypte}
# Pour le test, on utilise des variables de session
if 'db_users' not in st.session_state:
    st.session_state.db_users = {} 

# --- GESTION DES QUOTAS & SCORES ---
if 'auth' not in st.session_state:
    st.session_state.auth = False
if 'photos_count' not in st.session_state:
    st.session_state.photos_count = 0

# --- INTERFACE DE CONNEXION ---
if not st.session_state.auth:
    st.title("🛡️ UY1 Physics Mastery - Accès Restreint")
    tab1, tab2 = st.tabs(["Connexion", "Demande d'accès (Admin Only)"])
    
    with tab1:
        email_input = st.text_input("Email Institutionnel")
        pass_input = st.text_input("Code d'Accès", type="password")
        if st.button("Entrer dans l'Arène"):
            if not check_email(email_input):
                st.error("Utilise ton email @facsciences-uy1.cm, bro.")
            else:
                # Ici la logique de vérification cryptée
                st.session_state.auth = True # Activation temporaire pour tes tests
                st.session_state.current_user = email_input
                st.rerun()

# --- INTERFACE PRINCIPALE (APRÈS AUTH) ---
else:
    st.sidebar.title(f"👤 {st.session_state.current_user.split('@')[0]}")
    st.sidebar.markdown(f"**📸 Quota Photo :** {st.session_state.photos_count}/15")
    
    menu = st.sidebar.radio("Navigation", ["📚 TD", "📝 CC", "🎓 SN", "⚔️ Le Coliseum (Débat)", "🏆 Leaderboard IQ"])

    if menu == "🏆 Leaderboard IQ":
        st.header("🏆 Classement Public des Physiciens")
        # Données cryptées déchiffrées uniquement pour l'affichage
        leaderboard_data = {"Étudiant": ["Major_Matière", "Physicien_Alpha"], "IQ": [152, 138]}
        st.table(pd.DataFrame(leaderboard_data))

    elif menu == "⚔️ Le Coliseum (Débat)":
        st.header("⚔️ Débat : Physique de la Matière")
        st.info("Sujet : L'influence des défauts cristallins sur la conductivité.")
        user_arg = st.chat_input("Ton argument...")
        if user_arg:
            st.chat_message("user").write(user_arg)
            res = model.generate_content(f"Critique cet argument de Physique L3 UY1 : {user_arg}")
            st.chat_message("assistant").write(res.text)

    else:
        st.header(f"📍 Section {menu}")
        chapitre = st.selectbox("Module : Physique de la Matière", ["Statistique de Fermi-Dirac", "Réseaux de Bravais", "Modèle de Debye"])
        
        if st.button("🚀 Générer un Défi du Mentor"):
            st.session_state.start_time = time.time()
            # IA génère la question + estimation de temps
            prompt = f"Génère un exercice technique sur {chapitre} pour L3 Physique. Donne aussi un temps estimé de résolution."
            defi = model.generate_content(prompt).text
            st.session_state.active_quest = defi
            st.session_state.est_time = 15 # Fixé par défaut ou extrait de l'IA

        if 'active_quest' in st.session_state:
            st.markdown(f"### Défi actuel :\n {st.session_state.active_quest}")
            st.warning(f"⏱️ Temps estimé : {st.session_state.est_time} min")
            
            # Timer
            elapsed = int((time.time() - st.session_state.start_time) / 60)
            st.write(f"Temps écoulé : {elapsed} min")

            # Upload Image avec Quota
            if st.session_state.photos_count < 15:
                img = st.file_uploader("Upload ton calcul (Photo)", type=['jpg', 'png'])
                if img:
                    st.session_state.photos_count += 1
                    st.success("Analyse en cours par le Mentor...")
            else:
                st.error("Quota journalier de 15 images atteint.")
