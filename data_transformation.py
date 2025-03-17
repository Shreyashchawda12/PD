
import os
from push_data import MongoDBUploader
import pandas as pd

class DataFrameManager:
    def __init__(self, db_name, collection_name, drop_columns):
        """
        Initializes the DataFrameManager with MongoDB details and columns to drop.

        Parameters:
        db_name (str): The name of the MongoDB database.
        collection_name (str): The name of the collection to export from.
        drop_columns (list): List of columns to drop from the DataFrame.
        """
        self.uploader = MongoDBUploader(db_name=db_name, collection_name=collection_name)
        self.drop_columns = drop_columns
        self.df = None

    def export_data(self):
        """Exports data from MongoDB and stores it in a DataFrame."""
        self.df = self.uploader.export_from_mongo()
        print("Data exported from MongoDB.")

    def drop_unwanted_columns(self):
        """Drops specified columns from the DataFrame."""
        if self.df is not None:
            missing_columns = [col for col in self.drop_columns if col not in self.df.columns]
            if missing_columns:
                print(f"The following columns are not in the DataFrame and will be ignored: {missing_columns}")

            self.df.drop(columns=self.drop_columns, inplace=True, errors='ignore')  # Modify in-place
            print("Unwanted columns dropped.")

    def get_dataframe(self):
        
        """Returns the modified DataFrame."""
        return self.df

    def save_to_excel(self, filename="clean_data.xlsx"):
        """Saves the DataFrame to an Excel file in the artifacts folder."""
        artifacts = "artifacts"
        os.makedirs(artifacts, exist_ok=True)  # Create artifacts folder if it doesn't exist
        output_path = os.path.join(artifacts, filename)
        self.df.to_excel(output_path, index=False)
        print(f"Data saved to {output_path}")


# Example usage
if __name__ == "__main__":
    drop_data = [
        '_id', 'BSCNAME', 'BCF Name', 'NEW_BCF_NAME', 'BCFNUMBER', 
        'BTSNUMBER', 'ALARM_NUMBER', 'TEXT1', 'TOTALTIME', 'TEXT2', 
        'SUPPLEMENTARY_INFO', 'USER_ADDITIONAL_INFO', 'ACTUALALARMTIME', 
        'ACTUALCANCELTIME', 'CATEGORY', 'CITY', 'ID/OD', 'Accepted', 
        'GROUP_CATEGORY', 'CONSEC NO', 'TICKET ID', 'SEVERITY', 
        'REASON ID', 'Outage Reasons', 'Remarks', 'Raw', 'No_', 
        'Final', 'Sector'
    ]

    # Initialize the DataFrameManager
    manager = DataFrameManager(db_name="VIL_RFO", collection_name="Nov24", drop_columns=drop_data)

    # Export data and drop unwanted columns
    manager.export_data()
    manager.drop_unwanted_columns()

    # Get and display the resulting DataFrame
    final_df = manager.get_dataframe()
    manager.save_to_excel()  # Save the cleaned data to an Excel file
