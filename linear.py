import csv
import pulp
from datetime import datetime


def main():
    # Read input data from the CSV file
    budgetGiven = 105093308
    input_data = []
    with open('./data/Data_max_min - 30DayLpData.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            minUnits = max(int(int(row['no_of_units']) * 0.5), 1)  # Adjusted minUnits calculation
            input_data.append({
                'warehouse_id': int(row['warehouse_id']),
                'sku': row['sku'],
                'profit_per_quantity': float(row['profit_per_quantity']),
                'lp': float(row['lp']),
                'no_of_units': int(row['no_of_units']),  # Simplified conversion
                'total_profit_per_sku': float(row['total_profit_per_sku']),
                'max_units': int(int(row['no_of_units']) * 1.5),
                'min_units': minUnits,
            })

    # Create a LP problem
    prob = pulp.LpProblem("Maximize_Total_Profit", pulp.LpMaximize)

    # Define decision variables
    variables = pulp.LpVariable.dicts("Quantity:", [(row['sku'], row['warehouse_id']) for row in input_data],
                                      lowBound=0, cat='Integer')

    # Add objective function
    prob += pulp.lpSum([row['profit_per_quantity'] * variables[(row['sku'], row['warehouse_id'])] for row in input_data]), "Total_Profit"

    # Add constraints
    for row in input_data:
        prob += variables[(row['sku'], row['warehouse_id'])] >= row['min_units'], f"Min_Units_{row['sku']}_{row['warehouse_id']}"
        prob += variables[(row['sku'], row['warehouse_id'])] <= row['max_units'], f"Max_Units_{row['sku']}_{row['warehouse_id']}"

    # Add budget constraint
    prob += pulp.lpSum([row['lp'] * variables[(row['sku'], row['warehouse_id'])] for row in input_data]) <= budgetGiven, "Budget_Constraint"

    # Solve the problem
    prob.solve()

    sum_total_profit = sum(row['profit_per_quantity'] * v.varValue for row, v in zip(input_data, prob.variables()))
    sum_total_budget = sum(row['lp'] * v.varValue for row, v in zip(input_data, prob.variables()))

    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_file = f'./output/output_{current_datetime}.csv'


    # Write input data and then append the output data to output.csv
    # Write input data and then append the output data to output.csv
    with open(output_file, 'a', newline='') as file:
        fieldnames = ['sku', 'warehouse_id', 'lp', 'no_of_units', 'max_units', 'min_units', 'quantity']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Write input data
        if file.tell() == 0:  # Check if file is empty
            writer.writeheader()
        for row, v in zip(input_data, prob.variables()):
            sku, warehouse_id = row['sku'], row['warehouse_id']
            writer.writerow({
                'sku': sku,
                'warehouse_id': warehouse_id,
                'lp': row['lp'],
                'no_of_units': row['no_of_units'],
                'max_units': row['max_units'],
                'min_units': row['min_units'],
                'quantity':variables[(sku, warehouse_id)].varValue,  # Output quantity if it's greater than 0
            })
        writer.writerow({
            'sku': 0,
            'warehouse_id': f'give-budget:{budgetGiven}, total-budget-used:{sum_total_budget}, total-profit-got:{sum_total_profit},',
        })


    # Debugging Constraints
    for row in input_data:
        sku, warehouse_id = row['sku'], row['warehouse_id']
        decision_variable = variables[(sku, warehouse_id)]
        print(f"SKU: {sku}, Warehouse ID: {warehouse_id}, Decision Variable: {decision_variable.varValue}, Max Units: {row['max_units']}, Min units: {row['min_units']}")

    print("Sum of Total Profit:", sum_total_profit)
    print("Sum of Total budget:", sum_total_budget)


if __name__ == "__main__":
    main()
