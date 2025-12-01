#!/usr/bin/env python3
"""
Business Banking Transaction Data Generator
Generates realistic business banking transaction datasets for testing the self-learning system
Designed for SME (Small & Medium Enterprise) business accounts
"""

import argparse
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os


QUALITY_FOCUS_PRESETS = {
    "balanced": {
        "label": "Balanced realism",
        "description": "Reflects a realistic SME portfolio with a steady mix of revenues and expenses.",
        "transaction_scale": 1.0,
        "bonus_transactions": 0,
        "cross_border_chance": 0.65,
        "card_spend_chance": 0.35,
        "high_value_chance": 0.25,
        "recurring_chance": 0.15,
        "ensure_cross_border_count": 1,
        "ensure_high_value_count": 1,
        "ensure_card_spend_count": 2,
        "min_cross_border_notes": 1,
        "min_high_value_notes": 1,
        "min_card_spend_notes": 1,
        "insight_depth": 2
    },
    "actionable": {
        "label": "Actionable focus",
        "description": "Surfaces high-impact, implementable behaviours (cross-border payables, large invoices, card spend).",
        "transaction_scale": 1.3,
        "bonus_transactions": 3,
        "cross_border_chance": 0.85,
        "card_spend_chance": 0.55,
        "high_value_chance": 0.65,
        "recurring_chance": 0.4,
        "ensure_cross_border_count": 3,
        "ensure_high_value_count": 2,
        "ensure_card_spend_count": 3,
        "min_cross_border_notes": 2,
        "min_high_value_notes": 2,
        "min_card_spend_notes": 2,
        "insight_depth": 3
    },
    "comprehensive": {
        "label": "Comprehensive coverage",
        "description": "Maximizes category coverage so validation sees completeness and structural compliance.",
        "transaction_scale": 1.5,
        "bonus_transactions": 4,
        "cross_border_chance": 0.7,
        "card_spend_chance": 0.45,
        "high_value_chance": 0.7,
        "recurring_chance": 0.3,
        "ensure_cross_border_count": 2,
        "ensure_high_value_count": 2,
        "ensure_card_spend_count": 2,
        "min_cross_border_notes": 2,
        "min_high_value_notes": 2,
        "min_card_spend_notes": 2,
        "insight_depth": 4
    }
}


