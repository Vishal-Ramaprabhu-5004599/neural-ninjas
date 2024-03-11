import csv
import pulp


# Read input data from the CSV fil

def main():
    data = []
    with open('./data/Data_max_min - 30DayLpData.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            minUnits = int(int(row['no_of_units']) * 0.5)
            if minUnits <= 0:
                minUnits = 0.00001
            data.append({
                'warehouse_id': int(row['warehouse_id']),
                'sku': row['sku'],
                'profit_per_quantity': float(row['profit_per_quantity']),
                'lp': float(row['lp']),
                'no_of_units': int(int(row['no_of_units'])),
                'total_profit_per_sku': float(row['total_profit_per_sku']),
                'max_units': int(int(row['no_of_units']) * 1.5),
                'min_units': minUnits,
            })

    # Create a LP problem
    prob = pulp.LpProblem("Maximize_Total_Profit", pulp.LpMaximize)

    # Define decision variables
    variables = pulp.LpVariable.dicts("Quantity:", [(row['sku'], row['warehouse_id']) for row in data],
                                      lowBound=0, cat='Integer')

    # print("variables:", [row['profit_per_quantity'] * variables[(row['sku'],  row['warehouse_id'])] for row in data])
    # Add objective function
    prob += pulp.lpSum(
        [row['profit_per_quantity'] * variables[(row['sku'], row['warehouse_id'])] for row in data]), "Total_Profit"

    # Add constraints
    for row in data:
        prob += variables[(row['sku'], row['warehouse_id'])] >= row[
            'min_units'], f"Min_Units_{row['sku']}_{row['warehouse_id']}"
        prob += variables[(row['sku'], row['warehouse_id'])] <= row[
            'max_units'], f"Max_Units_{row['sku']}_{row['warehouse_id']}"

    # Add budget constraint
    prob += pulp.lpSum([row['lp'] * variables[(row['sku'], row['warehouse_id'])] for row in
                        data]) <= 1050933080, "Budget_Constraint"

    # Solve the problem
    prob.solve()

    # Calculate the sum of total profit

    # Write output data to a new CSV file
    output_data = []
    for v in prob.variables():
        print(v.name, v.varValue, v.name.split(':_')[1:])
        if v.varValue > 0:
            sku, warehouse_id = v.name.split(':_')[1].split(',_')
            output_data.append({
                'sku': sku,
                'warehouse_id': warehouse_id,
                'quantity': v.varValue,

            })

    with open('output.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['sku', 'warehouse_id', 'quantity'])
        writer.writeheader()
        writer.writerows(output_data)

    sum_total_profit = sum(
        row['profit_per_quantity'] * v.varValue for row, v in zip(data, prob.variables())
    )

    sum_total_budget = sum(
        row['lp'] * v.varValue for row, v in zip(data, prob.variables())
    )

    # Debugging Constraints
    for row in data:
        sku, warehouse_id = row['sku'], row['warehouse_id']
        decision_variable = variables[(sku, warehouse_id)]
        print(
            f"SKU: {sku}, Warehouse ID: {warehouse_id}, Decision Variable: {decision_variable.varValue}, Max Units: {row['max_units']}, Min units: {row['min_units']}")

    print("Sum of Total Profit:", sum_total_profit)
    print("Sum of Total budget:", sum_total_budget)


if __name__ == "__main__":
    main()
