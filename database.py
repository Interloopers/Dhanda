# database.py
import pymongo
from collections import defaultdict
import pandas as pd

class InventoryDB:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="inventoryDB", collection_name="inventory"):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def initialize_data(self):
        '''Initializes the inventory collection with some sample data.'''
        if self.collection.count_documents({}) == 0:
            sample_data = [ 
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


            self.collection.insert_many(sample_data)

    def load_data(self):
        '''Loads the inventory data from the MongoDB collection.'''
        data = list(self.collection.find({}))
        return pd.DataFrame(data).drop('_id', axis=1) if data else pd.DataFrame()

    def assign_new_id(self, df):
        '''Assigns a new ID based on the highest existing ID.'''
        return int(df['id'].max()) + 1 if not df.empty and df['id'].notna().any() else 1

    def update_data(self, df, changes):
        '''Updates the inventory data in the MongoDB collection.'''
        # Process edited rows
        for i, delta in changes.get('edited_rows', {}).items():
            if 'id' in df.columns and pd.notna(df.loc[i, 'id']):
                item_id = int(df.loc[i, 'id'])
                update_dict = {**df.iloc[i].to_dict(), **delta}
                if self.collection.find_one({'id': item_id}):
                    self.collection.update_one({'id': item_id}, {"$set": update_dict})

        # Process added rows
        for row in changes.get('added_rows', []):
            new_id = self.assign_new_id(df)
            row['id'] = new_id
            self.collection.insert_one(defaultdict(lambda: None, row))

        # Process deleted rows
        for i in changes.get('deleted_rows', []):
            if 'id' in df.columns and pd.notna(df.loc[i, 'id']):
                item_id = int(df.loc[i, 'id'])
                if self.collection.find_one({'id': item_id}):
                    self.collection.delete_one({'id': item_id})
    def add_item(self, item):
        '''Adds a new item to the database.'''
        max_id = self.collection.find_one(sort=[('id', -1)])  # Get the document with the highest ID
        new_id = max_id['id'] + 1 if max_id else 1  # Increment by 1 or set to 1 if collection is empty

    # Assign the new ID to the item
        item['id'] = new_id
        # Ensure you have a collection named 'inventory' or whatever you are using
        collection = self.client['inventoryDB']['inventory']
        collection.insert_one(item)  # Use insert_one to add the new item

