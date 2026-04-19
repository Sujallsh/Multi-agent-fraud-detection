import pandas as pd
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_transactions(file_path):
    """
    Load and preprocess the Transactions.csv dataset.

    Parameters:
    file_path (str): Path to the Transactions.csv file.

    Returns:
    pd.DataFrame: Preprocessed transactions data.
    """
    try:
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Basic data cleaning
        # Handle missing values for optional fields
        optional_fields = ['Sender IBAN', 'Location']  # Assuming these are optional
        for field in optional_fields:
            if field in df.columns:
                df[field] = df[field].fillna('Unknown')  # Or appropriate default
        
        # Convert timestamps to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            # Drop rows with invalid timestamps if any
            df = df.dropna(subset=['timestamp'])
        
        # Additional cleaning: ensure amounts are numeric
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df = df.dropna(subset=['amount'])
        
        logging.info(f"Loaded {len(df)} transactions from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error loading transactions: {e}")
        return pd.DataFrame()

def load_locations(file_path):
    """
    Load and preprocess the geo-referenced Locations dataset.

    Parameters:
    file_path (str): Path to the locations file (CSV or JSON).

    Returns:
    pd.DataFrame: Preprocessed locations data.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format for locations")
        
        # Handle missing values
        df = df.fillna({'latitude': 0.0, 'longitude': 0.0, 'location_name': 'Unknown'})
        
        # Ensure lat/lon are numeric
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        logging.info(f"Loaded {len(df)} locations from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error loading locations: {e}")
        return pd.DataFrame()

def load_users(file_path):
    """
    Load and preprocess the Users demographic dataset.

    Parameters:
    file_path (str): Path to the users file (CSV or JSON).

    Returns:
    pd.DataFrame: Preprocessed users data.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format for users")
        
        # Handle missing values for optional demographic fields
        optional_demo_fields = ['age', 'gender', 'income']  # Assuming these might be optional
        for field in optional_demo_fields:
            if field in df.columns:
                if field in ['age', 'income']:
                    df[field] = pd.to_numeric(df[field], errors='coerce')
                    df[field] = df[field].fillna(df[field].median())  # Fill with median
                else:
                    df[field] = df[field].fillna('Unknown')
        
        logging.info(f"Loaded {len(df)} users from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error loading users: {e}")
        return pd.DataFrame()

def load_conversations(file_path):
    """
    Load and preprocess the Conversations SMS thread dataset.

    Parameters:
    file_path (str): Path to the conversations file (CSV or JSON).

    Returns:
    pd.DataFrame: Preprocessed conversations data.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format for conversations")
        
        # Handle missing values
        df = df.fillna({'sender': 'Unknown', 'message': '', 'thread_id': 'Unknown'})
        
        # Convert timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
        
        logging.info(f"Loaded {len(df)} conversations from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error loading conversations: {e}")
        return pd.DataFrame()

def load_messages(file_path):
    """
    Load and preprocess the Messages email dataset.

    Parameters:
    file_path (str): Path to the messages file (CSV or JSON).

    Returns:
    pd.DataFrame: Preprocessed messages data.
    """
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format for messages")
        
        # Handle missing values
        df = df.fillna({'sender': 'Unknown', 'recipient': 'Unknown', 'subject': '', 'body': ''})
        
        # Convert timestamps
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
        
        logging.info(f"Loaded {len(df)} messages from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error loading messages: {e}")
        return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    # Assuming file paths - replace with actual paths
    transactions = load_transactions('data/Transactions.csv')
    locations = load_locations('data/Locations.csv')
    users = load_users('data/Users.csv')
    conversations = load_conversations('data/Conversations.csv')
    messages = load_messages('data/Messages.csv')
    
    print("Data loaded successfully!")