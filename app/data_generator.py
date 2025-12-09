"""
Lightweight dataset factory for the prompt engine UI
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List


class DynamicDatasetGenerator:
    def __init__(self) -> None:
        self.business_names = [
            'Tech Solutions Inc', 'Global Logistics Ltd', 'Green Energy Co',
            'Precision Manufacturing', 'Digital Marketing Agency', 'Wholesale Distributors Inc'
        ]
        self.currencies = ['USD', 'SGD', 'EUR', 'GBP', 'AED']
        self.transaction_categories = {
            'credit': [
                'sales_revenue', 'customer_payment', 'service_revenue',
                'contract_payment', 'subscription_revenue'
            ],
            'debit': [
                'payroll', 'vendor_payment', 'rent_lease',
                'software_subscription', 'marketing'
            ]
        }
        self.profile_configs = {
            'balanced': {
                'credit_bias': 0.62,
                'amount_multiplier': 1.0,
                'span_days': 45,
                'lookback_days': 60,
                'cross_border_rate': 0.25,
                'description_prefix': 'Growth and expansion'
            },
            'negative': {
                'credit_bias': 0.3,
                'amount_multiplier': 1.25,
                'span_days': 60,
                'lookback_days': 75,
                'cross_border_rate': 0.5,
                'description_prefix': 'Liquidity pressure'
            },
            'neutral': {
                'credit_bias': 0.5,
                'amount_multiplier': 0.85,
                'span_days': 30,
                'lookback_days': 30,
                'cross_border_rate': 0.12,
                'description_prefix': 'Steady-state operations'
            }
        }
        self.counterparties = [
            'Microsoft Corporation', 'Amazon Web Services Inc', 'Google LLC',
            'Adobe Inc', 'PayPal Holdings Inc', 'Stripe Inc'
        ]
        self.notes = [
            'Quarterly subscription', 'Customer milestone payment',
            'Vendor settlement', 'Payroll run', 'Infrastructure investment'
        ]

    def generate(
        self,
        profile: str = 'balanced',
        transaction_count: int = 30
    ) -> Dict[str, Any]:
        config = self.profile_configs.get(profile, self.profile_configs['balanced'])
        transaction_count = max(8, min(200, transaction_count))
        reference_date = datetime.utcnow() - timedelta(days=config['lookback_days'])
        customer_name = random.choice(self.business_names)
        customer_id = f"{customer_name.split()[0][:3].upper()}_{random.randint(100, 999)}"

        account_info = self._build_account_info()
        transactions: List[Dict[str, Any]] = []
        for idx in range(transaction_count):
            txn_type = self._choose_transaction_type(config)
            transaction = self._build_transaction(
                idx,
                txn_type,
                reference_date,
                customer_name,
                customer_id,
                config,
                account_info
            )
            transactions.append(transaction)

        return {
            'customer_id': customer_id,
            'name': customer_name,
            'email': f"contact@{customer_name.lower().replace(' ', '')}.com",
            'phone': f"+1-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
            'currency': random.choice(self.currencies),
            'transactions': transactions,
            'account_info': account_info,
            'profile': profile,
            'generated_at': datetime.utcnow().isoformat()
        }

    def _choose_transaction_type(self, config: Dict[str, Any]) -> str:
        return 'credit' if random.random() < config['credit_bias'] else 'debit'

    def _build_transaction(
        self,
        index: int,
        transaction_type: str,
        base_date: datetime,
        customer_name: str,
        customer_id: str,
        config: Dict[str, Any],
        account_info: Dict[str, str]
    ) -> Dict[str, Any]:
        category = random.choice(self.transaction_categories[transaction_type])
        amount = self._random_amount(config, transaction_type)
        currency = random.choice(self.currencies)
        timestamp = base_date + timedelta(days=random.randint(0, config['span_days']))

        description = f"{config['description_prefix']} - {self.notes[index % len(self.notes)]}"
        tags = ['card_spend'] if transaction_type == 'debit' else ['incoming_payment']
        if random.random() < config['cross_border_rate']:
            tags.append('cross_border')

        beneficiary = random.choice(self.counterparties)

        return {
            'transaction_date': timestamp.date().isoformat(),
            'amount': round(amount, 2),
            'currency': currency,
            'transaction_type': transaction_type,
            'description': description,
            'transaction_category': category,
            'tags': tags,
            'remittance_information': description,
            'date': timestamp.date().isoformat(),
            'type': transaction_type,
            'originator': customer_name,
            'beneficiary': beneficiary,
            'counterparty': beneficiary,
            'debtor': customer_name,
            'creditor': beneficiary,
            'debtor_account': account_info['account_number'],
            'creditor_account': account_info['routing_number'],
            'initiating_party': customer_id,
            'ultimate_debtor': customer_name,
            'ultimate_creditor': beneficiary,
            'merchant': beneficiary,
            'originator_account': account_info['account_number'],
            'beneficiary_account': account_info['routing_number']
        }

    def _random_amount(self, config: Dict[str, Any], transaction_type: str) -> float:
        base = 15000 if transaction_type == 'credit' else 8000
        variance = 10000 if transaction_type == 'credit' else 5000
        amount = (base + random.uniform(0, variance)) * config['amount_multiplier']
        return amount if transaction_type == 'credit' else -abs(amount)

    def _build_account_info(self) -> Dict[str, str]:
        return {
            'account_number': f"{random.randint(10000000, 99999999)}",
            'routing_number': f"{random.randint(100000000, 999999999)}",
            'bank_name': random.choice(['First National Bank', 'Commerce Bank', 'Enterprise Bank']),
            'account_type': random.choice(['business_checking', 'commercial_account'])
        }

