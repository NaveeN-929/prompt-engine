"""
Banking and Financial Templates
"""

from app.templates.base import PromptTemplate

# Refined CRM Insights Analysis Template (Updated for RAG Pipeline)
crm_insights_refined = PromptTemplate(
    name="crm_insights_refined",
    context="crm_financial_insights",
    data_type="transaction_history",
    template="""
    Generate up to 5 pairs of insight and recommendation for an SME business, based on the latest transaction and account data.

    Transaction Data: {transaction_data}

    **ANALYSIS REQUIREMENTS:**
    - Insights must highlight patterns, behaviours, or emerging issues from transaction data
    - Insights should be slightly broader than basic metrics but remain data-driven and immediately useful to Relationship Managers
    - Recommendations must be clear, helpful, and 3 out of 5 should include a product/service suggestion from our banking catalog
    - Use natural, CRM-friendly language throughout — not technical jargon
    - Language should feel advisory, not salesy — like a helpful banker would say
    - Each pair must be fully self-contained and not reference other pairs

    **BANKING PRODUCT INTEGRATION:**
    EXACTLY 3 out of the 5 recommendations MUST include banking product suggestions.
    Mark these recommendations with (Upsell) or (Cross-sell) labels.

    When suggesting banking products, use these advisory phrases:
    - "You may benefit from..."
    - "Consider exploring..."
    - "Your situation suggests you might find value in..."
    - "Given your cash flow patterns, you could consider..."

    Available banking products for suggestions:
    - High-yield savings accounts and term deposits (Upsell)
    - Flexible overdraft facilities and invoice financing (Upsell)
    - Multi-currency business accounts (Cross-sell)
    - Revolving credit lines (Upsell)
    - Payroll and cash management services (Cross-sell)

    **OUTPUT FORMAT:**
    Return a JSON array with exactly 5 objects, each containing:
    {{
        "insight": "Short, clear observation from transactions or behavioural patterns",
        "recommendation": "Actionable next step, framed as a smart nudge"
    }}

    **EXAMPLES OF PAIRED OUTPUT:**
    [
        {{
            "insight": "You've had a positive cash flow for 3 consecutive weeks, with incoming payments consistently exceeding outgoing expenses",
            "recommendation": "Consider setting aside a portion of this surplus in a high-yield savings account or term deposit to build financial resilience"
        }},
        {{
            "insight": "Recurring supplier payments and payroll costs are now clustering near the same weekly cycle, creating temporary dips in available funds",
            "recommendation": "To smooth out cash flow, you might explore a flexible overdraft facility or invoice financing during peak outflow weeks"
        }},
        {{
            "insight": "We've detected that most of your larger incoming payments are delayed by 14–18 days after invoicing",
            "recommendation": "Introducing automated payment reminders could improve cash flow predictability — your RM can assist"
        }},
        {{
            "insight": "Your recent increase in marketing-related spend suggests growth ambitions or campaign activity",
            "recommendation": "Consider bundling your marketing budget with a revolving credit line to support scalable growth without cash strain (Upsell)"
        }},
        {{
            "insight": "You're processing more international transactions than usual — both incoming and outgoing",
            "recommendation": "A multi-currency business account could reduce your conversion costs and improve reconciliation (Cross-sell)"
        }}
    ]

    Generate insights and recommendations that are immediately actionable for Relationship Managers working with SME clients.
    """,
    parameters={
        "transaction_data": {"type": "json", "required": True}
    }
)

# Original CRM Insights Analysis Template (maintained for compatibility)
crm_insights_analysis = PromptTemplate(
    name="crm_insights_analysis",
    context="crm_financial_insights",
    data_type="transaction_history",
    template="""
    Based on customer transaction, card, and behavioral data across the provided time period, extract business insights followed by clear, proactive recommendations.

    Transaction Data: {transaction_data}

    **ANALYSIS REQUIREMENTS:**
    - Identify meaningful financial patterns and trends
    - Focus on actionable business intelligence
    - Generate insights relevant to business growth and optimization
    - Provide financial services recommendations where appropriate

    **OUTPUT FORMAT:**
    The format must follow exactly:

    === SECTION 1: INSIGHTS ===

    Insight 1: [Single-sentence observation, phrased in natural, friendly language].
    Insight 2: [Single-sentence observation, phrased in natural, friendly language].
    [Continue for all meaningful insights discovered]

    === SECTION 2: RECOMMENDATIONS ===

    Recommendation 1: [Single-sentence advisory or product/service suggestion, positioned as helpful, not salesy].
    Recommendation 2: [Single-sentence advisory or product/service suggestion, positioned as helpful, not salesy].
    [Continue for all relevant recommendations]

    **GUIDELINES:**
    - Each insight should be a complete, standalone observation
    - Each recommendation should be actionable and specific
    - Focus on business financial health and growth opportunities
    - Suitable for CRM integration (cards, dashboards, automations)
    - Only include insights relevant to business clients
    - Use natural, conversational language
    - Avoid technical jargon
    - Be proactive and helpful, not pushy

    **EXAMPLE INSIGHTS:**
    - "You received 12 international payments last week — a 60% increase from the week before."
    - "Your average monthly card spend on equipment has increased by 34% over the last 3 months."
    - "Payroll expenses have risen by 22% over the last quarter."

    **EXAMPLE RECOMMENDATIONS:**
    - "Consider enabling a multi-currency account to reduce FX fees and improve settlement times."
    - "We suggest exploring our flexible equipment financing options to preserve your cash flow."
    - "Explore our short-term credit facility to support your growth during expansion phases."
    """,
    parameters={
        "transaction_data": {"type": "json", "required": True}
    }
)

