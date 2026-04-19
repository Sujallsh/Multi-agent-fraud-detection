import asyncio
from agent_framework import (
    transactions_df,
    locations_df,
    users_df,
    conversations_df,
    messages_df,
    evaluate_transaction,
)


async def demo_fraud_detective():
    if transactions_df.empty:
        print("No transactions loaded. Ensure data/Transactions.csv exists and is populated.")
        return

    first_row = transactions_df.iloc[0]
    transaction_id = first_row.get('ID') or first_row.get('transaction_id') or first_row.get('id')

    if not transaction_id:
        print("Could not determine the transaction ID from the first row.")
        return

    print(f"Evaluating transaction ID: {transaction_id}")
    result = await evaluate_transaction(
        transaction_id,
        transactions_df,
        locations_df,
        users_df,
        conversations_df,
        messages_df,
    )

    print("\n=== Fraud Detective Result ===")
    if isinstance(result, dict):
        for key, value in result.items():
            print(f"{key}: {value}\n")
    else:
        print(result)


if __name__ == "__main__":
    asyncio.run(demo_fraud_detective())


if __name__ == '__main__':
    demo_fraud_detective()