class TransactionDataGenerator:
    """Generate realistic business banking transaction data for SMEs"""
    
    def __init__(self):
        # Business names for realistic data
        self.business_names = [
            'Tech Solutions Inc', 'Global Logistics Ltd', 'Green Energy Co',
            'Precision Manufacturing', 'Digital Marketing Agency', 'Wholesale Distributors Inc',
            'Professional Services Group', 'Retail Solutions LLC', 'Healthcare Services Inc',
            'Construction Partners Ltd', 'Food & Beverage Co', 'Transportation Services',
            'Consulting Group International', 'Engineering Solutions', 'Import Export Trading',
            'Software Development Corp', 'Real Estate Holdings', 'Financial Services Inc',
            'Education Services Ltd', 'Hospitality Management Co'
        ]
        
        # Real company names for PAM scraping (vendors, customers, partners)
        self.real_tech_companies = [
            'Microsoft Corporation', 'Amazon Web Services Inc', 'Google LLC', 
            'Apple Inc', 'Salesforce Inc', 'Adobe Inc', 'Oracle Corporation',
            'IBM Corporation', 'SAP America Inc', 'Cisco Systems Inc',
            'Intel Corporation', 'Dell Technologies Inc', 'HP Inc',
            'VMware Inc', 'Zoom Video Communications Inc', 'Slack Technologies LLC',
            'Atlassian Corporation', 'HubSpot Inc', 'Shopify Inc'
        ]
        
        self.real_service_companies = [
            'Deloitte LLP', 'PwC US', 'KPMG LLP', 'Ernst & Young LLP',
            'Accenture PLC', 'McKinsey & Company', 'Boston Consulting Group',
            'Bain & Company', 'FedEx Corporation', 'UPS Inc',
            'WeWork Companies Inc', 'Regus Business Centers'
        ]
        
        self.real_financial_companies = [
            'PayPal Holdings Inc', 'Stripe Inc', 'Square Inc',
            'American Express Company', 'Visa Inc', 'Mastercard Inc',
            'JPMorgan Chase & Co', 'Bank of America Corp', 'Wells Fargo & Company'
        ]
        
        self.real_media_companies = [
            'LinkedIn Corporation', 'Meta Platforms Inc', 'Twitter Inc',
            'The New York Times Company', 'Bloomberg LP', 'Reuters'
        ]
        
        # All real companies combined
        self.all_real_companies = (
            self.real_tech_companies + 
            self.real_service_companies + 
            self.real_financial_companies + 
            self.real_media_companies
        )
        
        # Business email domains
        self.email_domains = [
            'business.com', 'company.net', 'corp.com', 'enterprises.com',
            'solutions.com', 'services.net', 'group.com', 'industries.com'
        ]
        
        # Bank names for account info
        self.bank_names = [
            'First National Bank', 'Commerce Bank', 'Business Banking Corp',
            'Enterprise Bank', 'Merchant Bank', 'Trade Finance Bank',
            'SME Banking Solutions', 'Corporate Bank'
        ]
        
        # Business banking transaction categories and their typical ranges
        self.transaction_types = {
            'credit': {
                # Revenue streams
                'customer_payment': {'min': 5000, 'max': 50000, 'frequency': 'frequent'},
                'sales_revenue': {'min': 10000, 'max': 100000, 'frequency': 'frequent'},
                'contract_payment': {'min': 20000, 'max': 200000, 'frequency': 'monthly'},
                'service_revenue': {'min': 8000, 'max': 80000, 'frequency': 'frequent'},
                'subscription_revenue': {'min': 3000, 'max': 30000, 'frequency': 'monthly'},
                'invoice_payment': {'min': 5000, 'max': 75000, 'frequency': 'frequent'},
                'interest_income': {'min': 500, 'max': 5000, 'frequency': 'monthly'},
                'loan_proceeds': {'min': 50000, 'max': 500000, 'frequency': 'rare'},
                'investment_income': {'min': 10000, 'max': 100000, 'frequency': 'quarterly'},
                'grant_funding': {'min': 25000, 'max': 250000, 'frequency': 'rare'},
            },
            'debit': {
                # Business expenses
                'payroll': {'min': 30000, 'max': 300000, 'frequency': 'monthly'},
                'vendor_payment': {'min': 5000, 'max': 100000, 'frequency': 'frequent'},
                'rent_lease': {'min': 5000, 'max': 50000, 'frequency': 'monthly'},
                'utilities': {'min': 1000, 'max': 10000, 'frequency': 'monthly'},
                'supplies': {'min': 2000, 'max': 25000, 'frequency': 'frequent'},
                'equipment_purchase': {'min': 10000, 'max': 150000, 'frequency': 'random'},
                'marketing': {'min': 5000, 'max': 50000, 'frequency': 'monthly'},
                'insurance': {'min': 3000, 'max': 30000, 'frequency': 'monthly'},
                'legal_fees': {'min': 5000, 'max': 50000, 'frequency': 'random'},
                'accounting_fees': {'min': 2000, 'max': 20000, 'frequency': 'monthly'},
                'software_subscription': {'min': 1000, 'max': 10000, 'frequency': 'monthly'},
                'tax_payment': {'min': 10000, 'max': 100000, 'frequency': 'quarterly'},
                'loan_payment': {'min': 5000, 'max': 75000, 'frequency': 'monthly'},
                'maintenance': {'min': 2000, 'max': 20000, 'frequency': 'random'},
                'travel_expense': {'min': 3000, 'max': 30000, 'frequency': 'random'},
                'shipping_logistics': {'min': 4000, 'max': 40000, 'frequency': 'frequent'},
                'consulting_fees': {'min': 8000, 'max': 80000, 'frequency': 'random'},
                'training': {'min': 2000, 'max': 20000, 'frequency': 'random'},
            }
        }
        
        # Categories that are likely to include cross-border flows
        self.cross_border_categories = {
            'contract_payment',
            'shipping_logistics',
            'international_payments',
            'subscription_revenue',
            'service_revenue'
        }

        # Products that customers typically own
        self.product_catalog = [
            'salary_account',
            'corporate_card',
            'business_loan',
            'trade_finance',
            'cash_management',
            'foreign_currency_account'
        ]

        self.segment_types = ['retail', 'SME', 'wealth']
        self.channel_preferences = ['digital', 'branch', 'relationship_manager']
        self.life_stages = ['growth', 'scaling', 'mature', 'expansion']
        self.currency_preferences = ['SGD', 'USD', 'EUR', 'GBP', 'AED']
        
        # Business customer ID prefixes
        self.customer_prefixes = ['BIZ', 'SME', 'ENT', 'CORP', 'CO']

        # Focus presets control signal density for validation
        self.quality_focus_presets = QUALITY_FOCUS_PRESETS
        
    def generate_customer_id(self, index: int) -> str:
        """Generate a unique customer ID"""
        prefix = random.choice(self.customer_prefixes)
        return f"{prefix}_{index:04d}"
    
    def generate_business_name(self, index: int) -> str:
        """Generate a realistic business name"""
        if index <= len(self.business_names):
            return self.business_names[index - 1]
        else:
            # Generate variations for more datasets
            base_name = random.choice(self.business_names)
            suffix = random.choice(['Group', 'International', 'LLC', 'Inc', 'Corp', 'Ltd'])
            return f"{base_name} {suffix}"
    
    def generate_business_email(self, business_name: str, customer_id: str) -> str:
        """Generate a business email address"""
        # Clean business name for email
        name_part = business_name.lower().replace(' ', '').replace('&', 'and')[:15]
        domain = random.choice(self.email_domains)
        
        # Use different email formats
        formats = [
            f"info@{name_part}.{domain}",
            f"contact@{name_part}.{domain}",
            f"accounts@{name_part}.{domain}",
            f"finance@{name_part}.{domain}",
        ]
        return random.choice(formats)
    
    def generate_phone_number(self) -> str:
        """Generate a business phone number"""
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        return f"{area_code}-{exchange}-{number}"
    
    def generate_account_info(self, customer_id: str) -> dict:
        """Generate business account information"""
        # Generate account number
        account_number = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        # Generate routing number (9 digits)
        routing_number = f"{random.randint(100000000, 999999999):09d}"
        
        # Select bank
        bank_name = random.choice(self.bank_names)
        
        # Account types for businesses
        account_type = random.choice(['business_checking', 'business_savings', 'commercial_account'])
        
        return {
            "account_number": account_number,
            "routing_number": routing_number,
            "bank_name": bank_name,
            "account_type": account_type
        }
    
    def generate_transaction(self, transaction_type: str, category: str, 
                           base_date: datetime) -> Dict[str, Any]:
        """Generate a single transaction with company names for PAM scraping"""
        
        config = self.transaction_types[transaction_type][category]
        
        # Generate amount
        amount = round(random.uniform(config['min'], config['max']), 2)
        if transaction_type == 'debit':
            amount = -abs(amount)
        
        # Generate date offset (within a reasonable range)
        days_offset = random.randint(0, 30)
        transaction_date = base_date + timedelta(days=days_offset)
        
        # Format description with company names
        description, merchant = self._format_description(category, amount)
        
        transaction = {
            'date': transaction_date.strftime('%Y-%m-%d'),
            'amount': amount,
            'type': transaction_type,
            'description': description,
            'tags': self._build_transaction_tags(category, transaction_type, amount)
        }
        
        # Add merchant/company field if available (for PAM to extract)
        if merchant:
            transaction['merchant'] = merchant
        
        return transaction

    def _compute_contextual_signals(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize behavioural signals used by PAM contexts"""
        total_amount = sum(abs(tx['amount']) for tx in transactions)
        cross_border = sum(1 for tx in transactions if 'cross_border' in tx.get('tags', []))
        card_spend = sum(1 for tx in transactions if 'card_spend' in tx.get('tags', []))
        high_value_spend = sum(
            1 for tx in transactions
            if tx.get('type') == 'debit' and abs(tx['amount']) >= 40000
        )

        avg_tx_value = round(total_amount / len(transactions), 2) if transactions else 0

        return {
            "recent_transaction_count": len(transactions),
            "cross_border_transfers": cross_border,
            "card_spend_count": card_spend,
            "high_value_spend": high_value_spend,
            "avg_transaction_value": avg_tx_value,
            "signals_timestamp": datetime.utcnow().isoformat()
        }

    def generate_customer_profile(self, account_balance: float, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Create an enriched customer profile for PAM eligibility checks"""
        fx_factor = min(1.0, signals.get("cross_border_transfers", 0) / 6)
        card_factor = min(1.0, signals.get("card_spend_count", 0) / 8)
        high_value_factor = min(1.0, signals.get("high_value_spend", 0) / 6)

        propensities = {
            "fx_lockup": round(0.5 + fx_factor * 0.45, 2),
            "credit_increase": round(0.4 + card_factor * 0.5, 2),
            "card_to_loan": round(0.35 + high_value_factor * 0.55, 2)
        }

        products = random.sample(self.product_catalog, k=random.randint(2, 4))
        segments = random.sample(self.segment_types, k=random.randint(1, 2))
        channels = random.sample(self.channel_preferences, k=random.randint(1, 2))

        profile = {
            "income": round(random.uniform(90000, 320000), 2),
            "products_owned": products,
            "propensities": propensities,
            "risk_profile": random.choice(['low', 'medium', 'high']),
            "segments": segments,
            "channel_preferences": channels,
            "credit_utilization": round(random.uniform(0.3, 0.9), 2),
            "life_stage": random.choice(self.life_stages),
            "preferred_currency": random.choice(self.currency_preferences),
            "tenure_months": random.randint(6, 84),
            "account_balance": round(account_balance, 2)
        }

        return profile

    def generate_context_cards(self) -> List[Dict[str, Any]]:
        """Return templated context cards that mirror the PAM config for UI inputs"""
        return [
            {
                "id": "fx_lockup",
                "name": "FX Lockup Promotion",
                "focus_area": "Secure FX rates for customers with frequent cross-border transfers",
                "priority": 1,
                "status": "active",
                "time_frame": {
                    "start_date": "2025-11-01",
                    "end_date": "2025-12-31",
                    "open_ended": False
                },
                "description": "Target customers sending at least 4 cross-border transfers in 30 days and with FX propensity.",
                "incentive": "Preferential FX rate + cashback on lockup fees",
                "eligibility": {
                    "min_recent_cross_border_transactions": 4,
                    "recent_days": 30,
                    "transaction_tags": ["cross_border"],
                    "propensity_score": {"key": "fx_lockup", "min": 0.65},
                    "required_products": ["salary_account"],
                    "risk_profiles": ["low", "medium"],
                    "segments": ["SME", "retail"],
                    "channel_preferences": ["digital", "branch"]
                },
                "preview": "Customer made multiple EUR transfers and prefers digital channels."
            },
            {
                "id": "credit_limit_increase",
                "name": "Credit Limit Optimisation",
                "focus_area": "Raise credit limits for clients showing high card utilisation",
                "priority": 2,
                "status": "active",
                "time_frame": {
                    "open_ended": True
                },
                "description": "Encourage customers who consistently use 65-90% of their limit to consider an increase.",
                "incentive": "Waived annual review fee on approved increases",
                "eligibility": {
                    "min_transactions": 6,
                    "recent_days": 30,
                    "min_credit_utilization": 0.65,
                    "max_credit_utilization": 0.9,
                    "propensity_score": {"key": "credit_increase", "min": 0.6},
                    "required_products": ["corporate_card", "salary_account"],
                    "risk_profiles": ["low"],
                    "segments": ["retail", "SME"]
                },
                "preview": "Frequent card spend with strong payment history."
            },
            {
                "id": "card_to_loan",
                "name": "Card-to-Loan Conversion",
                "focus_area": "Move high invoice spenders toward term loans",
                "priority": 3,
                "status": "scheduled",
                "time_frame": {
                    "start_date": "2025-11-15",
                    "end_date": "2025-12-15",
                    "open_ended": False
                },
                "description": "Convert consistent high spenders into structured financing opportunities.",
                "incentive": "Discounted first-year interest rate",
                "eligibility": {
                    "min_transactions": 8,
                    "recent_days": 30,
                    "min_income": 120000,
                    "propensity_score": {"key": "card_to_loan", "min": 0.5},
                    "risk_profiles": ["low", "medium"],
                    "segments": ["SME"]
                },
                "preview": "SMEs with repeat high-value invoice payments."
            }
        ]
    
    def _format_description(self, category: str, amount: float) -> tuple:
        """Format transaction description with real company names for PAM scraping
        
        Returns:
            tuple: (description, merchant_name or None)
        """
        
        # 60% chance to include a real company name (for PAM to research)
        include_company = random.random() < 0.6
        merchant = None
        
        descriptions = {
            # Revenue/Credit transactions
            'customer_payment': [
                'Customer payment received - Invoice #INV{}',
                'Payment from client - Account #AC{}',
                'Customer order payment',
                'Recurring customer payment'
            ],
            'sales_revenue': [
                'Product sales revenue',
                'Monthly sales deposit',
                'E-commerce sales',
                'Retail sales revenue'
            ],
            'contract_payment': [
                'Contract milestone payment',
                'Annual contract payment',
                'Service contract revenue',
                'Long-term contract installment'
            ],
            'service_revenue': [
                'Professional services rendered',
                'Consulting services payment',
                'Service delivery payment',
                'Monthly service fees'
            ],
            'subscription_revenue': [
                'Monthly subscription revenue',
                'SaaS subscription payments',
                'Membership fees collected',
                'Recurring subscription income'
            ],
            'invoice_payment': [
                'Invoice payment - Net 30',
                'Outstanding invoice settled',
                'Customer invoice payment',
                'Bulk invoice payment'
            ],
            'interest_income': [
                'Interest income earned',
                'Business savings interest',
                'Investment interest',
                'Cash management interest'
            ],
            'loan_proceeds': [
                'Business loan disbursement',
                'Line of credit drawdown',
                'Term loan proceeds',
                'Working capital loan'
            ],
            'investment_income': [
                'Investment returns',
                'Dividend income',
                'Capital gains',
                'Portfolio income'
            ],
            'grant_funding': [
                'Government grant received',
                'Research grant funding',
                'Small business grant',
                'Innovation grant'
            ],
            
            # Expense/Debit transactions
            'payroll': [
                'Bi-weekly payroll',
                'Monthly payroll processing',
                'Employee salaries and wages',
                'Payroll tax and benefits'
            ],
            'vendor_payment': [
                'Vendor payment - Purchase Order #PO{}',
                'Supplier payment',
                'Wholesale purchase',
                'Vendor invoice settlement'
            ],
            'rent_lease': [
                'Commercial rent payment',
                'Office lease payment',
                'Warehouse rent',
                'Retail space lease'
            ],
            'utilities': [
                'Commercial utilities',
                'Business electricity',
                'Water and sewer',
                'Gas and heating'
            ],
            'supplies': [
                'Office supplies',
                'Production materials',
                'Inventory purchase',
                'Operational supplies'
            ],
            'equipment_purchase': [
                'Equipment purchase',
                'Machinery acquisition',
                'Computer hardware',
                'Production equipment'
            ],
            'marketing': [
                'Marketing campaign',
                'Digital advertising',
                'Trade show expenses',
                'Brand promotion'
            ],
            'insurance': [
                'Business insurance premium',
                'Liability insurance',
                'Property insurance',
                'Workers compensation'
            ],
            'legal_fees': [
                'Legal services',
                'Attorney fees',
                'Contract review',
                'Compliance legal fees'
            ],
            'accounting_fees': [
                'Accounting services',
                'Bookkeeping fees',
                'Tax preparation',
                'Financial audit'
            ],
            'software_subscription': [
                'Business software subscription',
                'SaaS platform fees',
                'Cloud services',
                'Enterprise software license'
            ],
            'tax_payment': [
                'Quarterly tax payment',
                'Sales tax remittance',
                'Corporate tax',
                'Payroll tax deposit'
            ],
            'loan_payment': [
                'Business loan payment',
                'Line of credit payment',
                'Term loan installment',
                'Equipment financing'
            ],
            'maintenance': [
                'Equipment maintenance',
                'Building maintenance',
                'Vehicle maintenance',
                'Facility repairs'
            ],
            'travel_expense': [
                'Business travel',
                'Client meeting travel',
                'Trade show travel',
                'Sales team travel'
            ],
            'shipping_logistics': [
                'Shipping and freight',
                'Logistics services',
                'Delivery expenses',
                'Distribution costs'
            ],
            'consulting_fees': [
                'Business consulting',
                'Management consulting',
                'Strategy consulting',
                'Technical consulting'
            ],
            'training': [
                'Employee training',
                'Professional development',
                'Skills training',
                'Certification programs'
            ],
        }
        
        description_template = random.choice(descriptions.get(category, [category.replace('_', ' ').title()]))
        
        # Add reference numbers for some transaction types
        if '{}' in description_template:
            ref_number = random.randint(10000, 99999)
            description_template = description_template.format(ref_number)
        
        # Add real company names for specific transaction types (for PAM to scrape)
        if include_company:
            if category in ['customer_payment', 'sales_revenue', 'contract_payment', 'service_revenue']:
                # Revenue from real companies
                company = random.choice(self.all_real_companies)
                merchant = company
                description_template = f"Payment from {company}"
                
            elif category == 'software_subscription':
                # Software subscriptions from tech companies
                company = random.choice(self.real_tech_companies)
                merchant = company
                description_template = f"Subscription to {company}"
                
            elif category == 'vendor_payment':
                # Payments to real vendors
                company = random.choice(self.all_real_companies)
                merchant = company
                description_template = f"Payment to {company}"
                
            elif category == 'consulting_fees':
                # Consulting from major firms
                company = random.choice(self.real_service_companies)
                merchant = company
                description_template = f"Consulting services from {company}"
                
            elif category == 'marketing':
                # Marketing with tech/media companies
                company = random.choice(self.real_tech_companies + self.real_media_companies)
                merchant = company
                description_template = f"Advertising campaign with {company}"
                
            elif category == 'shipping_logistics':
                # Shipping with logistics companies
                company = random.choice(['FedEx Corporation', 'UPS Inc', 'DHL Express'])
                merchant = company
                description_template = f"Shipping via {company}"
        
        return description_template, merchant

    def _build_transaction_tags(self, category: str, transaction_type: str, amount: float) -> List[str]:
        """Build tags that signal behaviours for PAM contexts"""
        tags = []

        if category in self.cross_border_categories and random.random() < 0.65:
            tags.append('cross_border')

        if transaction_type == 'debit':
            if random.random() < 0.35:
                tags.append('card_spend')
            if abs(amount) >= 40000:
                tags.append('high_value')
        else:
            if random.random() < 0.25:
                tags.append('revenue')

        if random.random() < 0.15:
            tags.append('recurring')

        return tags
    
    def generate_dataset(self, num_transactions: int = 10, 
                        base_balance: float = 100000.0,
                        customer_index: int = 1) -> Dict[str, Any]:
        """Generate a complete business banking dataset with PII-enhanced structure"""
        
        transactions = []
        base_date = datetime.now() - timedelta(days=30)
        
        # Business accounts typically have more revenue transactions
        # Ratio: ~40% revenue (credit), ~60% expenses (debit)
        num_credits = random.randint(max(2, num_transactions // 3), max(3, num_transactions // 2))
        num_debits = num_transactions - num_credits
        
        # Generate credit transactions
        credit_categories = list(self.transaction_types['credit'].keys())
        for _ in range(num_credits):
            category = random.choice(credit_categories)
            transaction = self.generate_transaction('credit', category, base_date)
            transactions.append(transaction)
        
        # Generate debit transactions
        debit_categories = list(self.transaction_types['debit'].keys())
        for _ in range(num_debits):
            category = random.choice(debit_categories)
            transaction = self.generate_transaction('debit', category, base_date)
            transactions.append(transaction)
        
        # Sort transactions by date
        transactions.sort(key=lambda x: x['date'])
        
        # Calculate final balance
        total_change = sum(t['amount'] for t in transactions)
        final_balance = round(base_balance + total_change, 2)
        
        contextual_signals = self._compute_contextual_signals(transactions)
        customer_profile = self.generate_customer_profile(final_balance, contextual_signals)
        context_cards = self.generate_context_cards()

        # Generate PII data
        customer_id = self.generate_customer_id(customer_index)
        business_name = self.generate_business_name(customer_index)
        email = self.generate_business_email(business_name, customer_id)
        phone = self.generate_phone_number()
        account_info = self.generate_account_info(customer_id)
        
        # Return in new PII-enhanced structure
        return {
            'customer_id': customer_id,
            'name': business_name,
            'email': email,
            'phone': phone,
            'transactions': transactions,
            'account_info': account_info,
            'account_balance': final_balance,
            'customer_profile': customer_profile,
            'contextual_signals': contextual_signals,
            'bank_contexts': context_cards,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
    
    def generate_multiple_datasets(self, count: int, 
                                  min_transactions: int = 5,
                                  max_transactions: int = 15) -> List[Dict[str, Any]]:
        """Generate multiple business banking datasets"""
        
        datasets = []
        for i in range(1, count + 1):
            num_transactions = random.randint(min_transactions, max_transactions)
            # Business accounts have higher balances
            base_balance = round(random.uniform(50000, 500000), 2)
            
            dataset = self.generate_dataset(
                num_transactions=num_transactions,
                base_balance=base_balance,
                customer_index=i
            )
            datasets.append(dataset)
        
        return datasets
    
    def save_datasets(self, datasets: List[Dict[str, Any]], 
                     output_dir: str = 'generated_data',
                     format: str = 'individual') -> None:
        """
        Save datasets to files
        
        Args:
            datasets: List of datasets to save
            output_dir: Directory to save files
            format: 'individual' (one file per dataset) or 'combined' (all in one file)
        """
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        if format == 'individual':
            # Save each dataset to a separate file
            for i, dataset in enumerate(datasets, 1):
                filename = os.path.join(output_dir, f'dataset_{i:04d}.json')
                with open(filename, 'w') as f:
                    json.dump(dataset, f, indent=2)
            
            print(f"✅ Saved {len(datasets)} datasets to {output_dir}/")
            print(f"   Files: dataset_0001.json to dataset_{len(datasets):04d}.json")
            
        elif format == 'combined':
            # Save all datasets to one file
            filename = os.path.join(output_dir, 'all_datasets.json')
            with open(filename, 'w') as f:
                json.dump(datasets, f, indent=2)
            
            print(f"✅ Saved {len(datasets)} datasets to {filename}")
        
        else:
            raise ValueError(f"Unknown format: {format}")
    
    def print_dataset_stats(self, datasets: List[Dict[str, Any]]) -> None:
        """Print statistics about generated datasets"""
        
        total_transactions = sum(len(d['transactions']) for d in datasets)
        avg_transactions = total_transactions / len(datasets)
        
        all_balances = [d['account_balance'] for d in datasets]
        avg_balance = sum(all_balances) / len(all_balances)
        min_balance = min(all_balances)
        max_balance = max(all_balances)
        
        print("\n" + "=" * 60)
        print("📊 DATASET GENERATION STATISTICS")
        print("=" * 60)
        print(f"Total datasets: {len(datasets)}")
        print(f"Total transactions: {total_transactions}")
        print(f"Average transactions per dataset: {avg_transactions:.1f}")
        print(f"\nAccount Balances:")
        print(f"  Average: ${avg_balance:,.2f}")
        print(f"  Minimum: ${min_balance:,.2f}")
        print(f"  Maximum: ${max_balance:,.2f}")
        print("=" * 60 + "\n")


def main():
    """Main function to generate business banking datasets"""
    
    print("=" * 60)
    print("🏢 BUSINESS BANKING TRANSACTION DATA GENERATOR")
    print("   For SME Business Accounts (PII-Enhanced)")
    print("=" * 60)
    print("✨ Generates data with:")
    print("   - Business names, emails, phone numbers")
    print("   - Account information (account #, routing #)")
    print("   - Transaction history")
    print("   - Ready for PII detection testing")
    print("=" * 60)
    print()
    
    # Create generator
    generator = TransactionDataGenerator()
    
    # Configuration
    num_datasets = int(input("How many datasets to generate? (default: 10): ").strip() or "10")
    min_transactions = int(input("Minimum transactions per dataset? (default: 5): ").strip() or "5")
    max_transactions = int(input("Maximum transactions per dataset? (default: 15): ").strip() or "15")
    
    print(f"\n🔄 Generating {num_datasets} datasets...")
    print(f"   Transactions per dataset: {min_transactions}-{max_transactions}")
    print()
    
    # Generate datasets
    datasets = generator.generate_multiple_datasets(
        count=num_datasets,
        min_transactions=min_transactions,
        max_transactions=max_transactions
    )
    
    # Print statistics
    generator.print_dataset_stats(datasets)
    
    # Show sample dataset
    print("📋 Sample Dataset (first one):")
    print("-" * 60)
    print(json.dumps(datasets[0], indent=2))
    print("-" * 60)
    print()
    
    # Ask about saving
    save_choice = input("Save datasets to files? (y/n, default: y): ").strip().lower() or 'y'
    
    if save_choice == 'y':
        format_choice = input("Format? (individual/combined, default: individual): ").strip().lower() or 'individual'
        output_dir = input("Output directory? (default: generated_data): ").strip() or 'generated_data'
        
        generator.save_datasets(datasets, output_dir=output_dir, format=format_choice)
    
    print("\n✨ Generation complete!")
    print()
    print("💡 Next steps:")
    print("   1. Test PII detection: python3 test_pii_detection.py")
    print("   2. Use with pseudonymization service (port 5003)")
    print("   3. Feed to prompt engine via API")
    print("   4. Monitor PII detection and learning metrics")
    print()


if __name__ == "__main__":
    # Example usage with command-line arguments
    import sys
    
    if len(sys.argv) > 1:
        # Quick generation mode
        try:
            count = int(sys.argv[1])
            min_tx = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            max_tx = int(sys.argv[3]) if len(sys.argv) > 3 else 15
            
            generator = TransactionDataGenerator()
            datasets = generator.generate_multiple_datasets(count, min_tx, max_tx)
            generator.print_dataset_stats(datasets)
            generator.save_datasets(datasets, output_dir='generated_data', format='individual')
            
            print(f"\n✅ Generated {count} datasets in generated_data/")
            
        except (ValueError, IndexError) as e:
            print(f"Usage: {sys.argv[0]} <count> [min_transactions] [max_transactions]")
            print(f"Example: {sys.argv[0]} 100 5 15")
            sys.exit(1)
    else:
        # Interactive mode
        main()