# Legacy Transaction Categorization Template (maintained for compatibility)
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
    
    **CRITICAL OUTPUT STRUCTURE REQUIREMENT:**
    
    Your response MUST be organized into exactly TWO main sections:
    
    === SECTION 1: INSIGHTS ===
    Provide all insights that can be derived from the input data and analysis:
    - Data patterns and trends identified
    - Key findings and observations
    - Statistical analysis results
    - Anomalies or unusual patterns detected
    - Business context implications
    - Risk factors identified
    - Opportunities discovered
    
    === SECTION 2: RECOMMENDATIONS ===
    Provide specific, actionable recommendations for SMEs to take necessary actions:
    - Immediate actions required
    - Strategic recommendations
    - Risk mitigation steps
    - Process improvements
    - Technology or tool recommendations
    - Training or skill development needs
    - Follow-up analysis requirements
    - Compliance or regulatory actions
    
    **FORMATTING RULES:**
    - Use clear section headers with === markers
    - Provide specific, actionable recommendations
    - Include confidence levels for insights
    - Prioritize recommendations by urgency/impact
    - Use bullet points for clarity
    - Quantify findings where possible
    - Include reasoning for each recommendation
    
    **EXAMPLE FORMAT:**
    === SECTION 1: INSIGHTS ===
    • [Insight 1 with supporting data]
    • [Insight 2 with supporting data]
    ...
    
    === SECTION 2: RECOMMENDATIONS ===
    • [Specific action item 1 with timeline]
    • [Specific action item 2 with timeline]
    ...
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
    
    **CRITICAL OUTPUT STRUCTURE REQUIREMENT:**
    
    Your response MUST be organized into exactly TWO main sections:
    
    === SECTION 1: INSIGHTS ===
    Provide all insights that can be derived from the input data and analysis:
    - Data patterns and trends identified
    - Key findings and observations
    - Statistical analysis results
    - Anomalies or unusual patterns detected
    - Business context implications
    - Risk factors identified
    - Opportunities discovered
    
    === SECTION 2: RECOMMENDATIONS ===
    Provide specific, actionable recommendations for SMEs to take necessary actions:
    - Immediate actions required
    - Strategic recommendations
    - Risk mitigation steps
    - Process improvements
    - Technology or tool recommendations
    - Training or skill development needs
    - Follow-up analysis requirements
    - Compliance or regulatory actions
    
    **FORMATTING RULES:**
    - Use clear section headers with === markers
    - Provide specific, actionable recommendations
    - Include confidence levels for insights
    - Prioritize recommendations by urgency/impact
    - Use bullet points for clarity
    - Quantify findings where possible
    - Include reasoning for each recommendation
    
    **EXAMPLE FORMAT:**
    === SECTION 1: INSIGHTS ===
    • [Insight 1 with supporting data]
    • [Insight 2 with supporting data]
    ...
    
    === SECTION 2: RECOMMENDATIONS ===
    • [Specific action item 1 with timeline]
    • [Specific action item 2 with timeline]
    ...
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
    
    **CRITICAL OUTPUT STRUCTURE REQUIREMENT:**
    
    Your response MUST be organized into exactly TWO main sections:
    
    === SECTION 1: INSIGHTS ===
    Provide all insights that can be derived from the input data and analysis:
    - Data patterns and trends identified
    - Key findings and observations
    - Statistical analysis results
    - Anomalies or unusual patterns detected
    - Business context implications
    - Risk factors identified
    - Opportunities discovered
    
    === SECTION 2: RECOMMENDATIONS ===
    Provide specific, actionable recommendations for SMEs to take necessary actions:
    - Immediate actions required
    - Strategic recommendations
    - Risk mitigation steps
    - Process improvements
    - Technology or tool recommendations
    - Training or skill development needs
    - Follow-up analysis requirements
    - Compliance or regulatory actions
    
    **FORMATTING RULES:**
    - Use clear section headers with === markers
    - Provide specific, actionable recommendations
    - Include confidence levels for insights
    - Prioritize recommendations by urgency/impact
    - Use bullet points for clarity
    - Quantify findings where possible
    - Include reasoning for each recommendation
    
    **EXAMPLE FORMAT:**
    === SECTION 1: INSIGHTS ===
    • [Insight 1 with supporting data]
    • [Insight 2 with supporting data]
    ...
    
    === SECTION 2: RECOMMENDATIONS ===
    • [Specific action item 1 with timeline]
    • [Specific action item 2 with timeline]
    ...
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
    
    **CRITICAL OUTPUT STRUCTURE REQUIREMENT:**
    
    Your response MUST be organized into exactly TWO main sections:
    
    === SECTION 1: INSIGHTS ===
    Provide all insights that can be derived from the input data and analysis:
    - Data patterns and trends identified
    - Key findings and observations
    - Statistical analysis results
    - Anomalies or unusual patterns detected
    - Business context implications
    - Risk factors identified
    - Opportunities discovered
    
    === SECTION 2: RECOMMENDATIONS ===
    Provide specific, actionable recommendations for SMEs to take necessary actions:
    - Immediate actions required
    - Strategic recommendations
    - Risk mitigation steps
    - Process improvements
    - Technology or tool recommendations
    - Training or skill development needs
    - Follow-up analysis requirements
    - Compliance or regulatory actions
    
    **FORMATTING RULES:**
    - Use clear section headers with === markers
    - Provide specific, actionable recommendations
    - Include confidence levels for insights
    - Prioritize recommendations by urgency/impact
    - Use bullet points for clarity
    - Quantify findings where possible
    - Include reasoning for each recommendation
    
    **EXAMPLE FORMAT:**
    === SECTION 1: INSIGHTS ===
    • [Insight 1 with supporting data]
    • [Insight 2 with supporting data]
    ...
    
    === SECTION 2: RECOMMENDATIONS ===
    • [Specific action item 1 with timeline]
    • [Specific action item 2 with timeline]
    ...
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
    
    **CRITICAL OUTPUT STRUCTURE REQUIREMENT:**
    
    Your response MUST be organized into exactly TWO main sections:
    
    === SECTION 1: INSIGHTS ===
    Provide all insights that can be derived from the input data and analysis:
    - Data patterns and trends identified
    - Key findings and observations
    - Statistical analysis results
    - Anomalies or unusual patterns detected
    - Business context implications
    - Risk factors identified
    - Opportunities discovered
    
    === SECTION 2: RECOMMENDATIONS ===
    Provide specific, actionable recommendations for SMEs to take necessary actions:
    - Immediate actions required
    - Strategic recommendations
    - Risk mitigation steps
    - Process improvements
    - Technology or tool recommendations
    - Training or skill development needs
    - Follow-up analysis requirements
    - Compliance or regulatory actions
    
    **FORMATTING RULES:**
    - Use clear section headers with === markers
    - Provide specific, actionable recommendations
    - Include confidence levels for insights
    - Prioritize recommendations by urgency/impact
    - Use bullet points for clarity
    - Quantify findings where possible
    - Include reasoning for each recommendation
    
    **EXAMPLE FORMAT:**
    === SECTION 1: INSIGHTS ===
    • [Insight 1 with supporting data]
    • [Insight 2 with supporting data]
    ...
    
    === SECTION 2: RECOMMENDATIONS ===
    • [Specific action item 1 with timeline]
    • [Specific action item 2 with timeline]
    ...
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
    
    **CRITICAL OUTPUT STRUCTURE REQUIREMENT:**
    
    Your response MUST be organized into exactly TWO main sections:
    
    === SECTION 1: INSIGHTS ===
    Provide all insights that can be derived from the input data and analysis:
    - Data patterns and trends identified
    - Key findings and observations
    - Statistical analysis results
    - Anomalies or unusual patterns detected
    - Business context implications
    - Risk factors identified
    - Opportunities discovered
    
    === SECTION 2: RECOMMENDATIONS ===
    Provide specific, actionable recommendations for SMEs to take necessary actions:
    - Immediate actions required
    - Strategic recommendations
    - Risk mitigation steps
    - Process improvements
    - Technology or tool recommendations
    - Training or skill development needs
    - Follow-up analysis requirements
    - Compliance or regulatory actions
    
    **FORMATTING RULES:**
    - Use clear section headers with === markers
    - Provide specific, actionable recommendations
    - Include confidence levels for insights
    - Prioritize recommendations by urgency/impact
    - Use bullet points for clarity
    - Quantify findings where possible
    - Include reasoning for each recommendation
    
    **EXAMPLE FORMAT:**
    === SECTION 1: INSIGHTS ===
    • [Insight 1 with supporting data]
    • [Insight 2 with supporting data]
    ...
    
    === SECTION 2: RECOMMENDATIONS ===
    • [Specific action item 1 with timeline]
    • [Specific action item 2 with timeline]
    ...
    """,
    parameters={
        "statements": {"type": "json", "required": True},
        "payment_history": {"type": "json", "required": True}
    }
) 