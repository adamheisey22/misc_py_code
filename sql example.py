import sqlite3

# Create a connection to a new SQLite database in memory
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL
)''')
cursor.execute('''
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    customer_id INTEGER,
    date TEXT,
    quantity INTEGER,
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
)''')
cursor.execute('''
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    city TEXT
)''')

# Insert data into tables
products = [(1, 'Laptop', 1200), (2, 'Mouse', 25), (3, 'Keyboard', 75)]
customers = [(1, 'Alice Smith', 'New York'), (2, 'Bob Johnson', 'Los Angeles'), (3, 'Carol Danvers', 'Chicago')]
sales = [
    (1, 1, 1, '2023-04-10', 2),
    (2, 2, 1, '2023-04-11', 1),
    (3, 3, 2, '2023-04-12', 3),
    (4, 1, 3, '2023-04-13', 1),
    (5, 2, 2, '2023-04-14', 2),
    (6, 2, 3, '2023-04-15', 1),
    (7, 3, 1, '2023-04-16', 1)
]
cursor.executemany('INSERT INTO products VALUES (?, ?, ?)', products)
cursor.executemany('INSERT INTO customers VALUES (?, ?, ?)', customers)
cursor.executemany('INSERT INTO sales VALUES (?, ?, ?, ?, ?)', sales)

# Aggregation query
query1 = '''
SELECT p.name, SUM(s.quantity * p.price) AS total_sales
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id;
'''
# Average query
query2 = '''
SELECT p.name, AVG(s.quantity) AS avg_quantity
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id;
'''
# Disaggregation query
query3 = '''
SELECT c.city, p.name, SUM(s.quantity) AS total_quantity
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN products p ON s.product_id = p.product_id
GROUP BY c.city, p.product_id;
'''

# Execute and print the queries
print("Total Sales Per Product:")
print(cursor.execute(query1).fetchall())
print("\nAverage Sales Quantity Per Product:")
print(cursor.execute(query2).fetchall())
print("\nSales Breakdown by Customer City:")
print(cursor.execute(query3).fetchall())

# Close the connection
conn.close()
