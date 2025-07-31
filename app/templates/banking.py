"""
Banking and Financial Templates
"""

from app.templates.base import PromptTemplate

# Transaction Categorization Template
transaction_categorization = PromptTemplate(
    name="transaction_categorization",
    context="core_banking",
    data_type="transaction_history",
    template="""
    Analyze the following business transaction data and categorize each transaction:
    
    {transaction_data}
    
    Categorize into:
    1. Revenue streams (identify all income sources)
    2. Operating expenses (breakdown by expense type)
    3. Debt obligations (loan payments, credit card payments)
    4. Irregular/suspicious transactions
    
    Output format:
    - For each transaction ID:
      * Category: 
      * Sub-category:
      * Confidence score (0-1):
      * Notes:
    """,
    parameters={
        "transaction_data": {"type": "json", "required": True}
    }
)

# Cash Flow Analysis Template
cash_flow_analysis = PromptTemplate(
    name="cash_flow_analysis",
    context="lending_decision",
    data_type="time_series_data",
    template="""
    Analyze cash flow patterns from this SME's transaction history:
    
    {time_series_data}
    
    Calculate:
    1. Average monthly cash flow
    2. Cash flow volatility (standard deviation)
    3. Seasonality patterns
    4. Working capital cycle length
    
    Identify:
    1. Cash flow positive/negative months
    2. Liquidity risk indicators
    3. Growth trends (YoY/MoM)
    
    Output format: JSON with calculations and risk flags
    """,
    parameters={
        "time_series_data": {"type": "json", "required": True},
        "time_window": {"type": "str", "required": False, "default": "90d"}
    }
)

# Creditworthiness Assessment Template
credit_assessment = PromptTemplate(
    name="credit_assessment",
    context="loan_approval",
    data_type="transaction_analysis",
    template="""
    Assess creditworthiness for SME loan application based on:
    - Transaction history analysis: {transaction_analysis}
    - Existing liabilities: {liability_data}
    - Industry benchmarks: {industry_data}
    
    Calculate:
    1. Debt Service Coverage Ratio (DSCR)
    2. Loan-to-Value (LTV) potential
    3. Probability of default (0-1 scale)
    
    Provide:
    1. Recommended credit limit
    2. Risk flags (list with severity)
    3. Key positive factors
    
    Output format: JSON with scores and explanations
    """,
    parameters={
        "transaction_analysis": {"type": "json", "required": True},
        "liability_data": {"type": "json", "required": False},
        "industry_data": {"type": "json", "required": False}
    }
)

# Customized Offer Generation Template
offer_generation = PromptTemplate(
    name="offer_generation",
    context="loan_offers",
    data_type="credit_assessment",
    template="""
    Generate customized loan offers for SME based on:
    - Credit assessment: {credit_assessment}
    - Bank product catalog: {product_catalog}
    - Customer preferences: {preferences}
    
    Create 3 offer variants:
    1. Conservative (low risk)
    2. Balanced (risk/reward)
    3. Growth-oriented (higher risk)
    
    For each variant include:
    - Loan amount
    - Interest rate range
    - Term length options
    - Special conditions
    - Upsell/cross-sell opportunities
    
    Format as markdown table with justification for each offer
    """,
    parameters={
        "credit_assessment": {"type": "json", "required": True},
        "product_catalog": {"type": "json", "required": True},
        "preferences": {"type": "json", "required": False}
    }
)

# Card Spend Analysis Template
card_spend_analysis = PromptTemplate(
    name="card_spend_analysis",
    context="card_data",
    data_type="card_transactions",
    template="""
    Analyze business card transactions:
    {card_transactions}
    
    Identify:
    1. Business vs personal spend ratio
    2. Recurring expenses breakdown
    3. High-risk merchant categories
    4. Spending patterns by:
       - Time of month
       - Merchant type
       - Transaction size
    
    Output: JSON with spend analytics and risk flags
    """,
    parameters={
        "card_transactions": {"type": "json", "required": True},
        "time_window": {"type": "str", "required": False, "default": "180d"}
    }
)

# Credit Utilization Assessment Template
credit_utilization = PromptTemplate(
    name="credit_utilization",
    context="risk_assessment",
    data_type="card_behavior",
    template="""
    Analyze credit card usage behavior:
    - Monthly statements: {statements}
    - Payment history: {payment_history}
    
    Calculate:
    1. Average credit utilization ratio
    2. Payment punctuality score
    3. Cash advance frequency
    4. Reward points efficiency
    
    Risk assessment:
    1. Over-utilization patterns
    2. Late payment trends
    3. Potential liquidity crunches
    
    Output format: JSON with scores and risk indicators
    """,
    parameters={
        "statements": {"type": "json", "required": True},
        "payment_history": {"type": "json", "required": True}
    }
) 