import pandas as pd
import numpy as np

# Parameters for the dataset
num_items = 12  # Number of items to simulate

# Create item details
items= [ 
        {'id': 1, 'item_name': 'Bottled Water (1L)', 'price': 25.00, 'units_sold': 150, 'units_left': 25, 'cost_price': 10.00, 'reorder_point': 20, 'description': 'Hydrating bottled water'},
        {'id': 2, 'item_name': 'Soft Drink (300ml)', 'price': 40.00, 'units_sold': 120, 'units_left': 5, 'cost_price': 15.00, 'reorder_point': 10, 'description': 'Chilled carbonated soft drink'},
        {'id': 3, 'item_name': 'Energy Drink (250ml)', 'price': 60.00, 'units_sold': 30, 'units_left': 15, 'cost_price': 25.00, 'reorder_point': 5, 'description': 'High-caffeine energy drink'},
        {'id': 4, 'item_name': 'Fresh Coffee (hot, large)', 'price': 80.00, 'units_sold': 50, 'units_left': 20, 'cost_price': 30.00, 'reorder_point': 5, 'description': 'Freshly brewed hot coffee'},
        {'id': 5, 'item_name': 'Fruit Juice (200ml)', 'price': 50.00, 'units_sold': 40, 'units_left': 12, 'cost_price': 18.00, 'reorder_point': 5, 'description': 'Refreshing fruit juice blend'},
        {'id': 6, 'item_name': 'Biscuits (Pack of 10)', 'price': 35.00, 'units_sold': 85, 'units_left': 30, 'cost_price': 12.00, 'reorder_point': 15, 'description': 'Pack of delicious biscuits'},
        {'id': 7, 'item_name': 'Chips (50g)', 'price': 30.00, 'units_sold': 75, 'units_left': 20, 'cost_price': 10.00, 'reorder_point': 10, 'description': 'Crunchy potato chips'},
        {'id': 8, 'item_name': 'Instant Noodles (Single Pack)', 'price': 20.00, 'units_sold': 100, 'units_left': 50, 'cost_price': 7.00, 'reorder_point': 20, 'description': 'Quick-cooking instant noodles'},
        {'id': 9, 'item_name': 'Chocolate Bar (50g)', 'price': 40.00, 'units_sold': 60, 'units_left': 25, 'cost_price': 15.00, 'reorder_point': 8, 'description': 'Delicious chocolate bar'},
        {'id': 10, 'item_name': 'Coconut Water (500ml)', 'price': 60.00, 'units_sold': 35, 'units_left': 10, 'cost_price': 20.00, 'reorder_point': 5, 'description': 'Natural coconut water'},
        {'id': 11, 'item_name': 'Pulses (1kg)', 'price': 120.00, 'units_sold': 20, 'units_left': 18, 'cost_price': 80.00, 'reorder_point': 5, 'description': 'Various types of pulses'},
        {'id': 12, 'item_name': 'Rice (1kg)', 'price': 80.00, 'units_sold': 15, 'units_left': 12, 'cost_price': 45.00, 'reorder_point': 5, 'description': 'Premium quality rice'},
    ]

# Generate a fake dataset
data = {
    'id': [],
    'item_name': [],
    'price': [],
    'units_sold': [],
    'units_left': [],
    'cost_price': [],
    'reorder_point': [],
    'description': []
}

for idx, item in enumerate(items):
    item_id = idx + 1  # Generate IDs starting from 1
    base_sales = np.random.randint(10, 50)  # Base sales per day
    # Simulating sales and ensuring it does not go below 0
    sales = np.maximum(base_sales + np.random.randint(-5, 5), 0) * 30  # Simulating monthly sales
    units_left = np.maximum(sales - np.random.randint(1, 10), 0)  # Ensure units left doesn't go negative

    # Fill the data
    data['id'].append(item_id)
    data['item_name'].append(item['item_name'])
    data['price'].append(item['price'])
    data['units_sold'].append(sales)
    data['units_left'].append(units_left)
    data['cost_price'].append(item['cost_price'])
    data['reorder_point'].append(item['reorder_point'])
    data['description'].append(item['description'])

# Create a DataFrame
fake_inventory_df = pd.DataFrame(data)

# Display the generated dataset
print(fake_inventory_df)
