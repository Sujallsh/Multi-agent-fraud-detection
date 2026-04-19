# AI Agent-Based Fraud Detection System

This project implements a robust fraud detection system using Python, pandas for data processing, and Microsoft AutoGen for cooperative multi-agent orchestration.

## Features

- **Data Ingestion Module**: Handles loading and preprocessing of multiple datasets including transactions, locations, users, SMS conversations, and email messages.
- **Data Cleaning**: Includes handling missing values, type conversions, and timestamp normalization.
- **Cooperative Multi-Agent Framework**: Three specialized agents work together to analyze transactions:
  - **Data Profiler Agent**: Retrieves and summarizes transaction, user, location, and communication data
  - **Fraud Detective Agent**: Evaluates data against evolving malicious patterns (temporal, geographic, behavioral)
  - **Adaptive Strategy Agent**: Reviews findings, maintains anomaly memory, and makes final decisions to minimize false positives

## Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY="your-api-key-here"
   ```

## Data Structure

Place your datasets in the `data/` directory:

- `Transactions.csv`: Transaction data with columns like ID, user_id, type, amount, location, payment method, timestamp, sender IBAN (optional)
- `Locations.csv` or `Locations.json`: Geo-referenced location data with location_id
- `Users.csv`: User demographic information with user_id
- `Conversations.csv`: SMS thread data with user_id, timestamp
- `Messages.csv`: Email message data with user_id, timestamp

## Usage

### Single Transaction Analysis
```python
from agent_framework import analyze_transaction

result = analyze_transaction("TXN_12345")
print(f"Decision: {result['decision']}, Confidence: {result['confidence']}")
```

### Batch Evaluation Pipeline
1. Prepare evaluation dataset: Create `data/evaluation_transactions.csv` with a `transaction_id` column (sample provided)
2. Run evaluation:
   ```python
   python evaluate.py
   ```
3. Results are exported to `fraud_results.txt` containing only fraudulent transaction IDs

### Execution Instructions
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set OpenAI API key:
   ```
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. Place data files in `data/` directory

4. For evaluation:
   - Create `data/evaluation_transactions.csv` with transaction IDs to analyze
   - Run `python evaluate.py`
   - Check `fraud_results.txt` for results

### Reproducibility
To generate requirements.txt with exact versions:
```python
python generate_requirements.py
```

## Agent Architecture

The system uses a GroupChat where agents communicate in sequence:

1. **Data Profiler** summarizes relevant data for the transaction
2. **Fraud Detective** analyzes for suspicious patterns
3. **Adaptive Strategy** reviews, considers historical anomalies, and makes final decision

The Adaptive Strategy Agent maintains memory of flagged anomalies to adapt detection strategies over time.

## Modules

- `data_ingestion.py`: Functions for loading and cleaning datasets
- `agent_framework.py`: Cooperative multi-agent system using AutoGen
  - **`build_transaction_context()`**: Core Data Profiler function that compiles comprehensive transaction dossiers
- `evaluate.py`: Batch evaluation pipeline for transaction analysis
- `generate_requirements.py`: Script to generate reproducible requirements.txt
- `main.py`: Example usage script
- `demo_profiler.py`: Demo script showing how to use `build_transaction_context()`

## Data Profiler Agent

The Data Profiler Agent builds comprehensive transaction context dossiers through the `build_transaction_context()` function. This function:

1. **Extracts transaction details** (Sender ID, Timestamp, Amount)
2. **Retrieves user demographics** from the Users dataset
3. **Establishes spending baseline** using the last 5 prior transactions
4. **Collects location data** within a 48-hour window (matching BioTag to User ID)
5. **Gathers communications** (SMS and emails) within 48-hour window
6. **Compiles a Context Dossier** formatted for Fraud Detective analysis

For detailed documentation, see [DATA_PROFILER_AGENT.md](DATA_PROFILER_AGENT.md)

### Quick Example
```python
from agent_framework import build_transaction_context, transactions_df, locations_df, users_df, conversations_df, messages_df

dossier = build_transaction_context(
    transaction_id="TXN_12345",
    df_transactions=transactions_df,
    df_locations=locations_df,
    df_users=users_df,
    df_sms=conversations_df,
    df_mails=messages_df
)

print(dossier)  # Formatted context ready for Fraud Detective analysis
```