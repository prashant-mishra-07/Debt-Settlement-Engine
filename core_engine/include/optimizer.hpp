#ifndef OPTIMIZER_HPP
#define OPTIMIZER_HPP

#include <string>
#include <vector>
#include <map>
#include <queue>
#include <sstream>
#include <iomanip>

namespace debt_optimizer {

// Transaction structure
struct Transaction {
    std::string from_user;
    std::string to_user;
    double amount;
    
    Transaction() : amount(0.0) {}
    Transaction(const std::string& from, const std::string& to, double amt)
        : from_user(from), to_user(to), amount(amt) {}
    
    // Convert to JSON string
    std::string to_json_string() const {
        std::ostringstream oss;
        oss << "{\"from_user\":\"" << from_user 
            << "\",\"to_user\":\"" << to_user 
            << "\",\"amount\":" << std::fixed << std::setprecision(2) << amount << "}";
        return oss.str();
    }
};

// Optimization result structure
struct OptimizationResult {
    std::vector<Transaction> optimized_transactions;
    int original_count;
    int optimized_count;
    double total_original_amount;
    double total_optimized_amount;
    double reduction_percentage;
    std::string status;
    
    OptimizationResult() 
        : original_count(0), optimized_count(0), 
          total_original_amount(0.0), total_optimized_amount(0.0),
          reduction_percentage(0.0), status("success") {}
    
    // Convert to JSON string
    std::string to_json_string() const {
        std::ostringstream oss;
        oss << "{\"optimized_transactions\":[";
        for (size_t i = 0; i < optimized_transactions.size(); ++i) {
            if (i > 0) oss << ",";
            oss << optimized_transactions[i].to_json_string();
        }
        oss << "],\"original_count\":" << original_count
            << ",\"optimized_count\":" << optimized_count
            << ",\"total_original_amount\":" << std::fixed << std::setprecision(2) << total_original_amount
            << ",\"total_optimized_amount\":" << std::fixed << std::setprecision(2) << total_optimized_amount
            << ",\"reduction_percentage\":" << std::fixed << std::setprecision(2) << reduction_percentage
            << ",\"status\":\"" << status << "\"}";
        return oss.str();
    }
};

// Cash Flow Optimizer class
class CashFlowOptimizer {
private:
    std::map<std::string, double> net_balances;
    
    // Calculate net balance for each person
    void calculate_net_balances(const std::vector<Transaction>& transactions);
    
    // Build priority queues for creditors and debtors
    void build_priority_queues(
        std::priority_queue<std::pair<double, std::string>>& creditors,
        std::priority_queue<std::pair<double, std::string>>& debtors
    );
    
public:
    CashFlowOptimizer() = default;
    
    // Main optimization function
    OptimizationResult optimize(const std::vector<Transaction>& transactions);
    
    // Helper function to validate transactions
    static bool validate_transactions(const std::vector<Transaction>& transactions);
};

} // namespace debt_optimizer

#endif // OPTIMIZER_HPP
