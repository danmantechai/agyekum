import os
import asyncio
from datetime import datetime, timedelta
from metaapi_cloud_sdk import MetaApi
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt


# Terminal state
console = Console()
account_info = {
    "Account Name": None,
    "Currency": "XAUUSD",
    "Mode": None,  # Will be "buy" or "sell"
}

# MetaTrader API setup
token = os.getenv('TOKEN') or '<put in your token here>'
login = os.getenv('LOGIN') or '<put in your MT login here>'
password = os.getenv('PASSWORD') or '<put in your MT password here>'
server_name = os.getenv('SERVER') or '<put in your MT server name here>'
api = MetaApi(token)


async def connect_to_mt5():
    """Connect to MetaTrader and return the account instance."""
    try:
        accounts = await api.metatrader_account_api.get_accounts_with_infinite_scroll_pagination()
        account = next((a for a in accounts if a.login == login and a.type.startswith('cloud')), None)

        if not account:
            console.print(Panel("[yellow]Adding MT5 account to MetaApi[/yellow]"))
            account = await api.metatrader_account_api.create_account(
                {
                    'name': 'Terminal Account',
                    'type': 'cloud',
                    'login': login,
                    'password': password,
                    'server': server_name,
                    'platform': 'mt5',
                    'application': 'MetaApi',
                    'magic': 1000,
                }
            )
        else:
            console.print(Panel("[green]MT5 account already added to MetaApi[/green]"))

        console.print("[cyan]Deploying account and connecting...[/cyan]")
        await account.deploy()
        await account.wait_connected()
        console.print("[bold green]Connected to MT5 successfully![/bold green]")

        connection = account.get_rpc_connection()
        await connection.connect()
        await connection.wait_synchronized()

        info = await connection.get_account_information()
        account_info["Account Name"] = info["name"]
        return connection
    except Exception as e:
        console.print(Panel(f"[red]Error connecting to MT5: {e}[/red]"))
        raise e


async def execute_trade(connection, strategy):
    """Perform a trade based on the selected strategy."""
    if account_info["Mode"] not in ["buy", "sell"]:
        console.print(Panel("[red]Set a trading mode before executing trades![/red]"))
        return

    try:
        symbol = account_info["Currency"]
        volume = 0.1
        console.print(Panel(f"[cyan]Executing {strategy} in {account_info['Mode']} mode...[/cyan]"))

        if strategy == "30 pip TP":
            result = await connection.create_market_buy_order(
                symbol, volume, {'takeProfit': 30} if account_info["Mode"] == "buy" else {'stopLoss': 30}
            )
        elif strategy == "50 pip TP":
            result = await connection.create_market_buy_order(
                symbol, volume, {'takeProfit': 50} if account_info["Mode"] == "buy" else {'stopLoss': 50}
            )
        elif strategy == "Trailing SL":
            result = await connection.create_market_buy_order(
                symbol, volume, {'trailingStopLoss': 15} if account_info["Mode"] == "buy" else {'trailingStopLoss': 15}
            )

        console.print(Panel(f"[green]Trade completed: {result['stringCode']}[/green]"))
    except Exception as e:
        console.print(Panel(f"[red]Trade failed: {e}[/red]"))


def display_account_info():
    """Display the account info panel."""
    table = Table(title="Account Information", expand=True)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Account Name", account_info["Account Name"] or "Not Connected")
    table.add_row("Currency", account_info["Currency"])
    table.add_row("Current Mode", account_info["Mode"] or "Not Set")
    console.print(table)


async def main_menu(connection):
    while True:
        console.clear()
        display_account_info()
        console.print(Panel("Main Menu", style="bold cyan"))
        console.print("[1] Trading Mode")
        console.print("[2] Trade")
        console.print("[E] Exit")
        choice = Prompt.ask("Select an option").strip().lower()

        if choice == "1":
            await trading_mode_menu()
        elif choice == "2":
            await trade_menu(connection)
        elif choice == "e":
            console.print(Panel("[bold green]Exiting application. Goodbye![/bold green]"))
            break
        else:
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


async def trading_mode_menu():
    while True:
        console.clear()
        display_account_info()
        console.print(Panel("Trading Mode Menu", style="bold cyan"))
        console.print("[1] Buy")
        console.print("[2] Sell")
        console.print("[P] Go Back")
        choice = Prompt.ask("Select a mode").strip().lower()

        if choice == "1":
            account_info["Mode"] = "buy"
        elif choice == "2":
            account_info["Mode"] = "sell"
        elif choice == "p":
            break
        else:
            console.print("[bold red]Invalid option. Try again.[/bold red]")


async def trade_menu(connection):
    while True:
        console.clear()
        display_account_info()
        console.print(Panel("Trade Strategies Menu", style="bold cyan"))
        console.print("[1] 30 pip Take Profit")
        console.print("[2] 50 pip Take Profit")
        console.print("[3] Trailing Stop Loss")
        console.print("[P] Go Back")
        choice = Prompt.ask("Select a strategy").strip().lower()

        if choice == "1":
            await execute_trade(connection, "30 pip TP")
        elif choice == "2":
            await execute_trade(connection, "50 pip TP")
        elif choice == "3":
            await execute_trade(connection, "Trailing SL")
        elif choice == "p":
            break
        else:
            console.print("[bold red]Invalid option. Try again.[/bold red]")


async def run_app():
    connection = await connect_to_mt5()
    await main_menu(connection)


if __name__ == "__main__":
    asyncio.run(run_app())
