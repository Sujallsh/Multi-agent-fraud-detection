from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.models import ChatCompletionClient
import os
from dotenv import load_dotenv
from typing import Any, Dict, Optional

load_dotenv()

from data_ingestion import load_transactions, load_locations, load_users, load_conversations, load_messages
import pandas as pd

class GroupChat:
    def __init__(self, *args, **kwargs):
        self.messages = []

class GroupChatManager:
    def __init__(self, *args, **kwargs):
        pass

# Configure the LLM
llm_config = {
    "model": "meta-llama/llama-3-8b-instruct", # Using a cheap/free OpenRouter model for testing
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "base_url": "https://openrouter.ai/api/v1",
}


def create_openrouter_model_client(config: Dict[str, Any]) -> ChatCompletionClient:
    """Instantiate the OpenRouter chat completion client from llm_config."""
    if not config.get("api_key"):
        raise RuntimeError("Missing OPENROUTER_API_KEY in environment. Set it in .env.")

    try:
        from autogen_ext.models.openrouter import OpenRouterChatCompletionClient

        return OpenRouterChatCompletionClient(
            model=config["model"],
            api_key=config["api_key"],
            base_url=config["base_url"],
        )
    except ImportError:
        pass

    try:
        from autogen_ext.models.openai import OpenAIChatCompletionClient
        from autogen_core.models import ModelInfo

        return OpenAIChatCompletionClient(
            model=config["model"],
            api_key=config["api_key"],
            base_url=config["base_url"],
            model_info=ModelInfo(
                id=config["model"],
                family="llama",
                vision=False,
                function_calling=False,
                json_output=False,
                structured_output=False,
            ),
        )
    except Exception as exc:
        raise RuntimeError(
            "OpenRouter model client is unavailable. Install autogen_ext with OpenRouter support, and ensure the OpenAI-compatible client is available."
        ) from exc


class AutonomousUserProxyAgent(UserProxyAgent):
    def __init__(
        self,
        name: str,
        *,
        description: str = "A human user",
        input_func: Optional[Any] = None,
        max_consecutive_auto_reply: int = 1,
    ) -> None:
        self.max_consecutive_auto_reply = max_consecutive_auto_reply
        super().__init__(name=name, description=description, input_func=input_func or self._auto_reply)

    def _auto_reply(self, prompt: str, cancellation_token: Optional[CancellationToken] = None) -> str:
        return ""

    async def initiate_chat(self, assistant_agent: AssistantAgent, message: str):
        if assistant_agent is None:
            raise RuntimeError("Assistant agent is not initialized.")

        text_message = TextMessage(content=message, source="user")
        task_result = await assistant_agent.run(task=text_message, cancellation_token=CancellationToken())
        return task_result


def create_fraud_detective_agent() -> Optional[AssistantAgent]:
    try:
        model_client = create_openrouter_model_client(llm_config)
        return AssistantAgent(
            name="fraud_detective",
            model_client=model_client,
            system_message=(
                "You are a Senior Fraud Analyst for MirrorPay. You will receive a Context Dossier for a specific "
                "transaction. Analyze it step-by-step. Specifically look for Mirror Hacker tactics: targeting new merchants, "
                "shifting temporal habits, geographic inconsistencies, unusual amounts compared to the user's baseline, "
                "and deceptive behavioral sequences in the 48-hour SMS/email window. End your response with a final binary "
                "decision: either [FRAUD] or [LEGITIMATE]."
            ),
        )
    except Exception as exc:
        print(f"WARNING: Could not create fraud_detective agent: {exc}")
        return None


# Global agent instances
fraud_detective: Optional[AssistantAgent] = create_fraud_detective_agent()
user_proxy: AutonomousUserProxyAgent = AutonomousUserProxyAgent(
    "user_proxy",
    input_func=lambda prompt, cancellation_token=None: "",
    max_consecutive_auto_reply=1,
)

