import asyncio
from datetime import datetime, timedelta
import os
from metaapi_cloud_sdk import MetaApi
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
# Terminal state
console = Console()
account_info = {
    "Account Name": None,
    "Currency": "XAUUSD",
    "Mode": None,  # Will be "buy" or "sell"
}
logs = []  # To hold the log messages

# MetaTrader API setup
token = os.getenv('TOKEN')

async def add_log(message, success=True):
    """Add a log message."""
    logs.append((datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message, success))
    if len(logs) > 5:  # Keep the last 5 messages
        logs.pop(0)


def display_logs():
    """Display the log messages."""
    table = Table(title="Logs", expand=True)
    table.add_column("Time", style="dim", no_wrap=True)
    table.add_column("Message", style="bold")
    table.add_column("Status", style="bold green" if logs else "bold red")

    for log in logs:
        time, message, success = log
        table.add_row(time, message, "Success" if success else "Error")
    console.print(table)


async def execute_trade(connection, strategy):
    """Perform a trade based on the selected strategy."""
    if account_info["Mode"] not in ["buy", "sell"]:
        await add_log("Set a trading mode before executing trades!", success=False)
        return

    try:
        symbol = account_info["Currency"]
        volume = 0.1
        trade_message = f"{strategy} in {account_info['Mode']} mode for {symbol}"
        console.print(Panel(f"[cyan]Executing {trade_message}...[/cyan]"))

        # Dummy example for placing a trade
        if strategy == "30 pip TP":
            await asyncio.sleep(1)  # Simulate API call
        elif strategy == "50 pip TP":
            await asyncio.sleep(1)
        elif strategy == "Trailing SL":
            await asyncio.sleep(1)

        await add_log(f"Trade placed: {trade_message}")
    except Exception as e:
        await add_log(f"Trade failed: {e}", success=False)


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
        display_logs()
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
            await add_log("Invalid option. Please try again.", success=False)


async def trading_mode_menu():
    while True:
        console.clear()
        display_account_info()
        display_logs()
        console.print(Panel("Trading Mode Menu", style="bold cyan"))
        console.print("[1] Buy")
        console.print("[2] Sell")
        console.print("[P] Go Back")
        choice = Prompt.ask("Select a mode").strip().lower()

        if choice == "1":
            account_info["Mode"] = "buy"
            await add_log("Trading mode set to Buy")
        elif choice == "2":
            account_info["Mode"] = "sell"
            await add_log("Trading mode set to Sell")
        elif choice == "p":
            break
        else:
            await add_log("Invalid mode selected.", success=False)


async def trade_menu(connection):
    while True:
        console.clear()
        display_account_info()
        display_logs()
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
            await add_log("Invalid strategy selected.", success=False)


async def run_app():
    login = Prompt.ask("[bold yellow]Login[/bold yellow]")
    password = Prompt.ask("[bold yellow]Password[/bold yellow]", password=True)
    server_name = Prompt.ask("[bold yellow]Server Name[/bold yellow]")
    connection = None  # Simulate MetaTrader connection
    await main_menu(connection)


if __name__ == "__main__":
    asyncio.run(run_app())
