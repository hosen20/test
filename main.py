import streamlit as st
from supabase import create_client

url = "https://hwxfcsyvvrogbhmtszih.supabase.co"
key = st.secrets["ANON_KEY"]
supabase = create_client(url, key)

st.title("Salary Prediction Dashboard")

data = supabase.table("predictions").select("*").order("created_at", desc=True).execute().data

if not data:
    st.warning("No predictions yet.")
else:
    for row in data:
        st.subheader("Prediction")

        st.json(row["inputs"])
        st.metric("Predicted Salary", f"${row['predicted_salary']:,.0f}")
        st.write(row["narrative"])

        if row["chart_url"]:
            st.image(row["chart_url"])
