import streamlit as st
import pandas as pd
from io import BytesIO

# PD Data File Path
PD_FILE_PATH = 'VIL PD Alarm - Final (2).xlsx'

@st.cache_data(ttl=0)
def load_pd_data(file_path):
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # Remove spaces from column names
    return df

def to_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

def main():
    st.title("📊 VIL PD RCA UPDATES")

    # Load PD data
    df1 = load_pd_data(PD_FILE_PATH)

    # Filter PD data where '2025 PD Count' is not blank
    pd_data = df1[df1['2025 PD Count'].notna() & (df1['2025 PD Count'] != '')]

    if not pd_data.empty:
        # Step 1: Select Cluster
        pd_cluster_options = sorted(pd_data['Cluster'].dropna().unique())
        selected_pd_cluster = st.selectbox("Select Cluster for PD Data", pd_cluster_options)

        # Step 2: Select CE based on Cluster
        pd_ce_options = sorted(pd_data[pd_data['Cluster'] == selected_pd_cluster]['CE'].dropna().unique())
        selected_pd_ce = st.selectbox("Select CE for PD Data", pd_ce_options)

        # Step 3: Filter data based on Cluster and CE
        filtered_pd_data = pd_data[(pd_data['Cluster'] == selected_pd_cluster) & (pd_data['CE'] == selected_pd_ce)]

        # Step 4: Select Site
        st.write("Filtered PD Data")
        pd_display_columns = ["Site ID", "Global ID", "Site Name", "Cluster", "CE", "RCA-1", "RCA-2", "Action Plan", "Status", "Closure Date/TAT", "Jan-25", "Feb-25", "Mar-25", "2025 PD Count"]
        st.dataframe(filtered_pd_data[pd_display_columns], width=1600)

        selected_site = st.selectbox("Select Site Name to Update", filtered_pd_data["Site Name"].unique())

        # Get data of selected site
        site_data = filtered_pd_data[filtered_pd_data["Site Name"] == selected_site]

        # Ensure site_data is not empty before accessing values
        def get_value(column):
            return site_data[column].values[0] if not site_data[column].isnull().all() else ""

        # Input fields with pre-filled values
        RCA1 = st.text_input("RCA-1", get_value("RCA-1"))
        RCA2 = st.text_input("RCA-2", get_value("RCA-2"))
        action_plan = st.text_input("Action Plan", get_value("Action Plan"))
        status = st.text_input("Status", get_value("Status"))
        closure_date_tat = st.text_input("Closure Date/TAT", get_value("Closure Date/TAT"))

        # Update button
        if st.button("Update PD Data"):
            df1.loc[df1["Site Name"] == selected_site, ["RCA-1", "RCA-2", "Action Plan", "Status", "Closure Date/TAT"]] = [RCA1, RCA2, action_plan, status, closure_date_tat]
            df1.to_excel(PD_FILE_PATH, index=False)
            st.success("PD Data updated successfully.")

        # Download button for updated PD data
        excel_data = to_excel(df1)
        st.sidebar.download_button(
            label="Download Modified PD Excel File",
            data=excel_data,
            file_name="modified_PD_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("No PD data available.")

if __name__ == "__main__":
    main()
