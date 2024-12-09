import os
import asyncio
from datetime import datetime
from metaapi_cloud_sdk import MetaApi
from dotenv import load_dotenv
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.clock import mainthread

load_dotenv()

# MetaTrader API setup
token = os.getenv("TOKEN")

# App state
account_info = {
    "Account Name": None,
    "Account Id": None,
    "Account Region": None,
    "Currency": "GOLD",
    "Mode": None,
}

logs = []  # To hold the log messages


def api_url(region, id):
    return f"https://mt-client-api-v1.{region}.agiliumtrade.ai/users/current/accounts/{id}/trade'"


async def add_log(message, success=True):
    """Add a log message."""
    logs.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message, success))
    if len(logs) > 5:  # Keep the last 5 messages
        logs.pop(0)


class LoginScreen(Screen):
    async def on_login(self):
        """Handle login logic."""
        login = self.ids.login_input.text
        password = self.ids.password_input.text
        server_name = self.ids.server_input.text

        if not login or not password or not server_name:
            self.ids.error_label.text = "All fields are required."
            return

        self.ids.error_label.text = "Connecting..."
        try:
            connection = await self.connect_to_mt5(login, password, server_name)
            self.manager.get_screen("menu").connection = connection
            self.manager.current = "menu"
        except Exception as e:
            self.ids.error_label.text = f"Error: {e}"

    async def connect_to_mt5(self, login, password, server_name):
        """Connect to MetaTrader and return the account instance."""
        try:
            api = MetaApi(token)
            accounts = await api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
            account = next((a for a in accounts if a.login == login and a.type.startswith("cloud")), None)

            if not account:
                account = await api.metatrader_account_api.create_account(
                    {
                        "name": "Terminal Account",
                        "type": "cloud",
                        "login": login,
                        "password": password,
                        "server": server_name,
                        "platform": "mt5",
                        "application": "MetaApi",
                        "magic": 1000,
                    }
                )

            await account.deploy()
            await account.wait_connected()

            connection = account.get_rpc_connection()
            await connection.connect()
            await connection.wait_synchronized()

            info = await connection.get_account_information()
            account_info["Account Name"] = info["name"]
            account_info["Account Id"] = account.id
            account_info["Account Region"] = account.region
            return connection
        except Exception as e:
            raise Exception(f"Failed to connect to MT5: {e}")


class MenuScreen(Screen):
    connection = None

    def on_enter(self):
        """Update UI with account info."""
        self.update_account_info()

    def update_account_info(self):
        """Update the account information panel."""
        info = (
            f"Name: {account_info['Account Name'] or 'Not Connected'}\n"
            f"Id: {account_info['Account Id'] or 'Not Connected'}\n"
            f"Region: {account_info['Account Region'] or 'Not Connected'}\n"
            f"Currency: {account_info['Currency']}\n"
            f"Mode: {account_info['Mode'] or 'Not Set'}"
        )
        self.ids.account_info_label.text = info

    def set_mode(self, mode):
        """Set the trading mode."""
        account_info["Mode"] = mode
        self.update_account_info()

    async def execute_trade(self, strategy):
        """Perform a trade based on the selected strategy."""
        try:
            symbol = account_info["Currency"]
            if account_info["Mode"] not in ["buy", "sell"]:
                raise Exception("Set a trading mode before executing trades!")

            action_type = {
                "buy": self.connection.create_market_buy_order,
                "sell": self.connection.create_market_sell_order,
            }[account_info["Mode"]]

            if strategy == "30 pip TP":
                result = await action_type(
                    symbol="GOLD",
                    volume=0.2,
                    stop_loss=0.0,
                    take_profit=3.0,
                    options={
                        "stopLossUnits": "RELATIVE_PIPS",
                        "takeProfitUnits": "RELATIVE_PIPS",
                        "comment": "comment",
                    },
                )
            # Add more strategies here

            await add_log(f"Trade placed: {result}")
        except Exception as e:
            await add_log(f"Trade failed: {e}", success=False)


class MainApp(App):
    def build(self):
        return Builder.load_string(
            """
ScreenManager:
    LoginScreen:
    MenuScreen:

<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: "vertical"
        padding: 10
        spacing: 10
        TextInput:
            id: login_input
            hint_text: "Login"
        TextInput:
            id: password_input
            hint_text: "Password"
            password: True
        TextInput:
            id: server_input
            hint_text: "Server Name"
        Button:
            text: "Login"
            on_press: app.run_coroutine(root.on_login())
            
        Label:
            id: error_label
            text: ""
            color: 1, 0, 0, 1

<MenuScreen>:
    name: "menu"
    BoxLayout:
        orientation: "vertical"
        Label:
            id: account_info_label
            text: "Account Info"
        Button:
            text: "Set Buy Mode"
            on_press: root.set_mode("buy")
        Button:
            text: "Set Sell Mode"
            on_press: root.set_mode("sell")
        Button:
            text: "Execute 30 pip TP Trade"
           
            on_press: app.run_coroutine(root.execute_trade("30 pip TP"))
"""
        )
    
    @mainthread
    def run_coroutine(self, coroutine):
        asyncio.run(coroutine)


if __name__ == "__main__":
    MainApp().run()