# Adaptive Memory for flagged anomalies
class AdaptiveMemory:
    def __init__(self):
        self.flagged_anomalies = []  # List of dicts with anomaly details

    def add_anomaly(self, transaction_id, reason, timestamp):
        self.flagged_anomalies.append({
            'transaction_id': transaction_id,
            'reason': reason,
            'timestamp': timestamp
        })

    def get_recent_anomalies(self, limit=10):
        return self.flagged_anomalies[-limit:]

    def get_patterns(self):
        # Simple pattern extraction: count reasons
        reasons = [a['reason'] for a in self.flagged_anomalies]
        return pd.Series(reasons).value_counts().to_dict()

# Global memory instance
adaptive_memory = AdaptiveMemory()

# Load datasets (assuming paths - in production, load once)
transactions_df = load_transactions('data/transactions.csv')
locations_df = load_locations('data/locations.json')
users_df = load_users('data/users.json')
conversations_df = load_conversations('data/sms.json')
messages_df = load_messages('data/mails.json')

# Placeholder agent variables for compatibility with other modules.
data_profiler = None

adaptive_strategy = None

groupchat = None

manager = None

def build_transaction_context(transaction_id, df_transactions, df_locations, df_users, df_sms, df_mails):
    """
    Build a comprehensive transaction context dossier for fraud analysis.

    This function extracts and compiles all relevant data for a given transaction,
    including user demographics, transaction history, location data, and communications
    within a 48-hour window.

    Parameters:
    -----------
    transaction_id : str
        The ID of the transaction to analyze.
    df_transactions : pd.DataFrame
        DataFrame containing transaction records with columns:
        ID, sender_id, timestamp, amount, type, location, payment_method, etc.
    df_locations : pd.DataFrame
        DataFrame containing geo-referenced locations with columns:
        location_id, BioTag, latitude, longitude, location_name, timestamp (optional)
    df_users : pd.DataFrame
        DataFrame containing user demographics with columns:
        user_id, name, age, gender, income, registration_date, etc.
    df_sms : pd.DataFrame
        DataFrame containing SMS data with columns:
        user_id, sender, message, timestamp
    df_mails : pd.DataFrame
        DataFrame containing email data with columns:
        user_id, sender, subject, body, timestamp

    Returns:
    --------
    str : A formatted Context Dossier string containing all relevant information
          for the Fraud Detective Agent to analyze.
    """
    
    try:
        # ===== STEP 1: Locate and extract the target transaction =====
        if df_transactions.empty:
            return "ERROR: Transaction database is empty."
        
        # Find transaction by ID (try multiple possible column names)
        transaction = None
        for id_col in ['ID', 'transaction_id', 'id']:
            if id_col in df_transactions.columns:
                trans_matches = df_transactions[df_transactions[id_col] == transaction_id]
                if not trans_matches.empty:
                    transaction = trans_matches.iloc[0]
                    break
        
        if transaction is None:
            return f"ERROR: Transaction {transaction_id} not found in database."
        
        # Extract key transaction details
        sender_id = transaction.get('sender_id') or transaction.get('user_id') or transaction.get('Sender ID')
        timestamp = transaction.get('timestamp')
        amount = transaction.get('amount') or transaction.get('Amount')
        trans_type = transaction.get('type') or transaction.get('Type') or 'Unknown'
        location = transaction.get('location') or transaction.get('Location') or 'Unknown'
        payment_method = transaction.get('payment_method') or transaction.get('Payment Method') or 'Unknown'
        
        if timestamp is None:
            return f"ERROR: Transaction {transaction_id} has no timestamp."
        
        # Ensure timestamp is datetime
        if not isinstance(timestamp, pd.Timestamp):
            timestamp = pd.to_datetime(timestamp)
        
        # ===== STEP 2: Look up user demographics =====
        user_dossier = "USER DEMOGRAPHICS: Not Found"
        if not df_users.empty and sender_id:
            for user_id_col in ['user_id', 'User ID', 'sender_id']:
                if user_id_col in df_users.columns:
                    user_matches = df_users[df_users[user_id_col] == sender_id]
                    if not user_matches.empty:
                        user = user_matches.iloc[0]
                        user_info = {
                            'User ID': sender_id,
                            'Name': user.get('name') or user.get('Name') or 'Unknown',
                            'Age': user.get('age') or user.get('Age') or 'Unknown',
                            'Gender': user.get('gender') or user.get('Gender') or 'Unknown',
                            'Income': user.get('income') or user.get('Income') or 'Unknown',
                            'Registration Date': user.get('registration_date') or user.get('Registration Date') or 'Unknown',
                        }
                        user_dossier = "USER DEMOGRAPHICS:\n"
                        for key, value in user_info.items():
                            user_dossier += f"  - {key}: {value}\n"
                        break
        
        # ===== STEP 3: Retrieve last 5 transactions before current timestamp =====
        spending_baseline = "SPENDING BASELINE (Last 5 Transactions): No prior transactions found"
        if not df_transactions.empty and sender_id:
            # Find all transactions by this user before the current timestamp
            for sender_col in ['sender_id', 'user_id', 'Sender ID']:
                if sender_col in df_transactions.columns:
                    prior_trans = df_transactions[
                        (df_transactions[sender_col] == sender_id) &
                        (df_transactions['timestamp'] < timestamp)
                    ].sort_values('timestamp', ascending=False).head(5)
                    
                    if not prior_trans.empty:
                        spending_baseline = "SPENDING BASELINE (Last 5 Transactions):\n"
                        for idx, trans in prior_trans.iterrows():
                            trans_amt = trans.get('amount') or trans.get('Amount') or 'Unknown'
                            trans_time = trans.get('timestamp') or 'Unknown'
                            trans_loc = trans.get('location') or trans.get('Location') or 'Unknown'
                            spending_baseline += f"  - {trans_time}: ${trans_amt} at {trans_loc}\n"
                    break
        
        # ===== STEP 4: Filter locations within 48-hour window matching BioTag =====
        location_context = "LOCATION DATA (48hr window): No location records found"
        if not df_locations.empty and sender_id:
            time_window_start = timestamp - pd.Timedelta(hours=48)
            time_window_end = timestamp + pd.Timedelta(hours=48)
            
            # Filter by BioTag (user ID equivalent in locations)
            for biotag_col in ['BioTag', 'biota', 'user_id']:
                if biotag_col in df_locations.columns:
                    # Also check if locations have timestamps
                    if 'timestamp' in df_locations.columns:
                        matching_locations = df_locations[
                            (df_locations[biotag_col] == sender_id) &
                            (df_locations['timestamp'] >= time_window_start) &
                            (df_locations['timestamp'] <= time_window_end)
                        ]
                    else:
                        # If no timestamp, just match by BioTag
                        matching_locations = df_locations[df_locations[biotag_col] == sender_id]
                    
                    if not matching_locations.empty:
                        location_context = "LOCATION DATA (48hr window):\n"
                        for idx, loc in matching_locations.iterrows():
                            loc_name = loc.get('location_name') or loc.get('Location Name') or 'Unknown'
                            lat = loc.get('latitude') or loc.get('Latitude') or 'N/A'
                            lon = loc.get('longitude') or loc.get('Longitude') or 'N/A'
                            loc_time = loc.get('timestamp') or 'Unknown'
                            location_context += f"  - {loc_time}: {loc_name} ({lat}, {lon})\n"
                    break
        
        # ===== STEP 5: Filter SMS within 48-hour window =====
        sms_context = "SMS COMMUNICATIONS (48hr window): No SMS records found"
        if not df_sms.empty and sender_id:
            time_window_start = timestamp - pd.Timedelta(hours=48)
            time_window_end = timestamp + pd.Timedelta(hours=48)
            
            for user_col in ['user_id', 'User ID', 'sender_id']:
                if user_col in df_sms.columns and 'timestamp' in df_sms.columns:
                    matching_sms = df_sms[
                        (df_sms[user_col] == sender_id) &
                        (df_sms['timestamp'] >= time_window_start) &
                        (df_sms['timestamp'] <= time_window_end)
                    ].sort_values('timestamp', ascending=False).head(10)
                    
                    if not matching_sms.empty:
                        sms_context = "SMS COMMUNICATIONS (48hr window - Last 10):\n"
                        for idx, sms in matching_sms.iterrows():
                            sms_time = sms.get('timestamp') or 'Unknown'
                            sms_sender = sms.get('sender') or 'Unknown'
                            sms_msg = sms.get('message') or sms.get('Message') or '[No message content]'
                            # Truncate long messages
                            if len(str(sms_msg)) > 100:
                                sms_msg = str(sms_msg)[:100] + "..."
                            sms_context += f"  - {sms_time} from {sms_sender}: {sms_msg}\n"
                    break
        
        # ===== STEP 6: Filter emails within 48-hour window =====
        email_context = "EMAIL COMMUNICATIONS (48hr window): No email records found"
        if not df_mails.empty and sender_id:
            time_window_start = timestamp - pd.Timedelta(hours=48)
            time_window_end = timestamp + pd.Timedelta(hours=48)
            
            for user_col in ['user_id', 'User ID', 'sender_id']:
                if user_col in df_mails.columns and 'timestamp' in df_mails.columns:
                    matching_emails = df_mails[
                        (df_mails[user_col] == sender_id) &
                        (df_mails['timestamp'] >= time_window_start) &
                        (df_mails['timestamp'] <= time_window_end)
                    ].sort_values('timestamp', ascending=False).head(10)
                    
                    if not matching_emails.empty:
                        email_context = "EMAIL COMMUNICATIONS (48hr window - Last 10):\n"
                        for idx, email in matching_emails.iterrows():
                            email_time = email.get('timestamp') or 'Unknown'
                            email_sender = email.get('sender') or 'Unknown'
                            email_subject = email.get('subject') or email.get('Subject') or '[No subject]'
                            email_context += f"  - {email_time} from {email_sender}: Subject: {email_subject}\n"
                    break
        
        # ===== COMPILE CONTEXT DOSSIER =====
        dossier = f"""
{'='*80}
TRANSACTION CONTEXT DOSSIER
{'='*80}

TARGET TRANSACTION:
  - Transaction ID: {transaction_id}
  - Sender ID: {sender_id}
  - Timestamp: {timestamp}
  - Amount: ${amount}
  - Type: {trans_type}
  - Location: {location}
  - Payment Method: {payment_method}

{user_dossier}

{spending_baseline}

{location_context}

{sms_context}

{email_context}

{'='*80}
"""
        
        return dossier
        
    except Exception as e:
        return f"ERROR building transaction context: {str(e)}"


