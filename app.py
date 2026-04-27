import streamlit as st
import pandas as pd
import plotly.express as px

from backend.supabase_client import supabase
from backend.model import Model
from backend.utils import risk_level

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="EduPulse Analytics", layout="wide")

# =========================
# STYLE
# =========================
st.markdown("""
<style>

.stApp {
    background-color: #0b1220;
    color: #e5e7eb;
}

.block-container {
    padding: 2rem;
}

h1 {
    color: #60a5fa;
}

h2, h3 {
    color: #e5e7eb;
}

[data-testid="stSidebar"] {
    background-color: #0f172a;
}

div.stMetric {
    background-color: #111827;
    border-radius: 12px;
    padding: 10px;
}

.stButton>button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
st.markdown("""
<h1 style='text-align:center;'>📊 EduPulse Analytics</h1>
<h4 style='text-align:center; color:gray;'>
Système d’analyse des performances académiques des étudiants
</h4>
<hr>
""", unsafe_allow_html=True)

# =========================
# PRESENTATION (NOUVEAU)
# =========================
st.markdown("""
<div style="
    background-color: #111827;
    padding: 15px;
    border-radius: 10px;
    color: #e5e7eb;
    font-size: 16px;
    line-height: 1.6;
    border-left: 5px solid #60a5fa;
">

🎯 <b>EduPulse Analytics</b> est une application de data science qui permet de collecter et d'analyser les performances académiques des étudiants à partir de leurs habitudes de travail (étude, sommeil, stress et assiduité). Elle permet aussi de prédire les résultats et d’identifier les étudiants à risque afin d’améliorer la réussite scolaire.
</div>
""", unsafe_allow_html=True)
# =========================
# SIDEBAR - AJOUT
# =========================
st.sidebar.header("➕ Ajouter un étudiant")

nom = st.sidebar.text_input("Nom", key="nom_add")
sexe = st.sidebar.selectbox("Sexe", ["Homme", "Femme"], key="sexe_add")

moyenne = st.sidebar.number_input("Moyenne générale", min_value=0.0, key="moyenne_add")

nb_heures_etude = st.sidebar.number_input("Heures d'étude", min_value=0, key="etude_add")
nb_heures_sommeil = st.sidebar.number_input("Heures de sommeil", min_value=0, key="sommeil_add")

niveau_stress = st.sidebar.slider("Stress", 1, 10, key="stress_add")
niveau_assiduite = st.sidebar.slider("Assiduité", 1, 10, key="assiduite_add")

if st.sidebar.button("Enregistrer"):
    supabase.table("etudiants").insert({
        "nom": nom,
        "sexe": sexe,
        "moyenne": moyenne,
        "nb_heures_etude": nb_heures_etude,
        "nb_heures_sommeil": nb_heures_sommeil,
        "niveau_stress": niveau_stress,
        "niveau_assiduite": niveau_assiduite
    }).execute()

    st.sidebar.success("✔ Données enregistrées")

# =========================
# DATA
# =========================
data = supabase.table("etudiants").select("*").execute().data
df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠️ Aucune donnée disponible")
    st.stop()

# =========================
# MODEL
# =========================
X = df[
    [
        "nb_heures_etude",
        "nb_heures_sommeil",
        "niveau_stress",
        "niveau_assiduite"
    ]
]
y = df["moyenne"]

model = Model()
model.train(X, y)

df["prediction"] = model.predict(X)
df["niveau"] = df["prediction"].apply(risk_level)

score = model.score(X, y)

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard",
    "👥 Étudiants",
    "📈 Analyses",
    "🧠 Intelligence"
])

# =========================
# TAB 1
# =========================
with tab1:
    st.subheader("📊 Vue globale")

    col1, col2, col3 = st.columns(3)

    col1.metric("Moyenne", f"{df['moyenne'].mean():.2f}")
    col2.metric("Variance", f"{df['moyenne'].var():.2f}")
    col3.metric("Écart-type", f"{df['moyenne'].std():.2f}")

    st.metric("📈 Score du modèle (R²)", f"{score:.2f}")

    # =========================
    # BAR CHART ETUDE
    # =========================
    st.markdown("## 📚 Étude vs Performance")

    fig1 = px.bar(
        df,
        x="nom",
        y="moyenne",
        color="nb_heures_etude",
        template="plotly_dark"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # =========================
    # BAR CHART SOMMEIL
    # =========================
    st.markdown("## 😴 Sommeil vs Performance")

    fig2 = px.bar(
        df,
        x="nom",
        y="moyenne",
        color="nb_heures_sommeil",
        template="plotly_dark"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # BAR CHART STRESS
    # =========================
    st.markdown("## ⚠️ Stress vs Performance")

    fig3 = px.bar(
        df,
        x="nom",
        y="moyenne",
        color="niveau_stress",
        template="plotly_dark"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # =========================
    # SEXE
    # =========================
    st.markdown("## 🥧 Répartition par sexe")

    fig4 = px.pie(df, names="sexe", hole=0.4, template="plotly_dark")
    st.plotly_chart(fig4, use_container_width=True)

    # =========================
    # NIVEAU
    # =========================
    st.markdown("## 🥧 Répartition des niveaux")

    fig5 = px.pie(df, names="niveau", hole=0.4, template="plotly_dark")
    st.plotly_chart(fig5, use_container_width=True)

    # =========================
    # RAPPORT
    # =========================
    st.markdown("## 📄 Rapport global")

    mean_perf = df["moyenne"].mean()

    if mean_perf < 10:
        st.error("📉 Niveau global faible.")
    elif mean_perf < 14:
        st.warning("📊 Niveau moyen.")
    else:
        st.success("📈 Bon niveau global.")

    st.markdown("📌 Rapport généré automatiquement à partir des données.")

# =========================
# TAB 2
# =========================
with tab2:
    st.subheader("👥 Étudiants")

    filtre = st.selectbox("Filtrer", ["Tous", "Homme", "Femme"], key="filtre")

    if filtre != "Tous":
        df_show = df[df["sexe"] == filtre]
    else:
        df_show = df

    st.dataframe(df_show)

# =========================
# TAB 3
# =========================
with tab3:
    st.subheader("📈 Analyses")

    st.dataframe(df.corr(numeric_only=True))
    st.dataframe(df[["nom", "moyenne", "prediction"]])

# =========================
# TAB 4
# =========================
with tab4:
    st.subheader("🧠 Prédiction")

    col1, col2 = st.columns(2)

    etude = col1.number_input("Heures d'étude", min_value=0, key="etude_pred")
    sommeil = col1.number_input("Heures de sommeil", min_value=0, key="sommeil_pred")

    stress = col2.slider("Stress", 1, 10, key="stress_pred")
    assiduite = col2.slider("Assiduité", 1, 10, key="assiduite_pred")

    if st.button("Prédire"):

        input_data = pd.DataFrame([{
            "nb_heures_etude": etude,
            "nb_heures_sommeil": sommeil,
            "niveau_stress": stress,
            "niveau_assiduite": assiduite
        }])

        prediction = model.predict(input_data)[0]
        niveau = risk_level(prediction)

        st.success(f"📊 Moyenne prédite : {prediction:.2f}")
        st.info(f"🎯 Niveau : {niveau}")

# =========================
# FOOTER
# =========================
st.markdown("""
<hr>
<p style='text-align:center; color:gray;'>
Projet réalisé par <b>DONGMO TCHUDZO CHRISTELLE NIQUOIZE</b>
</p>
""", unsafe_allow_html=True)