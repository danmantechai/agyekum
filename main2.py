from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
import time

# State variables
account_info = {
    "Account Name": None,
    "Currency": "XAUUSD",
    "Mode": None  # Will be "buy" or "sell"
}

console = Console()

# Placeholder for actual trading logic
def execute_trade(strategy, mode):
    console.print(Panel(f"Executing {strategy} in mode: [bold green]{mode.upper()}[/bold green]..."))
    time.sleep(2)
    console.print(Panel(f"[bold green]{strategy.capitalize()} ({mode.upper()}) completed successfully![/bold green]"))


# Display account info (always visible)
def display_account_info():
    table = Table(title="Account Information")
    table.add_column("Field", style="bold")
    table.add_column("Value")
    table.add_row("Account Name", account_info["Account Name"] or "Not Connected")
    table.add_row("Currency", account_info["Currency"])
    table.add_row("Current Mode", account_info["Mode"] or "Not Set")
    console.print(table)


# Trading mode menu
def trading_mode():
    while True:
        console.clear()
        display_account_info()
        console.print(Panel("Trading Mode Menu", style="bold cyan"))
        console.print("[1] Buy")
        console.print("[2] Sell")
        console.print("[P] Go Back")
        choice = Prompt.ask("Select a trading mode").strip().lower()

        if choice == "1":
            account_info["Mode"] = "buy"
            console.print(Panel("[bold green]Mode set to BUY.[/bold green]"))
        elif choice == "2":
            account_info["Mode"] = "sell"
            console.print(Panel("[bold red]Mode set to SELL.[/bold red]"))
        elif choice == "p":
            break
        else:
            console.print("[bold red]Invalid option! Please try again.[/bold red]")
        time.sleep(1)


# Trade menu
def trade():
    if not account_info["Mode"]:
        console.print(Panel("[bold red]Set a trading mode (buy/sell) before trading![/bold red]"))
        time.sleep(2)
        return

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
            execute_trade("30 pip TP", account_info["Mode"])
        elif choice == "2":
            execute_trade("50 pip TP", account_info["Mode"])
        elif choice == "3":
            execute_trade("Trailing SL", account_info["Mode"])
        elif choice == "p":
            break
        else:
            console.print("[bold red]Invalid option! Please try again.[/bold red]")
        time.sleep(1)


# Main menu
def main_menu():
    while True:
        console.clear()
        display_account_info()
        console.print(Panel("Main Menu", style="bold cyan"))
        console.print("[1] Trading Mode")
        console.print("[2] Trade")
        console.print("[E] Exit")
        choice = Prompt.ask("Select an option").strip().lower()

        if choice == "1":
            trading_mode()
        elif choice == "2":
            trade()
        elif choice == "e":
            console.print(Panel("[bold green]Exiting the application. Goodbye![/bold green]"))
            break
        else:
            console.print("[bold red]Invalid option! Please try again.[/bold red]")
        time.sleep(1)


# Main application
def run_app():
    console.print(Panel("[bold magenta]Welcome to the Terminal Trading App![/bold magenta]", style="bold cyan"))
    account_info["Account Name"] = Prompt.ask("Enter your User ID").strip()
    console.print(Panel("[bold green]Connected successfully![/bold green]"))

    while True:
        main_menu()


# Run the application
if __name__ == "__main__":
    run_app()
