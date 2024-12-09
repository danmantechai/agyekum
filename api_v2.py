import os
import asyncio
from datetime import datetime, timedelta
from metaapi_cloud_sdk import MetaApi
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from dotenv import load_dotenv
from trade import place_trade
# Get the directory of the currently running script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Load .env from the same directory as the executable
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)
# Terminal state
logs = []  # To hold the log messages
console = Console()
account_info = {
    "Account Name": None,
    "Account Id":None,
    "Account Region":None,
    "Currency": "GOLD",
    "Mode": None,  # Will be "buy" or "sell"
}



# MetaTrader API setup
token = os.getenv('TOKEN')

def api_url(region,id):
    return f"https://mt-client-api-v1.{region}.agiliumtrade.ai/users/current/accounts/{id}/trade'"

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


async def get_user_credentials():
    """Prompt user for MT5 credentials."""
    console.print(Panel("[bold cyan]Please enter your MT5 account credentials[/bold cyan]"))
    login = Prompt.ask("[bold yellow]Login[/bold yellow]")
    password = Prompt.ask("[bold yellow]Password[/bold yellow]", password=True)
    server_name = Prompt.ask("[bold yellow]Server Name[/bold yellow]")

    if not login or not password or not server_name:
        console.print(Panel("[red]All fields are required. Please try again.[/red]"))
        return await get_user_credentials()

    return login, password, server_name


async def connect_to_mt5(login, password, server_name):
    """Connect to MetaTrader and return the account instance."""
    try:
        api = MetaApi(token)
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
        account_info["Account Id"]=account.id
        account_info["Account Region"] = account.region
        return connection
    except Exception as e:
        console.print(Panel(f"[red]Error connecting to MT5: {e}[/red]"))
        raise e


async def execute_trade(connection, strategy):
    """Perform a trade based on the selected strategy."""

    # print(account_info)
    if account_info["Mode"] not in ["buy", "sell"]:
        console.print(Panel("[red]Set a trading mode before executing trades![/red]"))
        await add_log("Set a trading mode before executing trades!", success=False)
        return
    
    try:
        symbol = account_info["Currency"]
        Mode  = {
    "buy":connection.create_market_buy_order,
    "sell":connection.create_market_sell_order
}
        trade_message = f"{strategy} in {account_info['Mode']} mode for {symbol}"
        actionType = Mode[account_info["Mode"]]

        volume = 0.2
        console.print(Panel(f"[cyan]Executing {strategy} in {account_info['Mode']} mode...[/cyan]"))

        if strategy == "30 pip TP":
            result = await actionType(symbol='GOLD', volume=volume, stop_loss=0.0, take_profit=3.0,
    options={"stopLossUnits":"RELATIVE_PIPS","takeProfitUnits":"RELATIVE_PIPS",'comment': 'comment'})
        elif strategy == "50 pip TP":
            result = await actionType(symbol=symbol, volume=volume, stop_loss=0.0, take_profit=5.0,
    options={"stopLossUnits":"RELATIVE_PIPS","takeProfitUnits":"RELATIVE_PIPS",'comment': 'comment'})
            
        elif strategy == "Trailing SL":
            result = await actionType('GOLD', volume, 5.0, 0.00, {
                "stopLossUnits":"RELATIVE_PIPS","takeProfitUnits":"RELATIVE_PIPS",'comment': 'comment',
    'trailingStopLoss': {
        'distance': {
            'distance': 20,
            'units': 'RELATIVE_POINTS'
        }
    }
})
        
        
        await add_log(f"Trade placed: {result}")
    except Exception as e:
        await add_log(f"Trade failed: {e}", success=False)


def display_account_info():
    """Display the account info panel."""
    table = Table(title="Account Information", expand=True)
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Account Name", account_info["Account Name"] or "Not Connected")
    table.add_row("Account id", account_info["Account Id"] or "Not Connected")
    table.add_row("Account Region", account_info["Account Region"] or "Not Connected")
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
            console.print("[bold red]Invalid option. Please try again.[/bold red]")


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
        display_logs()
        console.print(Panel("Trade Strategies Menu", style="bold cyan"))
        console.print("[1] 30 pip Take Profit")
        console.print("[2] 50 pip Take Profit")
        console.print("[3] Trailing Stop Loss")
        console.print("[P] Go Back")
        choice = Prompt.ask("Select a strategy").strip().lower()

        if choice == "1":
            console.print("option1 selected")
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
    login, password, server_name = await get_user_credentials()
    connection = await connect_to_mt5(login, password, server_name)
    await main_menu(connection)


if __name__ == "__main__":
    asyncio.run(run_app())
