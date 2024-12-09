import asyncio
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from metaapi_cloud_sdk import MetaApi
import os

app = Flask(__name__)
load_dotenv()

# MetaTrader API token
token = os.getenv('TOKEN')

# Account information
account_info = {
    "Account Name": None,
    "Account Id": None,
    "Account Region": None,
}

# Cross-origin resource sharing (CORS) setup
from flask_cors import CORS
CORS(app, origins=["*"], supports_credentials=True)

# User credentials model
class UserCredentials:
    def __init__(self, login, password, server_name):
        self.login = login
        self.password = password
        self.server_name = server_name

@app.route("/", methods=["GET"])
def home():
    return {"welcome":"Thankyou"}

@app.route("/login", methods=["POST"])
async def login():
    try:
        # Parse the incoming JSON data
        data = request.get_json()
        credentials = UserCredentials(
            login=data.get("login"),
            password=data.get("password"),
            server_name=data.get("server_name"),
        )

        # Create a MetaApi instance
        meta_api = MetaApi(token)

        # Use async methods directly
        accounts = await meta_api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()

        # Find the account matching the provided login
        account = next((a for a in accounts if a.login == credentials.login and a.type.startswith('cloud')), None)

        if not account:
            # Create a new account if not found
            account = await meta_api.metatrader_account_api.create_account({
                'name': 'Terminal Account',
                'type': 'cloud',
                'login': credentials.login,
                'password': credentials.password,
                'server': credentials.server_name,
                'platform': 'mt5',
                'application': 'MetaApi',
                'magic': 1000,
            })

        # Deploy and connect the account
        await account.deploy()
        await account.wait_connected()

        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        # Fetch account information
        info = await connection.get_account_information()

        account_info.update({
            "Account Name": info["name"],
            "Account Id": account.id,
            "Account Region": account.region,
        })

        # Return success message with account info
        return jsonify({"message": "Login successful", "account_info": account_info})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
