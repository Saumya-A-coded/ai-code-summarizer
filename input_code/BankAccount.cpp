#include <iostream>
#include <string>
#include <vector>

// Use the standard namespace for cout, string, etc.
using namespace std;

/**
 * @class BankAccount
 * @brief Manages a simple bank account with a balance.
 */
class BankAccount {
private:
    string accountHolder;
    double balance;

public:
    /**
     * @brief Constructs a new BankAccount object.
     * @param owner The name of the account holder.
     * @param initialBalance The starting balance.
     */
    BankAccount(string owner, double initialBalance) {
        accountHolder = owner;
        balance = initialBalance;
    }

    /**
     * @brief Deposits a specified amount into the account.
     * @param amount The amount to deposit. Must be positive.
     */
    void deposit(double amount) {
        if (amount > 0) {
            balance += amount;
            cout << "Deposited: $" << amount << endl;
        } else {
            cout << "Deposit amount must be positive." << endl;
        }
    }

    /**
     * @brief Withdraws a specified amount from the account.
     * @param amount The amount to withdraw. Cannot exceed balance.
     */
    void withdraw(double amount) {
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            cout << "Withdrew: $" << amount << endl;
        } else {
            cout << "Invalid withdrawal amount or insufficient funds." << endl;
        }
    }

    /**
     * @brief Retrieves the current account balance.
     * @return The current balance.
     */
    double getBalance() const {
        return balance;
    }
};

/**
 * @brief Prints a standard welcome message to the console.
 */
void printWelcomeMessage() {
    cout << "Welcome to the Simple Banking System!" << endl;
}