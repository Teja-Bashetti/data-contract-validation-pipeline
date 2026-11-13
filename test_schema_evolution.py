
from src.contract_validator import load_contract, compare_contracts

# Load original contract
old_contract = load_contract(
    "config/customer_contract_v1.json"
)

# Load breaking-change test contract
new_contract = load_contract(
    "config/customer_contract_breaking.json"
)

# Compare both contracts
result = compare_contracts(
    old_contract,
    new_contract
)

print("\n========== BREAKING CHANGE TEST ==========")

print("Old version:", result["old_version"])
print("New version:", result["new_version"])

print("\nBreaking changes:")
for change in result["breaking_changes"]:
    print("-", change)

print("\nNon-breaking changes:")
for change in result["non_breaking_changes"]:
    print("-", change)

print("\nIs compatible:", result["is_compatible"])
