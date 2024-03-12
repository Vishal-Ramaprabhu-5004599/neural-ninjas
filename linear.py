from datetime import datetime

from pulp import LpMaximize, LpProblem, LpVariable, lpSum, PULP_CBC_CMD
import pulp
import pandas as pd
import pulp

# Initialize the problem
def main():
    print("main")
    problem = LpProblem("Maximize_Total_Profit", LpMaximize)
    csv_file_path = './data/Data_max_min - output.csv'
    df = pd.read_csv(csv_file_path)
    print(df['no_of_units'])

    # Decision variables: Number of units for each SKU, cannot be negative
    # Using SKU names as variable identifiers for clarity
    unit_vars = {
        row['sku_id']: LpVariable(f'units_{row['sku_id']}', lowBound=row['min_units'], upBound=row['max_units'], cat='Integer')
        for index, row in df.iterrows()
    }
    # Objective Function: Maximize total profit
    problem += lpSum([row['profit_per_quantity'] * unit_vars[row['sku_id']] for index, row in df.iterrows()])

    # Calculate 10% of the budget for tolerance
    budget = calculate_total_spent(df)
    print("budget: " + str(budget))
    tolerance_limit = 0.001 * budget

    # Slack variable for tolerance
    slack = LpVariable("slack", lowBound=-tolerance_limit, upBound=tolerance_limit)

    # Objective Function: Maximize total profit
    problem += lpSum([row['lp'] * unit_vars[row['sku_id']] for index, row in df.iterrows()])+ slack == budget

    # Add constraints to ensure that optimal_units are within the min and max unit limits
    for index, row in df.iterrows():
        problem += unit_vars[row['sku_id']] >= row['min_units']
        problem += unit_vars[row['sku_id']] <= row['max_units']

    min_units_cost = sum(row['min_units'] * row['lp'] for index, row in df.iterrows())
    if min_units_cost > budget:
        raise ValueError("The budget is insufficient to cover the minimum required units for all SKUs.")

    print("starting optimization")

    # Solve the problem
    # pulp.solvers.PULP_CBC_CMD(maxSeconds=60).solve(problem)
    problem.solve(PULP_CBC_CMD(timeLimit=1))

    # Extract the solution
    optimal_units = {sku: var.value() for sku, var in unit_vars.items()}

    df['Optimal_Units'] = df['sku_id'].apply(lambda x: optimal_units.get(x, 0))
    df['Optimal_Profit_Per_SKU'] = df['profit_per_quantity'] * df['Optimal_Units']

    optimal_total_profit = sum(row['profit_per_quantity'] * optimal_units[row['sku_id']] for index, row in df.iterrows())
    current_date_time = datetime.now()
    updated_file_path = f'./output/output-{current_date_time}.csv'
    df.to_csv(updated_file_path, index=False)
    print("budget left:", calculate_new_spent(df)-calculate_total_spent(df))
    print("updated profit gitten:", (df['profit_per_quantity']*df['Optimal_Units']).sum()-(df['no_of_units'] * df['profit_per_quantity']).sum())
    print("Status:", pulp.LpStatus[problem.status])


def calculate_total_spent(df):
    return (df['no_of_units'] * df['lp']).sum()

def calculate_new_spent(df):
    return (df['Optimal_Units'] * df['lp']).sum()

if __name__ == "__main__":
    main()

