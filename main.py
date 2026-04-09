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
        # 🎯 OFFERS SECTION
        # -----------------------------
        st.markdown("### 🧾 Job Offers")

        offers = row.get("offers", [])

        if offers:
            offer_labels = []
            offer_map = {}

            for i, offer in enumerate(offers):
                # Create readable label
                if isinstance(offer, dict):
                    label = offer.get("job_title", f"Offer {i+1}")
                else:
                    label = f"Offer {i+1}"

                offer_labels.append(label)
                offer_map[label] = offer

            selected_label = st.selectbox(
                "Select an Offer",
                options=offer_labels,
                key=f"offer_{row['id']}"
            )

            selected_offer = offer_map[selected_label]

            # --- Display full offer details ---
            st.markdown("#### 📄 Offer Details")

            if isinstance(selected_offer, dict):
                for key, value in selected_offer.items():
                    st.write(f"**{key.replace('_', ' ').title()}**: {value}")
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
                # convert to float if needed
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