async def evaluate_transaction(transaction_id, df_transactions, df_locations, df_users, df_sms, df_mails):
    """Evaluate a single transaction by sending the context dossier to the Fraud Detective Agent."""
    context_dossier = build_transaction_context(
        transaction_id,
        df_transactions,
        df_locations,
        df_users,
        df_sms,
        df_mails,
    )

    if context_dossier.startswith("ERROR"):
        return {
            "transaction_id": transaction_id,
            "error": context_dossier,
        }

    if fraud_detective is None:
        raise RuntimeError(
            "fraud_detective agent is not initialized. Ensure OpenRouter support is installed and configured."
        )

    response = await user_proxy.initiate_chat(fraud_detective, message=context_dossier)
    final_message = None
    for msg in reversed(response.messages):
        content = getattr(msg, "content", None)
        if content:
            final_message = content
            break

    return {
        "transaction_id": transaction_id,
        "context_dossier": context_dossier,
        "response": final_message if final_message is not None else str(response),
        "raw_task_result": response,
    }


def get_transaction_data(transaction_id):
    """
    Retrieve data for a specific transaction ID.
    """
    # Find transaction
    trans = transactions_df[transactions_df['ID'] == transaction_id]
    if trans.empty:
        return None
    
    trans = trans.iloc[0]
    user_id = trans.get('user_id', 'Unknown')  # Assuming there's a user_id column
    
    # Get user data
    user = users_df[users_df['user_id'] == user_id] if not users_df.empty else pd.DataFrame()
    user = user.iloc[0] if not user.empty else {}
    
    # Get location data
    location_id = trans.get('location', 'Unknown')
    location = locations_df[locations_df['location_id'] == location_id] if not locations_df.empty else pd.DataFrame()
    location = location.iloc[0] if not location.empty else {}
    
    # Get recent communications (last 24 hours)
    if not conversations_df.empty and 'timestamp' in conversations_df.columns:
        recent_convos = conversations_df[
            (conversations_df['user_id'] == user_id) &
            (conversations_df['timestamp'] >= trans['timestamp'] - pd.Timedelta(hours=24)) &
            (conversations_df['timestamp'] <= trans['timestamp'])
        ].tail(10)
    else:
        recent_convos = pd.DataFrame()
    
    if not messages_df.empty and 'timestamp' in messages_df.columns:
        recent_msgs = messages_df[
            (messages_df['user_id'] == user_id) &
            (messages_df['timestamp'] >= trans['timestamp'] - pd.Timedelta(hours=24)) &
            (messages_df['timestamp'] <= trans['timestamp'])
        ].tail(10)
    else:
        recent_msgs = pd.DataFrame()
    
    return {
        'transaction': trans.to_dict(),
        'user': user.to_dict() if user else {},
        'location': location.to_dict() if location else {},
        'recent_conversations': recent_convos.to_dict('records') if not recent_convos.empty else [],
        'recent_messages': recent_msgs.to_dict('records') if not recent_msgs.empty else []
    }

