import os
import pandas as pd
import json
import certifi
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBUploader:
    def __init__(self, db_name, collection_name, file_path):
        # Load environment variables
        load_dotenv()
        self.mongo_url = os.getenv('MONGO_DB_URL')
        
        # Validate MongoDB URL
        if not self.mongo_url:
            raise ValueError("MongoDB URL not found in environment variables.")
        
        # Validate file path
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        self.file_path = file_path

        # MongoDB configuration
        try:
            self.client = MongoClient(
                self.mongo_url,
                tls=True,
                tlsCAFile=certifi.where()
            )
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            self.client = None

        # Select the database and collection
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def excel_to_json(self):
        """Convert Excel file to JSON format"""
        try:
            df = pd.read_excel(self.file_path)
            json_data = df.to_dict(orient='records')  # Convert DataFrame to JSON
            logger.info("Excel data successfully converted to JSON.")
            return json_data
        except Exception as e:
            logger.error(f"Error converting Excel to JSON: {e}")
            return None

    def preprocess_data(self, data):
        """Replace invalid characters in keys for MongoDB compatibility."""
        return {k.replace('.', '_').replace('$', '_'): v for k, v in data.items()}

    def clear_collection(self):
        """Delete all documents in the collection"""
        try:
            self.collection.delete_many({})
            logger.info("All data cleared from the collection.")
        except Exception as e:
            logger.error(f"Error clearing collection: {e}")

    def upload_to_mongo(self, json_data):
        """Upload JSON data to MongoDB without checking for duplicates"""
        if json_data:
            try:
                # Process and insert all records at once
                processed_data = [self.preprocess_data(record) for record in json_data]
                self.collection.insert_many(processed_data)
                logger.info("All new data inserted into MongoDB.")
            except Exception as e:
                logger.error(f"Error inserting records: {e}")
        else:
            logger.warning("No data to upload to MongoDB.")

    def export_from_mongo(self):
        """Export data from MongoDB to a pandas DataFrame"""
        try:
            cursor = self.collection.find()
            df = pd.DataFrame(list(cursor))
            logger.info(f"Data successfully exported from MongoDB. Total documents: {df.shape[0]}")
            return df
        except Exception as e:
            logger.error(f"Error exporting data from MongoDB: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def save_to_excel(self, df, filename="PD_data.xlsx"):
        """Saves the DataFrame to an Excel file in the artifacts folder."""
        artifacts = "artifacts"
        os.makedirs(artifacts, exist_ok=True)
        output_path = os.path.join(artifacts, filename)
        df.to_excel(output_path, index=False)
        logger.info(f"Data saved to {output_path}")

    def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")


if __name__ == "__main__":
    # Initialize the uploader with database and collection names
    uploader = MongoDBUploader(db_name="VIL_RFO", collection_name="PD", file_path='artifacts\VIL PD Alarm - Final MTD.xlsx')

    # Convert Excel data to JSON
    json_data = uploader.excel_to_json()

    if json_data:
        # Clear existing data in the collection
        uploader.clear_collection()

        # Insert all new data to MongoDB
        uploader.upload_to_mongo(json_data)
    else:
        logger.warning("No data to upload. Conversion from Excel to JSON failed.")

    # Export data from MongoDB to a DataFrame and save it to an Excel file
    df = uploader.export_from_mongo()
    uploader.save_to_excel(df)

    # Close the MongoDB connection
    uploader.close_connection()