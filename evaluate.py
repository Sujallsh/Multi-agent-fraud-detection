import pandas as pd
import logging
from agent_framework import analyze_transaction

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_evaluation_dataset(file_path):
    """
    Load the evaluation dataset containing transaction IDs to analyze.

    Parameters:
    file_path (str): Path to the evaluation CSV file.

    Returns:
    pd.DataFrame: Evaluation dataset.
    """
    try:
        df = pd.read_csv(file_path)
        if 'transaction_id' not in df.columns:
            logging.error("Evaluation dataset must contain 'transaction_id' column")
            return pd.DataFrame()
        logging.info(f"Loaded {len(df)} transactions for evaluation from {file_path}")
        return df
    except Exception as e:
        logging.error(f"Error loading evaluation dataset: {e}")
        return pd.DataFrame()

def evaluate_fraud_detection(evaluation_file_path, output_file_path):
    """
    Evaluate fraud detection on a dataset of transactions.

    Parameters:
    evaluation_file_path (str): Path to evaluation dataset CSV.
    output_file_path (str): Path to output text file for fraudulent IDs.
    """
    # Load evaluation dataset
    eval_df = load_evaluation_dataset(evaluation_file_path)
    if eval_df.empty:
        logging.error("No evaluation data loaded. Exiting.")
        return

    fraudulent_ids = []

    # Analyze each transaction
    for idx, row in eval_df.iterrows():
        transaction_id = row['transaction_id']
        logging.info(f"Analyzing transaction {idx+1}/{len(eval_df)}: {transaction_id}")

        try:
            result = analyze_transaction(transaction_id)
            decision = result.get('decision', 'UNKNOWN')

            if decision == 'FRAUDULENT':
                fraudulent_ids.append(transaction_id)
                logging.info(f"Transaction {transaction_id} flagged as FRAUDULENT")
            else:
                logging.info(f"Transaction {transaction_id} classified as {decision}")

        except Exception as e:
            logging.error(f"Error analyzing transaction {transaction_id}: {e}")

    # Export results
    export_fraudulent_ids(fraudulent_ids, output_file_path)
    logging.info(f"Evaluation complete. {len(fraudulent_ids)} fraudulent transactions found.")

def export_fraudulent_ids(fraudulent_ids, output_file_path):
    """
    Export the list of fraudulent transaction IDs to a text file.

    Parameters:
    fraudulent_ids (list): List of fraudulent transaction IDs.
    output_file_path (str): Path to the output text file.
    """
    try:
        with open(output_file_path, 'w', encoding='ascii') as f:
            for transaction_id in fraudulent_ids:
                f.write(f"{transaction_id}\n")
        logging.info(f"Exported {len(fraudulent_ids)} fraudulent IDs to {output_file_path}")
    except Exception as e:
        logging.error(f"Error exporting results: {e}")

if __name__ == "__main__":
    # Configuration
    EVALUATION_FILE = 'data/evaluation_transactions.csv'  # CSV with 'transaction_id' column
    OUTPUT_FILE = 'fraud_results.txt'

    # Run evaluation
    evaluate_fraud_detection(EVALUATION_FILE, OUTPUT_FILE)