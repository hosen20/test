import streamlit as st
from supabase import create_client
import pandas as pd

# --- Supabase setup ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(url, key)

# --- App Title ---
st.title("🤔 Job Search Confusion Dashboard")

# --- Fetch data ---
response = supabase.table("analysis").select("*").execute()
data = response.data or []

if not data:
    st.warning("No analysis records found.")
else:
    for row in data:
        st.markdown("## 📊 New Analysis")

        # -----------------------------
        # 🎯 OFFERS SECTION (FIXED)
        # -----------------------------
        st.markdown("### 🧾 Job Offers")

        offers = row.get("offers", {})

        if isinstance(offers, dict) and offers:
            # Create user-friendly labels
            offer_labels = {}
            for key, val in offers.items():
                if isinstance(val, dict):
                    label = f"{key} - {val.get('job_title', 'Unknown')}"
                else:
                    label = key
                offer_labels[label] = key

            selected_label = st.selectbox(
                "Select an Offer",
                options=list(offer_labels.keys()),
                key=f"offer_{row['id']}"
            )

            selected_key = offer_labels[selected_label]
            selected_offer = offers[selected_key]

            # --- Display full offer details ---
            st.markdown("#### 📄 Offer Details")

            if isinstance(selected_offer, dict):
                for k, v in selected_offer.items():
                    st.write(f"**{k.replace('_', ' ').title()}**: {v}")
            else:
                st.write(selected_offer)

        else:
            st.info("No offers available.")

        # -----------------------------
        # 💡 EXPLANATIONS SECTION
        # -----------------------------
        st.markdown("### 💡 Offer Explanations")

        explanations = [
            row.get("offer1_explanation"),
            row.get("offer2_explanation"),
            row.get("offer3_explanation"),
        ]

        explanations = [e for e in explanations if e]

        if explanations:
            index = st.slider(
                "Slide through explanations",
                0,
                len(explanations) - 1,
                0,
                key=f"slider_{row['id']}"
            )
            st.write(explanations[index])
        else:
            st.info("No explanations available.")

        # -----------------------------
        # 📈 SCORES SECTION
        # -----------------------------
        st.markdown("### 📈 Scores Comparison")

        scores = row.get("scores", [])

        if scores:
            try:
                scores = [float(s) for s in scores]

                df = pd.DataFrame({
                    "Offer": [f"Offer {i+1}" for i in range(len(scores))],
                    "Score": scores
                })

                st.bar_chart(df.set_index("Offer"))
            except:
                st.warning("Scores format is invalid.")
        else:
            st.info("No scores available.")

        st.markdown("---")