def analyze_transaction(transaction_id):
    """
    Analyze a specific transaction using the cooperative multi-agent system.

    Parameters:
    transaction_id (str): The ID of the transaction to analyze.

    Returns:
    dict: Analysis result with decision and confidence.
    """
    data = get_transaction_data(transaction_id)
    if not data:
        return {"decision": "UNKNOWN", "confidence": "High", "reason": "Transaction not found"}
    
    # Create data summary for agents
    data_summary = f"""
Transaction Details: {data['transaction']}
User Demographics: {data['user']}
Location Info: {data['location']}
Recent SMS (last 10): {data['recent_conversations']}
Recent Emails (last 10): {data['recent_messages']}
Historical Anomalies: {adaptive_memory.get_recent_anomalies()}
    """
    
    # Initiate group chat
    user_proxy.initiate_chat(
        manager,
        message=f"Analyze transaction ID {transaction_id} for fraud. Here is the relevant data: {data_summary}"
    )
    
    # Extract final decision from chat messages
    messages = groupchat.messages
    final_decision = {"decision": "UNKNOWN", "confidence": "Low", "reason": "Unable to parse decision"}
    
    # Find the last message from Adaptive_Strategy
    for msg in reversed(messages):
        if msg.get('name') == 'Adaptive_Strategy':
            content = msg.get('content', '')
            if 'FINAL DECISION:' in content:
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('FINAL DECISION:'):
                        decision = line.split(':')[1].strip()
                        final_decision['decision'] = decision
                    elif line.startswith('CONFIDENCE:'):
                        confidence = line.split(':')[1].strip()
                        final_decision['confidence'] = confidence
                    elif line.startswith('REASON:'):
                        reason = line.split(':')[1].strip()
                        final_decision['reason'] = reason
                break
    
    # If fraudulent, add to memory
    if final_decision['decision'] == 'FRAUDULENT':
        adaptive_memory.add_anomaly(transaction_id, final_decision['reason'], data['transaction'].get('timestamp'))
    
    return final_decision

# Example usage
if __name__ == "__main__":
    # Example transaction ID - replace with actual
    result = analyze_transaction("TXN_12345")
    print(f"Analysis Result: {result}")