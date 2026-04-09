import streamlit as st
from supabase import create_client

# --- Secure Supabase setup ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
supabase = create_client(url, key)

st.title("💼 Salary Prediction Dashboard")

# --- Fetch data ---
response = supabase.table("predictions").select("*").order("created_at", desc=True).execute()
data = response.data or []

# Base Supabase storage URL (OPTION 1 FIX)
BASE_STORAGE_URL = f"{url}/storage/v1/object/public/charts"

if not data:
    st.warning("No predictions found in Supabase yet.")
else:
    # --- Safe extraction of job titles ---
    job_titles = list({
        row.get("inputs", {}).get("job_title")
        for row in data
        if row.get("inputs", {}).get("job_title")
    })

    selected_job = st.sidebar.selectbox(
        "Filter by Job Title",
        ["All"] + sorted(job_titles)
    )

    # --- Display records ---
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

        # --- FIXED IMAGE HANDLING (Option 1) ---
        if row.get("chart_url"):
            # extract filename from stored value
            file_name = row["chart_url"].split("/")[-1]

            # rebuild full public URL
            public_url = f"{BASE_STORAGE_URL}/{file_name}"

            st.image(public_url, caption="Salary Landscape Chart", use_container_width=True)
        else:
            st.info("No chart available for this record.")

        st.markdown("---")
