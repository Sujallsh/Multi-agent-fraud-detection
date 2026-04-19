from agent_framework import (
    transactions_df,
    locations_df,
    users_df,
    conversations_df,
    messages_df,
    build_transaction_context,
)


def test_build_context():
    """Test the context building function."""
    if transactions_df.empty:
        print("No transactions loaded.")
        return

    # Test with first transaction
    first_row = transactions_df.iloc[0]
    transaction_id = first_row.get('ID') or first_row.get('transaction_id') or first_row.get('id')

    if not transaction_id:
        print("Could not determine transaction ID")
        return

    print(f"Testing context building for transaction: {transaction_id}")

    context = build_transaction_context(
        transaction_id,
        transactions_df,
        locations_df,
        users_df,
        conversations_df,
        messages_df,
    )

    print("Context built successfully!")
    print("First 500 characters of context:")
    print(context[:500])
    print("...")

    # Check if agents are initialized
    from agent_framework import fraud_detective, user_proxy
    print(f"Fraud detective initialized: {fraud_detective is not None}")
    print(f"User proxy initialized: {user_proxy is not None}")


if __name__ == "__main__":
    test_build_context()