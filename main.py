import streamlit as st
from supabase import create_client
import pandas as pd
import altair as alt

# --- Page Config ---
st.set_page_config(page_title="Job Dashboard", layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.title {
    color: #2c3e50;
    font-weight: bold;
}
.highlight {
    color: #27ae60;
    font-size: 20px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- Supabase setup ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(url, key)

# --- App Title ---
st.title("🤔 Choosing the Right Job Offer")

# --- Fetch data ---
response = supabase.table("analysis").select("*").execute()
data = response.data or []

if not data:
    st.warning("No analysis records found.")
else:
    for row in data:

        st.markdown("## 📊 Choosing Between Three Offers")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(f"{url}/storage/v1/object/public/charts/1.ChoosingBetweenOffers.png")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("## 🗺 Countries With Remote Opportunities")
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(f"{url}/storage/v1/object/public/charts/2.RemoteJobsWorldWideMap.png")
        st.markdown('</div>', unsafe_allow_html=True)

        # -----------------------------
        # 🎯 OFFERS SECTION
        # -----------------------------
        st.markdown("### 🧾 Job Offers")

        offers = row.get("offers", {})
        offered_salaries = []

        if isinstance(offers, dict) and offers:
            offer_labels = {}
            for key, val in offers.items():
                if isinstance(val, dict):
                    label = f"{val.get('job_title', 'Unknown')} ({key})"
                else:
                    label = key
                offer_labels[label] = key
                offered_salaries.append(offers[key]["salary_in_usd"])

            selected_label = st.selectbox(
                "Select an Offer",
                options=list(offer_labels.keys()),
                key=f"offer_{row['id']}"
            )

            selected_key = offer_labels[selected_label]
            selected_offer = offers[selected_key]

            # --- Beautiful Card Layout ---
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📄 Offer Details")

            if isinstance(selected_offer, dict):
                col1, col2 = st.columns(2)

                items = list(selected_offer.items())

                for i, (k, v) in enumerate(items):
                    if i % 2 == 0:
                        with col1:
                            st.markdown(f"**{k.replace('_',' ').title()}**")
                            st.write(v)
                    else:
                        with col2:
                            st.markdown(f"**{k.replace('_',' ').title()}**")
                            st.write(v)
            else:
                st.write(selected_offer)

            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("No offers available.")
        
        st.markdown("## 📊 Predicted vs Offered Salaries")
        
        predicted_salaries = row.get("predicted_salaries", [])
        predicted_salaries = [float(s) for s in predicted_salaries]

        df = pd.DataFrame({
            "Offer": ["Data Scientist", "ML Scientist", "ML Engineer"],
            "Salary offered": offered_salaries,
            "Salary_predicted": predicted_salaries
        })

        # Convert to long format for grouped bars
        df_long = df.melt(
            id_vars="Offer",
            var_name="Type",
            value_name="Salary"
        )

        # Streamlit card wrapper
        st.markdown('<div class="card">', unsafe_allow_html=True)

        chart = (
            alt.Chart(df_long)
            .mark_bar()
            .encode(
                x=alt.X("Offer:N", title="Offer"),
                xOffset="Type:N",   # <-- this makes bars sit side-by-side
                y=alt.Y("Salary:Q", title="Salary"),
            color="Type:N"
            )
        .properties(width=600)
        )

        st.altair_chart(chart, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)


        # -----------------------------
        # 💡 EXPLANATIONS SECTION
        # -----------------------------
        st.markdown("### 💡 Offer Insights")

        explanations = [
            row.get("offer1_explanation"),
            row.get("offer2_explanation"),
            row.get("offer3_explanation"),
        ]

        explanations = [e for e in explanations if e]

        if explanations:
            index = st.slider(
                "Browse insights",
                0,
                len(explanations) - 1,
                0,
                key=f"slider_{row['id']}"
            )

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(explanations[index])
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.info("No explanations available.")

        # -----------------------------
        # 📈 SCORES SECTION
        # -----------------------------
        st.markdown("### 📈 Offers Scores")

        scores = row.get("scores", [])

        if scores:
            try:
                scores = [float(s) for s in scores]

                df = pd.DataFrame({
                    "Offer": [f"Offer {job_title}" for job_title in ["Data Scientist", "ML Scientist", "ML Engineer"]],
                    "Score": scores
                })

                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.bar_chart(df.set_index("Offer"))
                st.markdown('</div>', unsafe_allow_html=True)

            except:
                st.warning("Scores format is invalid.")
        else:
            st.info("No scores available.")

        st.markdown("---")
