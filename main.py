import time

# State variables
account_info = {
    "Account Name": None,
    "Currency": "XAUUSD",
    "Mode": None  # Will be "buy" or "sell"
}


# Placeholder for actual trading logic
def execute_trade(strategy, mode):
    print(f"\nExecuting {strategy} with mode: {mode.upper()}...")
    time.sleep(2)
    print(f"{strategy.capitalize()} ({mode.upper()}) completed successfully!\n")


# Display account info (stays on screen)
def display_account_info():
    print("=" * 50)
    print(f"Account Name: {account_info['Account Name']}")
    print(f"Currency: {account_info['Currency']}")
    print(f"Current Mode: {account_info['Mode'] if account_info['Mode'] else 'Not Set'}")
    print("=" * 50)


# Trading mode menu
def trading_mode():
    while True:
        print("\nTrading Mode:")
        print("1. Buy")
        print("2. Sell")
        print("P. Go Back")
        choice = input("Select a trading mode: ").strip().lower()

        if choice == "1":
            account_info["Mode"] = "buy"
            print("\nMode set to BUY.")
        elif choice == "2":
            account_info["Mode"] = "sell"
            print("\nMode set to SELL.")
        elif choice == "p":
            break
        else:
            print("\nInvalid option! Please try again.")
        time.sleep(1)


# Trade menu
def trade():
    if not account_info["Mode"]:
        print("\nSet a trading mode (buy/sell) before trading!")
        time.sleep(2)
        return

    while True:
        print("\nTrade Strategies:")
        print("1. 30 pip Take Profit")
        print("2. 50 pip Take Profit")
        print("3. Trailing Stop Loss")
        print("P. Go Back")
        choice = input("Select a strategy: ").strip().lower()

        if choice == "1":
            execute_trade("30 pip TP", account_info["Mode"])
        elif choice == "2":
            execute_trade("50 pip TP", account_info["Mode"])
        elif choice == "3":
            execute_trade("Trailing SL", account_info["Mode"])
        elif choice == "p":
            break
        else:
            print("\nInvalid option! Please try again.")
        time.sleep(1)


# Main menu
def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Trading Mode")
        print("2. Trade")
        print("E. Exit")
        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            trading_mode()
        elif choice == "2":
            trade()
        elif choice == "e":
            print("\nExiting the application. Goodbye!")
            break
        else:
            print("\nInvalid option! Please try again.")
        time.sleep(1)


# Main application
def run_app():
    print("\nWelcome to the Terminal Trading App!")
    account_info["Account Name"] = input("Enter your User ID: ").strip()
    print("\nConnected successfully!")

    while True:
        display_account_info()
        main_menu()


# Run the application
if __name__ == "__main__":
    run_app()
