"""
Demo script showing how to use build_transaction_context function.
This demonstrates the Data Profiler Agent's core functionality.
"""

from agent_framework import (
    build_transaction_context, 
    transactions_df, 
    locations_df, 
    users_df, 
    conversations_df, 
    messages_df
)

def demo_build_transaction_context():
    """
    Demonstrate the build_transaction_context function with a sample transaction.
    """
    print("\n" + "="*80)
    print("DATA PROFILER AGENT - TRANSACTION CONTEXT BUILDER DEMO")
    print("="*80 + "\n")
    
    # Example transaction ID - replace with actual ID from your data
    transaction_id = "TXN_001"
    
    print(f"Building context dossier for transaction: {transaction_id}\n")
    
    # Build the context dossier
    context_dossier = build_transaction_context(
        transaction_id=transaction_id,
        df_transactions=transactions_df,
        df_locations=locations_df,
        df_users=users_df,
        df_sms=conversations_df,
        df_mails=messages_df
    )
    
    # Display the context dossier
    print(context_dossier)
    
    print("\n" + "="*80)
    print("This context dossier is now ready to be passed to the Fraud Detective Agent")
    print("="*80 + "\n")
    
    return context_dossier

if __name__ == "__main__":
    context = demo_build_transaction_context()