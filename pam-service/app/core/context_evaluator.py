"""
Context Evaluator
Evaluate bank context cards against customer signals to prioritize eligible actions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .context_loader import ContextCard

logger = logging.getLogger(__name__)


def _parse_transaction_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            logger.debug(f"Unable to parse transaction date: {value}")
            return None


class ContextEvaluator:
    """
    Simple evaluator that picks the highest-priority context card that matches the
    customer profile and transaction signals.
    """

    def evaluate(self,
                 contexts: List[ContextCard],
                 input_data: Dict[str, Any],
                 reference_time: Optional[datetime] = None
                 ) -> Tuple[Optional[ContextCard], Dict[str, Any]]:
        now = reference_time or datetime.utcnow()
        transactions = input_data.get("transactions", []) or []
        profile = input_data.get("customer_profile", {}) or {}

        for context in sorted(contexts, key=lambda ctx: ctx.priority):
            if not context.is_active(now):
                logger.debug(f"Skipping inactive context '{context.name}'")
                continue

            eligibility = self._matches(context, transactions, profile, input_data, now)
            if eligibility.get("eligible"):
                logger.info(f"Context '{context.name}' matched for customer {input_data.get('customer_id')}")
                return context, eligibility

        return None, {}

    def _matches(self,
                 context: ContextCard,
                 transactions: List[Dict[str, Any]],
                 profile: Dict[str, Any],
                 input_data: Dict[str, Any],
                 now: datetime) -> Dict[str, Any]:
        eligibility = context.eligibility or {}
        match_details = {}
        eligible = True

        recent_days = eligibility.get("recent_days", 30)
        window_transactions = self._filter_transactions(transactions, recent_days, now)

        for rule, rule_value in eligibility.items():
            checker = getattr(self, f"_check_{rule}", None)
            if checker:
                result = checker(rule_value, window_transactions, profile, input_data, now)
                match_details[rule] = result
                if not result:
                    eligible = False

        return {
            "eligible": eligible,
            "matched_rules": match_details,
            "context_priority": context.priority
        }

    @staticmethod
    def _filter_transactions(transactions, days, now):
        cutoff = now - timedelta(days=days)
        filtered = []
        for tx in transactions:
            tx_date = _parse_transaction_date(tx.get("date"))
            if tx_date and tx_date >= cutoff:
                filtered.append(tx)
        return filtered

    @staticmethod
    def _check_min_transactions(value, window_transactions, profile, input_data, now):
        try:
            required = int(value)
        except (TypeError, ValueError):
            return False
        return len(window_transactions) >= required

    @staticmethod
    def _check_min_recent_cross_border_transactions(value, window_transactions, profile, input_data, now):
        count = sum(1 for tx in window_transactions if "cross_border" in tx.get("tags", []))
        try:
            required = int(value)
        except (TypeError, ValueError):
            return False
        return count >= required

    @staticmethod
    def _check_transaction_tags(values, transactions, profile, input_data, now):
        if not isinstance(values, list):
            return False
        for tx in transactions:
            tx_tags = tx.get("tags", [])
            if any(tag in tx_tags for tag in values):
                return True
        return False

    @staticmethod
    def _check_required_products(values, transactions, profile, input_data, now):
        if not isinstance(values, list):
            return False
        owned = set(profile.get("products_owned", []))
        return bool(owned.intersection(values))

    @staticmethod
    def _check_propensity_score(value, transactions, profile, input_data, now):
        if not isinstance(value, dict):
            return False
        key = value.get("key")
        minimum = value.get("min", 0)
        score = profile.get("propensities", {}).get(key, 0)
        try:
            minimum = float(minimum)
        except (TypeError, ValueError):
            minimum = 0
        return score >= minimum

    @staticmethod
    def _check_risk_profiles(values, transactions, profile, input_data, now):
        if not isinstance(values, list):
            return False
        risk = profile.get("risk_profile")
        return risk in values

    @staticmethod
    def _check_segments(values, transactions, profile, input_data, now):
        if not isinstance(values, list):
            return False
        segments = profile.get("segments", [])
        return bool(set(segments).intersection(values))

    @staticmethod
    def _check_life_stages(values, transactions, profile, input_data, now):
        if not isinstance(values, list):
            return False
        stage = profile.get("life_stage")
        return stage in values

    @staticmethod
    def _check_channel_preferences(values, transactions, profile, input_data, now):
        if not isinstance(values, list):
            return False
        channels = profile.get("channel_preferences", [])
        return bool(set(channels).intersection(values))

    @staticmethod
    def _check_min_income(value, transactions, profile, input_data, now):
        try:
            minimum = float(value)
        except (TypeError, ValueError):
            return False
        income = profile.get("income")
        if income is None:
            return False
        return float(income) >= minimum

    @staticmethod
    def _check_max_income(value, transactions, profile, input_data, now):
        try:
            maximum = float(value)
        except (TypeError, ValueError):
            return False
        income = profile.get("income")
        if income is None:
            return False
        return float(income) <= maximum

    @staticmethod
    def _check_min_balance(value, transactions, profile, input_data, now):
        try:
            minimum = float(value)
        except (TypeError, ValueError):
            return False
        balance = input_data.get("account_balance")
        if balance is None:
            return False
        return float(balance) >= minimum

    @staticmethod
    def _check_max_balance(value, transactions, profile, input_data, now):
        try:
            maximum = float(value)
        except (TypeError, ValueError):
            return False
        balance = input_data.get("account_balance")
        if balance is None:
            return False
        return float(balance) <= maximum

    @staticmethod
    def _check_min_credit_utilization(value, transactions, profile, input_data, now):
        try:
            minimum = float(value)
        except (TypeError, ValueError):
            return False
        score = profile.get("credit_utilization")
        if score is None:
            return False
        return float(score) >= minimum

    @staticmethod
    def _check_max_credit_utilization(value, transactions, profile, input_data, now):
        try:
            maximum = float(value)
        except (TypeError, ValueError):
            return False
        score = profile.get("credit_utilization")
        if score is None:
            return False
        return float(score) <= maximum

