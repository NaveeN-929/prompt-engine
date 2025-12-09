const BUSINESS_NAMES = [
  'Tech Solutions Inc',
  'Global Logistics Ltd',
  'Green Energy Co',
  'Precision Manufacturing',
  'Digital Marketing Agency',
  'Wholesale Distributors Inc'
];

const CURRENCIES = ['USD', 'SGD', 'EUR', 'GBP', 'AED'];

const TRANSACTION_CATEGORIES = {
  credit: ['sales_revenue', 'customer_payment', 'service_revenue', 'contract_payment', 'subscription_revenue'],
  debit: ['payroll', 'vendor_payment', 'rent_lease', 'software_subscription', 'marketing']
};

const PROFILE_CONFIGS = {
  balanced: {
    creditBias: 0.62,
    amountMultiplier: 1,
    spanDays: 45,
    lookbackDays: 60,
    crossBorderRate: 0.25,
    descriptionPrefix: 'Growth and expansion'
  },
  negative: {
    creditBias: 0.3,
    amountMultiplier: 1.25,
    spanDays: 60,
    lookbackDays: 75,
    crossBorderRate: 0.5,
    descriptionPrefix: 'Liquidity pressure'
  },
  neutral: {
    creditBias: 0.5,
    amountMultiplier: 0.85,
    spanDays: 30,
    lookbackDays: 30,
    crossBorderRate: 0.12,
    descriptionPrefix: 'Steady-state operations'
  }
};

const COUNTERPARTIES = [
  'Microsoft Corporation',
  'Amazon Web Services Inc',
  'Google LLC',
  'Adobe Inc',
  'PayPal Holdings Inc',
  'Stripe Inc'
];

const NOTES = [
  'Quarterly subscription',
  'Customer milestone payment',
  'Vendor settlement',
  'Payroll run',
  'Infrastructure investment'
];

const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
const randomChoice = (arr) => arr[randomInt(0, arr.length - 1)];

const buildAccountInfo = () => ({
  account_number: `${randomInt(10000000, 99999999)}`,
  routing_number: `${randomInt(100000000, 999999999)}`,
  bank_name: randomChoice(['First National Bank', 'Commerce Bank', 'Enterprise Bank']),
  account_type: randomChoice(['business_checking', 'commercial_account'])
});

const chooseTransactionType = (config) =>
  Math.random() < config.creditBias ? 'credit' : 'debit';

const buildTransaction = (index, transactionType, referenceDate, customerName, customerId, config, accountInfo) => {
  const category = randomChoice(TRANSACTION_CATEGORIES[transactionType]);
  const base = transactionType === 'credit' ? 15000 : 8000;
  const variance = transactionType === 'credit' ? 10000 : 5000;
  const amount = (base + Math.random() * variance) * config.amountMultiplier;
  const signedAmount = transactionType === 'debit' ? -Math.abs(amount) : amount;
  const timestamp = new Date(referenceDate.getTime() + randomInt(0, config.spanDays) * 86400000);
  const description = `${config.descriptionPrefix} - ${NOTES[index % NOTES.length]}`;
  const tags = transactionType === 'debit' ? ['card_spend'] : ['incoming_payment'];
  if (Math.random() < config.crossBorderRate) {
    tags.push('cross_border');
  }

  const beneficiary = randomChoice(COUNTERPARTIES);

  return {
    transaction_date: timestamp.toISOString().split('T')[0],
    amount: Number(signedAmount.toFixed(2)),
    currency: randomChoice(CURRENCIES),
    transaction_type: transactionType,
    description,
    transaction_category: category,
    tags,
    remittance_information: description,
    date: timestamp.toISOString().split('T')[0],
    type: transactionType,
    originator: customerName,
    beneficiary,
    counterparty: beneficiary,
    debtor: customerName,
    creditor: beneficiary,
    debtor_account: accountInfo.account_number,
    creditor_account: accountInfo.routing_number,
    initiating_party: customerId,
    ultimate_debtor: customerName,
    ultimate_creditor: beneficiary,
    merchant: beneficiary,
    originator_account: accountInfo.account_number,
    beneficiary_account: accountInfo.routing_number
  };
};

export const generateDataset = (profile = 'balanced', transactionCount = 40) => {
  const config = PROFILE_CONFIGS[profile] ?? PROFILE_CONFIGS.balanced;
  const safeCount = Math.max(8, Math.min(5000, transactionCount));
  const referenceDate = new Date(Date.now() - config.lookbackDays * 24 * 3600 * 1000);
  const customerName = randomChoice(BUSINESS_NAMES);
  const customerId = `${customerName.split(' ')[0].slice(0, 3).toUpperCase()}_${randomInt(100, 999)}`;
  const accountInfo = buildAccountInfo();

  const transactions = [];
  for (let idx = 0; idx < safeCount; idx += 1) {
    const transactionType = chooseTransactionType(config);
    transactions.push(
      buildTransaction(idx, transactionType, referenceDate, customerName, customerId, config, accountInfo)
    );
  }

  return {
    customer_id: customerId,
    name: customerName,
    email: `contact@${customerName.toLowerCase().replace(/\s+/g, '')}.com`,
    phone: `+1-${randomInt(200, 999)}-${randomInt(1000, 9999)}`,
    currency: randomChoice(CURRENCIES),
    transactions,
    account_info: accountInfo,
    profile,
    generated_at: new Date().toISOString()
  };
};

