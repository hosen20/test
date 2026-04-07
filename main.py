import streamlit as st
from supabase import create_client

# --- Secure Supabase setup ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(url, key)

st.title("💼 Salary Prediction Dashboard")

# --- Fetch data ---
response = supabase.table("predictions").select("*").execute()
data = response.data or []

if not data:
    st.warning("No predictions found in Supabase yet.")
else:
    # Safe extraction of job titles
    job_titles = list({
        row.get("inputs", {}).get("job_title")
        for row in data
        if row.get("inputs", {}).get("job_title")
    })

    selected_job = st.sidebar.selectbox("Filter by Job Title", ["All"] + job_titles)

    # Display records
    for row in data:
        inputs = row.get("inputs", {})

        if selected_job != "All" and inputs.get("job_title") != selected_job:
            continue

        st.subheader(f"Job: {inputs.get('job_title', 'Unknown')}")
        st.write(f"Experience: {inputs.get('experience_level', 'N/A')}")
        st.write(f"Employment Type: {inputs.get('employment_type', 'N/A')}")
        st.write(f"Company Size: {inputs.get('company_size', 'N/A')}")

        st.write(f"💰 **Predicted Salary:** ${row.get('predicted_salary', 'N/A')}")
        st.write(row.get("narrative", "No narrative available."))

        if row.get("chart_url"):
            st.image(row["chart_url"], caption="Salary Landscape Chart")
        else:
            st.info("No chart available for this record.")

        st.markdown("---")
