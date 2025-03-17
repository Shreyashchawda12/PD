import streamlit as st
import pandas as pd
from io import BytesIO

# Load the data from the uploaded file

PD_FILE_PATH = 'artifacts/VIL PD Alarm - Final (2).xlsx'

@st.cache_data(ttl=0)
def load_data(file_path):
    data = pd.read_excel(file_path)
    data.columns = data.columns.str.strip()
    data['Date'] = pd.to_datetime(data['Date']).dt.date
    data['GID'] = data['GID'].astype(str)
    return data

def to_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        data.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return output

def main():
    st.title("VIL PD RCA UPDATES")
    
    # PD Data Section
    st.header("📊 PD Data")
    df1 = pd.read_excel(PD_FILE_PATH)
    
    pd_data = df1[df1['2025 PD Count'].notna() & (df1['2025 PD Count'] != '')]
    
    if not pd_data.empty:
        pd_cluster_options = sorted(pd_data['Cluster'].dropna().unique())
        selected_pd_cluster = st.selectbox("Select Cluster for PD Data", pd_cluster_options)
        
        pd_ce_options = sorted(pd_data[pd_data['Cluster'] == selected_pd_cluster]['CE'].dropna().unique())
        selected_pd_ce = st.selectbox("Select CE for PD Data", pd_ce_options)
        
        filtered_pd_data = pd_data[(pd_data['Cluster'] == selected_pd_cluster) & (pd_data['CE'] == selected_pd_ce)]
        
        st.write("Filtered PD Data")
        pd_display_columns = ["Site ID","Global ID","Site Name","Cluster","CE","RCA-1","RCA-2","Action Plan","Status","Closure Date/TAT","Jan-25","Feb-25","Mar-25","2025 PD Count"]
        st.dataframe(filtered_pd_data[pd_display_columns], width=1600)
        
        # Update section
        selected_site = st.selectbox("Select Site  to update", filtered_pd_data["Site Name"].unique())
        site_data = filtered_pd_data[filtered_pd_data["Site ID"] == selected_site]
        
        RCA1 = st.text_input("RCA-1", site_data["RCA-1"].values[0] if not site_data["RCA-1"].isnull().all() else "")
        RCA2 = st.text_input("RCA-2", site_data["RCA-2"].values[0] if not site_data["RCA-2"].isnull().all() else "")
        action_plan = st.text_input("Action Plan", site_data["Action Plan"].values[0] if not site_data["Action Plan"].isnull().all() else "")
        status = st.text_input("Status", site_data["Status"].values[0] if not site_data["Status"].isnull().all() else "")
        closure_date_tat = st.text_input("Closure Date/TAT", site_data["Closure Date/TAT"].values[0] if not site_data["Closure Date/TAT"].isnull().all() else "")
        
        if st.button("Update PD Data"):
            df1.loc[df1["Site ID"] == selected_site, ["RCA-1", "RCA-2", "Action Plan", "Status", "Closure Date/TAT"]] = [RCA1, RCA2, action_plan, status, closure_date_tat]
            df1.to_excel(PD_FILE_PATH, index=False)
            st.success("PD Data updated successfully.")
    else:
        st.warning("No PD data available.")
    
    # Download button for PD data
    excel_data = to_excel(df1)
    st.sidebar.download_button(
        label="Download Modified PD Excel File",
        data=excel_data,
        file_name="modified_PD_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    main()
