from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from metaapi_cloud_sdk import MetaApi
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

import os

app = FastAPI()
load_dotenv()


origins = [
  "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Can use ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# MetaTrader API token
token = os.getenv('TOKEN')

# Account information
account_info = {
    "Account Name": None,
    "Account Id": None,
    "Account Region": None,
}

class UserCredentials(BaseModel):
    login: str
    password: str
    server_name: str


@app.post("/login")
async def login(credentials: UserCredentials):
    try:
        meta_api = MetaApi(token)
        accounts = await meta_api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        account = next((a for a in accounts if a.login == credentials.login and a.type.startswith('cloud')), None)
        print(account)
        if not account:
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
        await account.deploy()
        await account.wait_connected()

        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()
        info = await connection.get_account_information()

        account_info.update({
            "Account Name": info["name"],
            "Account Id": account.id,
            "Account Region": account.region,
        })
        return {"message": "Login successful", "account_info": account_info}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))




