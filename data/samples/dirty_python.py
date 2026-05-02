"""
Sample inefficient Python code with carbon-heavy patterns.
This file is intentionally written poorly for testing GreenCode Sentinel.
"""

import time
import requests


def inefficient_data_processing(data_list):
    """Example of nested loops and inefficient operations."""
    result = []
    
    # ISSUE: Triple nested loop - O(n³) complexity
    for i in range(len(data_list)):
        for j in range(len(data_list)):
            for k in range(len(data_list)):
                if data_list[i] + data_list[j] == data_list[k]:
                    result.append((data_list[i], data_list[j], data_list[k]))
    
    return result


def redundant_api_calls(user_ids):
    """Example of redundant API calls without caching."""
    user_data = []
    
    # ISSUE: Making API call for each user without caching
    for user_id in user_ids:
        response = requests.get(f"https://api.example.com/users/{user_id}")
        user_data.append(response.json())
        
        # ISSUE: Another redundant call for the same user
        profile = requests.get(f"https://api.example.com/users/{user_id}/profile")
        user_data[-1]['profile'] = profile.json()
    
    return user_data


def memory_inefficient_processing(large_dataset):
    """Example of poor memory management."""
    # ISSUE: Creating unnecessary copies of large data
    copy1 = large_dataset.copy()
    copy2 = large_dataset.copy()
    copy3 = large_dataset.copy()
    
    # ISSUE: Building large list in memory instead of using generator
    processed = []
    for item in large_dataset:
        processed.append(item * 2)
        processed.append(item * 3)
        processed.append(item * 4)
    
    return processed


def inefficient_string_concatenation(items):
    """Example of inefficient string operations."""
    result = ""
    
    # ISSUE: String concatenation in loop (creates new string each time)
    for item in items:
        result = result + str(item) + ","
    
    return result


def unnecessary_computation():
    """Example of redundant calculations."""
    results = []
    
    # ISSUE: Recalculating same value in loop
    for i in range(1000):
        for j in range(100):
            # This calculation is the same every iteration
            expensive_value = sum(range(1000)) * 2
            results.append(i * j * expensive_value)
    
    return results


def poor_database_queries(db_connection):
    """Example of N+1 query problem."""
    users = db_connection.execute("SELECT id FROM users").fetchall()
    
    user_details = []
    # ISSUE: N+1 query problem - should use JOIN
    for user in users:
        details = db_connection.execute(
            f"SELECT * FROM user_details WHERE user_id = {user[0]}"
        ).fetchone()
        user_details.append(details)
    
    return user_details


def inefficient_list_operations(data):
    """Example of inefficient list operations."""
    # ISSUE: Using list when set would be more efficient
    unique_items = []
    for item in data:
        if item not in unique_items:  # O(n) lookup in list
            unique_items.append(item)
    
    # ISSUE: Repeatedly extending list instead of pre-allocating
    result = []
    for i in range(10000):
        result.append(i)  # Causes multiple reallocations
    
    return unique_items, result


def blocking_io_operations(file_paths):
    """Example of blocking I/O without async."""
    contents = []
    
    # ISSUE: Synchronous I/O in loop - should use async or threading
    for path in file_paths:
        with open(path, 'r') as f:
            contents.append(f.read())
        time.sleep(0.1)  # Simulating slow I/O
    
    return contents


if __name__ == "__main__":
    # Test the inefficient functions
    test_data = list(range(100))
    
    print("Running inefficient operations...")
    result1 = inefficient_data_processing(test_data[:10])
    result2 = unnecessary_computation()
    result3 = inefficient_string_concatenation(test_data)
    
    print("Done! (But consumed way too much energy)")

# Made with Bob
