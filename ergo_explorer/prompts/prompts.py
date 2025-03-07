"""
MCP prompts for the Ergo blockchain explorer.
"""


def check_balance_prompt(address: str) -> str:
    """Prompt for checking an Ergo address balance."""
    return f"""Please check the current balance of Ergo blockchain address {address}.
Provide the ERG amount and any tokens held by this address in a clear, readable format."""


def analyze_transaction_prompt(tx_id: str) -> str:
    """Prompt for analyzing an Ergo transaction."""
    return f"""Please analyze Ergo blockchain transaction {tx_id} in detail.
I'd like to understand:
1. The basic transaction details (block, height, timestamp, size)
2. The inputs and their addresses
3. The outputs and their addresses
4. The transaction fee
5. Any token transfers that occurred

Please present this information in a structured format and provide any insights
you can derive from this transaction data."""


def forensic_analysis_prompt(address: str, depth: int = 2, tx_limit: int = 5) -> str:
    """Prompt for performing forensic analysis on an Ergo address."""
    return f"""Please perform a thorough forensic analysis on Ergo address {address}.
Analyze transaction flows up to {depth} levels deep, following at most {tx_limit} transactions per address.

In your analysis:
1. Start with the current balance and recent transactions
2. Identify related addresses at each level
3. Look for patterns in transaction flows
4. Identify any unusual transaction patterns
5. Note any high-value transfers or token movements

Present the results in a clear, structured format that emphasizes the most significant findings.""" 