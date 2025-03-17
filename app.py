import streamlit as st
import pandas as pd

# Load the data from the uploaded file
FILE_PATH = 'artifacts/clean_data.xlsx'

@st.cache_data
def load_data(file_path):
    # Load the Excel file and return as a DataFrame
    data = pd.read_excel(file_path)
    data.columns = data.columns.str.strip()  # Remove leading/trailing spaces
    data['Date'] = pd.to_datetime(data['Date']).dt.date  # Convert Date to date format only
    data['GID'] = data['GID'].fillna(0).astype(int) 
    return data

# Filter function to get CE options based on Cluster
def get_ce_options(data, selected_cluster):
    return data[data['Cluster'] == selected_cluster]['CE'].unique()

# Filter function to get GID options based on Cluster and CE
def get_gid_options(data, selected_cluster, selected_ce):
    return data[(data['Cluster'] == selected_cluster) & (data['CE'] == selected_ce)]['GID'].unique()

# Filter function based on Cluster, CE, and GID selections
def filter_data(data, selected_cluster, selected_ce, selected_gid):
    return data[(data['Cluster'] == selected_cluster) & (data['CE'] == selected_ce) & (data['GID'] == selected_gid)].copy()

# Main Streamlit app function
def main():
    # Load and display title
    st.title("VIL Data Dashboard")

    # Load data
    data = load_data(FILE_PATH)

    # Step 1: Select Cluster
    cluster_options = data['Cluster'].unique()
    selected_cluster = st.selectbox("Select Cluster", cluster_options)

    # Step 2: Select CE based on selected Cluster
    ce_options = get_ce_options(data, selected_cluster)
    selected_ce = st.selectbox("Select CE", ce_options)

    # Step 3: Select GID based on selected Cluster and CE (as string)
    gid_options = get_gid_options(data, selected_cluster, selected_ce)
    selected_gid = st.selectbox("Select GID", gid_options)  # GID displayed as string (char)

    # Step 4: Filter data based on selected Cluster, CE, and GID
    filtered_data = filter_data(data, selected_cluster, selected_ce, selected_gid)

    # Step 5: Select Date(s) for row selection
    date_options = filtered_data['Date'].unique()
    selected_dates = st.multiselect("Select Date(s)", date_options)

    # Filter the data to include only the selected dates
    rows_to_update = filtered_data[filtered_data['Date'].isin(selected_dates)]

    # Step 6: Display filtered data and update fields for selected rows
    if not rows_to_update.empty:
        # Display Filtered Data with increased height
        st.write("Filtered Data")
        display_columns = ['Date', 'GID', 'Site Name','APPALARMTIME','APPCANCELTIME','OUTAGEDURATION']
        st.dataframe(rows_to_update[display_columns],width=1600)  

        # Display Update Fields for the selected rows
        st.write("Update Fields for Selected Date(s)")

        # Input fields for updating RCA1, RCA2, Action Plan, Status, TAT
        RCA1 = st.text_input("RCA1")
        RCA2 = st.text_input("RCA2")
        action_plan = st.text_input("Action Plan")
        status = st.text_input("Status")
        TAT = st.text_input("TAT")

        # Apply changes to the selected rows
        if st.button("Apply Updates"):
            # Update the selected rows with the new values
            rows_to_update['RCA1'] = RCA1
            rows_to_update['RCA2'] = RCA2
            rows_to_update['Action Plan'] = action_plan
            rows_to_update['Status'] = status
            rows_to_update['TAT'] = TAT

            # Update the main data with the modified rows
            data.update(rows_to_update)

            # Save updated data to Excel
            try:
                data.to_excel(FILE_PATH, index=False)
                st.success("Data updated successfully.")
            except Exception as e:
                st.error(f"Error updating Excel file: {e}")
    else:
        st.warning("Please select dates to update.")

if __name__ == "__main__":
    main()
