import requests
import os
import base64
from datetime import datetime

# Load Monnify Credentials from Environment Variables
# MONNIFY_API_KEY = os.getenv("MONNIFY_API_KEY")
# MONNIFY_CONTRACT_CODE = os.getenv("MONNIFY_CONTRACT_CODE")
# MONNIFY_BASE_URL = "https://api.monnify.com/api/v1"

MONNIFY_CONTRACT_CODE = "4001509973"
MONNIFY_BASE_URL_2 = "https://sandbox.monnify.com/api/v2/bank-transfer/reserved-accounts"
MONNIFY_BASE_URL = "https://sandbox.monnify.com/api/v1"
PAYSTACK_SECRET = os.getenv("PAYSTACK_SECRET")
MONNIFY_SECRET = os.getenv("MONNIFY_SECRET")
MONNIFY_API_KEY = os.getenv("MONNIFY_API_KEY")
MONNIFY_WALLET_ACCOUNT = os.getenv("MONNIFY_WALLET_ACCOUNT")
MONNIFY_BASE_URL_3 = "https://sandbox.monnify.com/api/v2/disbursements/single"
monnify_token = None
token_expiry = 0

# Function to get authentication token
def get_monnify_token():
    """Fetch and cache Monnify authentication token."""
    credentials = f"{MONNIFY_API_KEY}:{MONNIFY_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {"Authorization": f"Basic {encoded_credentials}"}
    response = requests.post(f"{MONNIFY_BASE_URL}/auth/login", headers=headers)

    if response.status_code == 200:
        data = response.json()["responseBody"]
        return data["accessToken"]

    raise Exception("Failed to authenticate with Monnify")

# Function to create a dedicated virtual account
def create_reserved_account(account_reference, account_name, customer_email, bvn, customer_name=None):
    """Create a general reserved account."""
    token = get_monnify_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    data = {
        "accountReference": account_reference,
        "accountName": account_name,
        "currencyCode": "NGN",
        "contractCode": MONNIFY_CONTRACT_CODE,
        "customerEmail": customer_email,
        "bvn": bvn,
        "getAllAvailableBanks": True,
    }

    print("Monnify Request Data:", data)

    if customer_name:
        data["customerName"] = customer_name

    try:
        response = requests.post(
            "https://sandbox.monnify.com/api/v2/bank-transfer/reserved-accounts",
            json=data,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


# Function to initialize payment
def initialize_payment(amount: float, customer_email: str, payment_reference: str, customer_name: str):
    token = get_monnify_token()
    url = f"{MONNIFY_BASE_URL}/transaction/initialize"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "amount": amount,
        "customerName": customer_name,
        "customerEmail": customer_email,
        "paymentReference": payment_reference,
        "paymentDescription": "Payment for Service",
        "currencyCode": "NGN",
        "contractCode": MONNIFY_CONTRACT_CODE,
        "redirectUrl": "https://yourapp.com/payment-success",
        "paymentMethods": ["CARD", "ACCOUNT_TRANSFER"]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Function to verify transaction status
def verify_transaction(payment_reference: str):
    token = get_monnify_token()
    url = f"{MONNIFY_BASE_URL}/transaction/status?paymentReference={payment_reference}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.get(url, headers=headers)
    return response.json()

# Function to refund a transaction
def refund_transaction(transaction_reference: str, amount: float, reason: str):
    token = get_monnify_token()
    url = f"{MONNIFY_BASE_URL}/transaction/refund"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "transactionReference": transaction_reference,
        "amount": amount,
        "refundReason": reason
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
