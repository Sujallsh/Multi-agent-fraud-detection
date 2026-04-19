from agent_framework import analyze_transaction

if __name__ == "__main__":
    # Example: Analyze a specific transaction
    transaction_id = "TXN_12345"  # Replace with actual transaction ID
    
    print(f"Analyzing transaction: {transaction_id}")
    result = analyze_transaction(transaction_id)
    
    print("Analysis Result:")
    print(f"Decision: {result['decision']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reason: {result['reason']}")