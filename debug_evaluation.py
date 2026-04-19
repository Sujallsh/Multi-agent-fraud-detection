import asyncio
from agent_framework import (
    transactions_df,
    locations_df,
    users_df,
    conversations_df,
    messages_df,
    build_transaction_context,
    fraud_detective,
    user_proxy,
)


async def evaluate_single_transaction_debug(transaction_id):
    """Evaluate a single transaction synchronously with debug output."""
    context_dossier = build_transaction_context(
        transaction_id,
        transactions_df,
        locations_df,
        users_df,
        conversations_df,
        messages_df,
    )

    if context_dossier.startswith("ERROR"):
        print(f"ERROR for {transaction_id}: {context_dossier}")
        return {"transaction_id": transaction_id, "error": context_dossier}

    if fraud_detective is None:
        raise RuntimeError("fraud_detective agent is not initialized.")

    print(f"Calling LLM for {transaction_id}...")
    response = await user_proxy.initiate_chat(fraud_detective, message=context_dossier)
    print(f"Got response for {transaction_id}")

    final_message = None
    for msg in reversed(response.messages):
        content = getattr(msg, "content", None)
        if content:
            final_message = content
            break

    result = {
        "transaction_id": transaction_id,
        "context_dossier": context_dossier,
        "response": final_message if final_message is not None else str(response),
    }

    print(f"Result keys: {result.keys()}")
    print(f"Response preview: {str(result.get('response', ''))[:100]}...")

    return result


async def debug_evaluation():
    """Debug evaluation on first 2 transactions."""
    if transactions_df.empty:
        print("No transactions loaded.")
        return

    fraudulent_transaction_ids = []

    # Test first 2 transactions
    for i in range(min(2, len(transactions_df))):
        row = transactions_df.iloc[i]
        transaction_id = row.get('ID') or row.get('transaction_id') or row.get('id')

        if not transaction_id:
            print(f"Warning: Could not determine transaction ID for row {i}")
            continue

        print(f"\nProcessing {i+1}/2: {transaction_id}")

        result = await evaluate_single_transaction_debug(transaction_id)

        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Has 'response' key: {'response' in result}")
            if 'response' in result:
                response_text = str(result['response']).upper()
                print(f"Checking for [FRAUD] in: {response_text[:200]}...")
                if '[FRAUD]' in response_text:
                    fraudulent_transaction_ids.append(transaction_id)
                    print(f"  -> FLAGGED AS FRAUD: {transaction_id}")
                else:
                    print(f"  -> LEGITIMATE: {transaction_id}")
        else:
            print(f"Result is not a dict: {result}")

    print(f"\nFraudulent IDs: {fraudulent_transaction_ids}")

    # Write results to submission.txt
    with open('submission_debug.txt', 'w') as f:
        for transaction_id in fraudulent_transaction_ids:
            f.write(f"{transaction_id}\n")

    print("Results written to submission_debug.txt")


if __name__ == "__main__":
    asyncio.run(debug_evaluation())