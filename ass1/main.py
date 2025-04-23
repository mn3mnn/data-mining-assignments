import tkinter as tk
from tkinter import filedialog, messagebox
from itertools import combinations

def load_data(file_path, percentage):
    transactions = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            transactions.append(set(line.strip().split(';')))
    transactions = transactions[:int(len(transactions) * percentage)]
    return transactions

def get_frequent_itemsets(transactions, min_support):
    """frequent itemsets using Apriori algorithm."""
    itemsets = {}
    candidates = set(frozenset([item]) for transaction in transactions for item in transaction)

    k = 1
    while candidates:
        item_counts = {item: 0 for item in candidates}
        for transaction in transactions:
            for item in candidates:
                if item.issubset(transaction):
                    item_counts[item] += 1

        num_transactions = len(transactions)
        itemsets[k] = {item: count / num_transactions for item, count in item_counts.items() if
                       count / num_transactions >= min_support}

        if not itemsets[k]:
            break

        candidates = set(frozenset(a | b) for a in itemsets[k] for b in itemsets[k] if len(a | b) == k + 1)
        k += 1

    return itemsets

def get_association_rules(frequent_itemsets, min_confidence):
    """association rules from frequent itemsets."""
    rules = []
    for k, itemset in frequent_itemsets.items():
        for item, support in itemset.items():
            for i in range(1, len(item)):
                for antecedent in combinations(item, i):
                    antecedent = frozenset(antecedent)
                    consequent = item - antecedent
                    antecedent_support = frequent_itemsets[len(antecedent)][antecedent]
                    confidence = support / antecedent_support
                    if confidence >= min_confidence:
                        rules.append((antecedent, consequent, support, confidence))
    return rules

def browse_file():
    file_path = filedialog.askopenfilename()
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(0, file_path)

def run_analysis():
    file_path = entry_file_path.get()
    percentage = float(entry_percentage.get())
    min_support = float(entry_min_support.get())
    min_confidence = float(entry_min_confidence.get())

    transactions = load_data(file_path, percentage)
    frequent_itemsets = get_frequent_itemsets(transactions, min_support)
    rules = get_association_rules(frequent_itemsets, min_confidence)

    text_frequent.delete(1.0, tk.END)
    text_rules.delete(1.0, tk.END)

    text_frequent.insert(tk.END, "Frequent Itemsets:\n")
    for k, itemset in frequent_itemsets.items():
        for item, support in itemset.items():
            text_frequent.insert(tk.END, f"{set(item)}: {support:.4f}\n")

    text_rules.insert(tk.END, "Association Rules:\n")
    for antecedent, consequent, support, confidence in rules:
        text_rules.insert(tk.END,
                          f"{set(antecedent)} -> {set(consequent)} (Support: {support:.4f}, Confidence: {confidence:.4f})\n")

# UI
root = tk.Tk()
root.title("Association Rule Mining")

tk.Label(root, text="Select File:").grid(row=0, column=0)
entry_file_path = tk.Entry(root, width=50)
entry_file_path.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

tk.Label(root, text="Data Percentage (ex: 0.5):").grid(row=1, column=0)
entry_percentage = tk.Entry(root)
entry_percentage.grid(row=1, column=1)

tk.Label(root, text="Min Support (ex: 0.04):").grid(row=2, column=0)
entry_min_support = tk.Entry(root)
entry_min_support.grid(row=2, column=1)

tk.Label(root, text="Min Confidence (ex: 0.02):").grid(row=3, column=0)
entry_min_confidence = tk.Entry(root)
entry_min_confidence.grid(row=3, column=1)

tk.Button(root, text="Run Analysis", command=run_analysis).grid(row=4, column=1)

# Output
tk.Label(root, text="Frequent Itemsets:").grid(row=5, column=0)
text_frequent = tk.Text(root, height=10, width=80)
text_frequent.grid(row=6, column=0, columnspan=3)

tk.Label(root, text="Association Rules:").grid(row=7, column=0)
text_rules = tk.Text(root, height=10, width=80)
text_rules.grid(row=8, column=0, columnspan=3)

root.mainloop()
