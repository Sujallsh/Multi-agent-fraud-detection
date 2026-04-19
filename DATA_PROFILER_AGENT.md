# Data Profiler Agent - Core Implementation

## Overview

The **Data Profiler Agent** is responsible for building comprehensive transaction context dossiers that provide the Fraud Detective Agent with all necessary information to analyze a transaction for potential fraud.

## Core Function: `build_transaction_context()`

### Function Signature
```python
def build_transaction_context(
    transaction_id,           # str: ID of the transaction to analyze
    df_transactions,          # pd.DataFrame: Transaction records
    df_locations,             # pd.DataFrame: Geo-referenced locations
    df_users,                 # pd.DataFrame: User demographics
    df_sms,                   # pd.DataFrame: SMS communications
    df_mails                  # pd.DataFrame: Email communications
) -> str:
```

### Functionality

The function performs the following steps in sequence:

#### 1. **Transaction Lookup**
- Locates the specified transaction in `df_transactions` by ID
- Extracts critical fields:
  - Sender ID (user identifier)
  - Timestamp (transaction time)
  - Amount (transaction value)
  - Type, Location, Payment Method

#### 2. **User Demographics Retrieval**
- Looks up the sender/user in `df_users` using the extracted Sender ID
- Compiles demographic information:
  - Name, Age, Gender
  - Income level
  - Account registration date
  - Other available user attributes

#### 3. **Spending Baseline Establishment**
- Retrieves the last 5 transactions from the same user **before** the current transaction
- Provides historical context for:
  - Typical spending amounts
  - Transaction frequency patterns
  - Known locations where user transacts
  - Comparison baseline for amount anomalies

#### 4. **Location Data (48-hour Window)**
- Filters `df_locations` for entries matching user's BioTag
- Extracts all location activity within **48 hours** before and after transaction:
  - Geo-coordinates (latitude, longitude)
  - Location names
  - Timestamps of location events
  - Enables detection of geographic inconsistencies

#### 5. **SMS Communications (48-hour Window)**
- Retrieves SMS records from `df_sms` within 48-hour window
- Captures last 10 SMS messages with:
  - Timestamp and sender
  - Message content (truncated if long)
  - Enables detection of communication-transaction correlations

#### 6. **Email Communications (48-hour Window)**
- Retrieves email records from `df_mails` within 48-hour window
- Captures last 10 emails with:
  - Timestamp, sender, and subject
  - Enables detection of suspicious email-initiated transactions

### Output Format

The function returns a **Context Dossier** - a well-formatted string containing:

```
================================================================================
TRANSACTION CONTEXT DOSSIER
================================================================================

TARGET TRANSACTION:
  - Transaction ID: TXN_12345
  - Sender ID: USER_789
  - Timestamp: 2026-04-16 14:32:00
  - Amount: $1,250.00
  - Type: Wire Transfer
  - Location: New York, NY
  - Payment Method: Bank Account

USER DEMOGRAPHICS:
  - User ID: USER_789
  - Name: John Doe
  - Age: 45
  - Gender: Male
  - Income: $85,000
  - Registration Date: 2020-01-15

SPENDING BASELINE (Last 5 Transactions):
  - 2026-04-15 09:15:00: $89.50 at San Francisco, CA
  - 2026-04-14 16:45:00: $234.00 at San Francisco, CA
  - 2026-04-12 11:20:00: $45.99 at Los Angeles, CA
  - 2026-04-10 13:00:00: $150.00 at New York, NY
  - 2026-04-08 10:30:00: $67.25 at Boston, MA

LOCATION DATA (48hr window):
  - 2026-04-15 22:45:00: San Francisco Office (37.7749, -122.4194)
  - 2026-04-16 08:30:00: San Francisco Airport (37.6213, -122.3790)

SMS COMMUNICATIONS (48hr window - Last 10):
  - 2026-04-15 20:00:00 from +1-555-0100: Reminder about tomorrow's meeting at 2pm
  - 2026-04-16 07:15:00 from +1-555-0101: Flight confirmation - Departure 10:30am

EMAIL COMMUNICATIONS (48hr window - Last 10):
  - 2026-04-15 19:30:00 from boss@company.com: Subject: Urgent - Q2 Budget Review
  - 2026-04-16 06:45:00 from travel@airline.com: Subject: Check-in reminder

================================================================================
```

### Data Validation

The function implements robust error handling:
- **Missing transaction**: Returns clear error if transaction ID not found
- **Empty dataframes**: Gracefully handles missing data sources with informative messages
- **Column name flexibility**: Tries multiple common column name variations (e.g., 'ID', 'transaction_id', 'sender_id', 'user_id')
- **Timestamp handling**: Converts timestamps to datetime objects automatically
- **Exception safety**: Catches and reports any errors during processing

### Expected DataFrame Columns

#### df_transactions
- Required: `ID` (or `transaction_id`), `timestamp`, `sender_id` (or `user_id`), `amount`
- Optional: `type`, `location`, `payment_method`

#### df_users
- Required: `user_id` (or matching sender_id column)
- Optional: `name`, `age`, `gender`, `income`, `registration_date`

#### df_locations
- Required: `BioTag` (or matching user_id), `location_name`, `latitude`, `longitude`
- Optional: `timestamp`

#### df_sms
- Required: `user_id`, `timestamp`, `sender`, `message`

#### df_mails
- Required: `user_id`, `timestamp`, `sender`, `subject`
- Optional: `body`

### Usage Example

```python
from agent_framework import build_transaction_context
from data_ingestion import load_transactions, load_locations, load_users, load_conversations, load_messages

# Load all datasets
trans_df = load_transactions('data/Transactions.csv')
loc_df = load_locations('data/Locations.csv')
usr_df = load_users('data/Users.csv')
sms_df = load_conversations('data/Conversations.csv')
mail_df = load_messages('data/Messages.csv')

# Build context for a specific transaction
dossier = build_transaction_context(
    transaction_id="TXN_12345",
    df_transactions=trans_df,
    df_locations=loc_df,
    df_users=usr_df,
    df_sms=sms_df,
    df_mails=mail_df
)

# Pass to Fraud Detective Agent
print(dossier)
```

## Integration with Multi-Agent System

The context dossier produced by `build_transaction_context()` is designed to be passed directly to the **Fraud Detective Agent** for analysis. The Fraud Detective then evaluates this comprehensive context against evolving malicious patterns.

### Pattern Detection Pipeline
1. **Data Profiler** → `build_transaction_context()` → Context Dossier
2. **Fraud Detective** → Analyzes dossier for:
   - Temporal anomalies (unusual transaction time vs. baseline)
   - Geographic inconsistencies (transaction location vs. recent locations)
   - Amount anomalies (transaction amount vs. spending baseline)
   - Communication correlations (email/SMS activity around transaction)
3. **Adaptive Strategy** → Reviews detective's findings + historical patterns → Final decision

## Performance Considerations

- **Memory**: Efficient filtering using pandas optimizations
- **Time Complexity**: O(n) for each dataframe filter where n is dataframe size
- **48-hour Window**: Balances between comprehensive context and computational efficiency
- **Last 5 Transactions**: Provides adequate baseline without excessive lookups

## Future Enhancements

- Parallel loading of dataframe sections for large datasets
- Caching of frequently accessed user profiles
- Incremental timestamp indexing for faster temporal queries
- Geographic clustering to detect location anomalies more precisely