#include "optimizer.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

using namespace debt_optimizer;

// Simple JSON parser for our specific use case
std::string extract_json_value(const std::string& json, const std::string& key) {
    size_t key_pos = json.find("\"" + key + "\":");
    if (key_pos == std::string::npos) return "";
    
    size_t colon_pos = key_pos + key.length() + 2;
    size_t value_start = json.find_first_not_of(" \t", colon_pos + 1);
    
    if (json[value_start] == '"') {
        // String value
        size_t value_end = json.find('"', value_start + 1);
        return json.substr(value_start + 1, value_end - value_start - 1);
    } else if (json[value_start] == '[') {
        // Array value - return the whole array
        size_t bracket_count = 1;
        size_t value_end = value_start + 1;
        while (bracket_count > 0 && value_end < json.length()) {
            if (json[value_end] == '[') bracket_count++;
            else if (json[value_end] == ']') bracket_count--;
            value_end++;
        }
        return json.substr(value_start, value_end - value_start);
    } else {
        // Number value
        size_t value_end = json.find_first_of(",}]", value_start);
        return json.substr(value_start, value_end - value_start);
    }
}

std::vector<std::string> extract_json_array(const std::string& array_str) {
    std::vector<std::string> elements;
    if (array_str.empty() || array_str[0] != '[') return elements;
    
    size_t pos = 1;
    int brace_count = 0;
    std::string current;
    
    while (pos < array_str.length() && array_str[pos] != ']') {
        char c = array_str[pos];
        if (c == '{') brace_count++;
        else if (c == '}') brace_count--;
        
        current += c;
        
        if (brace_count == 0 && (c == ',' || c == ']')) {
            if (!current.empty() && current != ",") {
                elements.push_back(current);
            }
            current.clear();
        }
        pos++;
    }
    
    if (!current.empty()) {
        elements.push_back(current);
    }
    
    return elements;
}

Transaction parse_transaction(const std::string& trans_str) {
    Transaction t;
    t.from_user = extract_json_value(trans_str, "from_user");
    t.to_user = extract_json_value(trans_str, "to_user");
    std::string amount_str = extract_json_value(trans_str, "amount");
    t.amount = std::stod(amount_str);
    return t;
}

int main(int argc, char* argv[]) {
    // Check command line arguments
    if (argc != 2) {
        std::cerr << "Usage: " << argv[0] << " <input_file.json>" << std::endl;
        std::cerr << "Example: " << argv[0] << " input.json" << std::endl;
        return 1;
    }
    
    std::string input_file_path = argv[1];
    
    // Read input JSON file
    std::ifstream input_file(input_file_path);
    if (!input_file.is_open()) {
        std::cerr << "Error: Could not open input file '" << input_file_path << "'" << std::endl;
        return 1;
    }
    
    // Read entire file into string
    std::stringstream buffer;
    buffer << input_file.rdbuf();
    std::string input_json = buffer.str();
    input_file.close();
    
    // Validate input structure
    if (input_json.find("\"transactions\"") == std::string::npos) {
        std::cerr << "Error: Input JSON must contain a 'transactions' array." << std::endl;
        return 1;
    }
    
    // Extract transactions array
    std::string transactions_array = extract_json_value(input_json, "transactions");
    std::vector<std::string> transaction_strings = extract_json_array(transactions_array);
    
    // Parse transactions
    std::vector<Transaction> transactions;
    try {
        for (const auto& t_str : transaction_strings) {
            transactions.push_back(parse_transaction(t_str));
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: Failed to parse transactions: " << e.what() << std::endl;
        return 1;
    }
    
    std::cout << "Loaded " << transactions.size() << " transactions from " << input_file_path << std::endl;
    
    // Run optimization
    CashFlowOptimizer optimizer;
    OptimizationResult result = optimizer.optimize(transactions);
    
    // Generate output file path (same directory as input, with output.json suffix)
    std::string output_file_path;
    size_t last_slash = input_file_path.find_last_of("\\/");
    if (last_slash != std::string::npos) {
        output_file_path = input_file_path.substr(0, last_slash + 1) + "output.json";
    } else {
        output_file_path = "output.json";
    }
    
    // Write output JSON file
    std::ofstream output_file(output_file_path);
    if (!output_file.is_open()) {
        std::cerr << "Error: Could not create output file '" << output_file_path << "'" << std::endl;
        return 1;
    }
    
    output_file << result.to_json_string() << std::endl;
    output_file.close();
    
    // Print summary to console
    std::cout << "\n=== Optimization Summary ===" << std::endl;
    std::cout << "Original transactions: " << result.original_count << std::endl;
    std::cout << "Optimized transactions: " << result.optimized_count << std::endl;
    std::cout << "Transaction reduction: " << std::fixed << std::setprecision(2) 
              << result.reduction_percentage << "%" << std::endl;
    std::cout << "Total original amount: $" << std::fixed << std::setprecision(2) 
              << result.total_original_amount << std::endl;
    std::cout << "Total optimized amount: $" << std::fixed << std::setprecision(2) 
              << result.total_optimized_amount << std::endl;
    std::cout << "\nOutput written to: " << output_file_path << std::endl;
    
    return 0;
}
