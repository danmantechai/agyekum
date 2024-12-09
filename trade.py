from datetime import datetime
import os
import requests
from dotenv import load_dotenv
load_dotenv()
auth_token=os.getenv("TOKEN")
def place_trade(
api_url,
    actionType,
    symbol,
    volume,
    stopLoss=None,
    takeProfit=None,
    stopLossUnits="RELATIVE_PIPS",
    takeProfitUnits="RELATIVE_PIPS",
    trailingStopLoss=None,
    comment=None,
    clientId=None,
    magic=None,
    slippage=None,
    fillingModes=None,
):
    
    if not actionType or not symbol or volume is None:
        raise ValueError("actionType, symbol, and volume are required parameters.")

    # Build request payload
    payload = {
        "actionType": actionType,
        "symbol": symbol,
        "volume": volume,
        "stopLoss": stopLoss,
        "takeProfit": takeProfit,
        "stopLossUnits": stopLossUnits,
        "takeProfitUnits": takeProfitUnits,
        "trailingStopLoss": trailingStopLoss,
        "comment": comment,
        "clientId": clientId,
        "magic": magic,
        "slippage": slippage,
        "fillingModes": fillingModes,
    }

    # Remove keys with None values
    payload = {key: value for key, value in payload.items() if value is not None}

    headers = {"Content-Type": "application/json"}
    print(auth_token)
    if auth_token:
        headers["auth-token"] = auth_token

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()  # Return JSON response
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}




def generate_trade_comment(actionType, symbol, volume):
    """
    Generates a unique and descriptive comment for a trade order.

0241147726

Newmont Kwame Obeng 
    Args:
        actionType (str): The type of action, e.g., ORDER_TYPE_BUY or ORDER_TYPE_SELL.
        symbol (str): The symbol being traded, e.g., "AUDNZD".
        volume (float): The trade volume.

    Returns:
        str: A generated comment string.
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{actionType}_{symbol}_{volume:.2f}_{timestamp}"