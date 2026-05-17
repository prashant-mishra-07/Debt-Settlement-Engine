#include "optimizer.hpp"
#include <iostream>
#include <cmath>
#include <algorithm>

namespace debt_optimizer {

void CashFlowOptimizer::calculate_net_balances(const std::vector<Transaction>& transactions) {
    net_balances.clear();
    
    for (const auto& t : transactions) {
        // Person who owes money (decreases their balance)
        net_balances[t.from_user] -= t.amount;
        
        // Person who is owed money (increases their balance)
        net_balances[t.to_user] += t.amount;
    }
    
    // Remove people with zero balance
    for (auto it = net_balances.begin(); it != net_balances.end(); ) {
        if (std::abs(it->second) < 0.001) {  // Floating point comparison
            it = net_balances.erase(it);
        } else {
            ++it;
        }
    }
}

void CashFlowOptimizer::build_priority_queues(
    std::priority_queue<std::pair<double, std::string>>& creditors,
    std::priority_queue<std::pair<double, std::string>>& debtors) {
    
    creditors = std::priority_queue<std::pair<double, std::string>>();
    debtors = std::priority_queue<std::pair<double, std::string>>();
    
    for (auto it = net_balances.begin(); it != net_balances.end(); ++it) {
        const std::string& person = it->first;
        double balance = it->second;
        if (balance > 0) {
            // Creditor (is owed money)
            creditors.push(std::make_pair(balance, person));
        } else if (balance < 0) {
            // Debtor (owes money) - store as positive for max-heap
            debtors.push(std::make_pair(-balance, person));
        }
    }
}

OptimizationResult CashFlowOptimizer::optimize(const std::vector<Transaction>& transactions) {
    OptimizationResult result;
    result.original_count = transactions.size();
    
    // Calculate total original amount
    for (const auto& t : transactions) {
        result.total_original_amount += t.amount;
    }
    
    // Validate transactions
    if (!validate_transactions(transactions)) {
        result.status = "error";
        return result;
    }
    
    // Calculate net balances
    calculate_net_balances(transactions);
    
    // If no net balances, all debts are already settled
    if (net_balances.empty()) {
        result.optimized_count = 0;
        result.total_optimized_amount = 0.0;
        result.reduction_percentage = 100.0;
        return result;
    }
    
    // Build priority queues
    std::priority_queue<std::pair<double, std::string>> creditors;
    std::priority_queue<std::pair<double, std::string>> debtors;
    build_priority_queues(creditors, debtors);
    
    // Greedy optimization: match largest debtor with largest creditor
    while (!creditors.empty() && !debtors.empty()) {
        std::pair<double, std::string> debtor_pair = debtors.top();
        std::pair<double, std::string> creditor_pair = creditors.top();
        
        double debtor_amount = debtor_pair.first;
        std::string debtor = debtor_pair.second;
        double creditor_amount = creditor_pair.first;
        std::string creditor = creditor_pair.second;
        
        debtors.pop();
        creditors.pop();
        
        // Calculate settlement amount
        double settle_amount = std::min(debtor_amount, creditor_amount);
        
        // Create optimized transaction
        result.optimized_transactions.emplace_back(debtor, creditor, settle_amount);
        result.total_optimized_amount += settle_amount;
        
        // Update remaining amounts
        double remaining_debtor = debtor_amount - settle_amount;
        double remaining_creditor = creditor_amount - settle_amount;
        
        // Push back if there's remaining balance
        if (remaining_debtor > 0.001) {
            debtors.push(std::make_pair(remaining_debtor, debtor));
        }
        if (remaining_creditor > 0.001) {
            creditors.push(std::make_pair(remaining_creditor, creditor));
        }
    }
    
    result.optimized_count = result.optimized_transactions.size();
    
    // Calculate reduction percentage
    if (result.original_count > 0) {
        result.reduction_percentage = 
            ((result.original_count - result.optimized_count) * 100.0) / result.original_count;
    }
    
    return result;
}

bool CashFlowOptimizer::validate_transactions(const std::vector<Transaction>& transactions) {
    for (const auto& t : transactions) {
        // Check for valid amount
        if (t.amount <= 0) {
            std::cerr << "Invalid transaction amount: " << t.amount << " for " 
                      << t.from_user << " -> " << t.to_user << std::endl;
            return false;
        }
        
        // Check for empty names
        if (t.from_user.empty() || t.to_user.empty()) {
            std::cerr << "Empty user name in transaction" << std::endl;
            return false;
        }
        
        // Check for self-transaction
        if (t.from_user == t.to_user) {
            std::cerr << "Self-transaction detected: " << t.from_user << std::endl;
            return false;
        }
    }
    return true;
}

} // namespace debt_optimizer
