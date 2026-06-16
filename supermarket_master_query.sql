CREATE DATABASE supermarket_db;
USE supermarket_db;
CREATE TABLE branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);
CREATE TABLE cashiers (
    cashier_id INT AUTO_INCREMENT PRIMARY KEY,
    cashier_name VARCHAR(100) NOT NULL,
    branch_id INT,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    city VARCHAR(50)
);
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    reorder_level INT NOT NULL
);
CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    branch_id INT,
    quantity INT NOT NULL,
    expiry_date DATE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    cashier_id INT,
    branch_id INT,
    sale_date DATE NOT NULL,
    sale_time TIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (cashier_id) REFERENCES cashiers(cashier_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
CREATE TABLE sale_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT,
    product_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
SHOW TABLES;
INSERT INTO branches (branch_name, location) VALUES
('Accra Central', 'Accra'),
('Kumasi Main', 'Kumasi'),
('Takoradi Branch', 'Takoradi');
INSERT INTO cashiers (cashier_name, branch_id) VALUES
('Ama', 1),
('Kofi', 1),
('Abena', 2),
('Kwame', 2),
('Akosua', 3),
('Yaw', 3);

INSERT INTO customers (customer_name, phone, city) VALUES
('Mensah', '0241234567', 'Accra'),
('James Osei', '0557654321', 'Kumasi'),
('Fiifi', '0201122334', 'Takoradi'),
('Sarah Miller', '0244556677', 'Accra'),
('Kojo', '0558899001', 'Kumasi'),
('David Chen', '0242233445', 'Accra'),
('Kweku', '0201234568', 'Takoradi'),
('Emily Johnson', '0557654322', 'Accra'),
('Kofi Agyeman', '0244556678', 'Kumasi'),
('Fatima Al-Hassan', '0558899002', 'Accra');

INSERT INTO products (product_name, category, price, reorder_level) VALUES
('Rice 5kg', 'Grains', 45.00, 20),
('Cooking Oil 1L', 'Oils', 28.00, 15),
('Sugar 1kg', 'Baking', 12.00, 25),
('Milk 500ml', 'Dairy', 8.50, 30),
('Bread', 'Bakery', 6.00, 20),
('Eggs 30pcs', 'Dairy', 35.00, 15),
('Tomato Paste 400g', 'Canned Goods', 9.00, 20),
('Sardines 155g', 'Canned Goods', 7.50, 25),
('Milo 400g', 'Beverages', 32.00, 15),
('Water 1.5L', 'Beverages', 4.00, 50),
('Detergent 1kg', 'Household', 22.00, 20),
('Toilet Roll 6pcs', 'Household', 18.00, 25),
('Chicken 1kg', 'Meat', 55.00, 10),
('Tuna Can 170g', 'Canned Goods', 11.00, 20),
('Noodles 70g', 'Grains', 3.50, 40);

INSERT INTO inventory (product_id, branch_id, quantity, expiry_date) VALUES
(1, 1, 50, '2027-01-01'),
(2, 1, 30, '2026-12-01'),
(3, 1, 45, '2027-03-01'),
(4, 1, 8, '2026-07-15'),
(5, 1, 25, '2026-06-20'),
(6, 1, 18, '2026-07-01'),
(7, 1, 12, '2026-12-01'),
(8, 1, 5, '2026-11-01'),
(9, 1, 22, '2027-01-01'),
(10, 1, 60, '2026-09-01'),
(11, 1, 15, '2027-06-01'),
(12, 1, 20, '2027-04-01'),
(13, 1, 8, '2026-06-25'),
(14, 1, 10, '2026-10-01'),
(15, 1, 35, '2026-08-01'),
(1, 2, 40, '2027-01-01'),
(2, 2, 12, '2026-12-01'),
(3, 2, 30, '2027-03-01'),
(4, 2, 25, '2026-07-15'),
(5, 2, 10, '2026-06-22'),
(6, 2, 20, '2026-07-01'),
(7, 2, 8, '2026-12-01'),
(8, 2, 40, '2026-11-01'),
(9, 2, 18, '2027-01-01'),
(10, 2, 75, '2026-09-01'),
(11, 2, 6, '2027-06-01'),
(12, 2, 30, '2027-04-01'),
(13, 2, 15, '2026-06-25'),
(14, 2, 22, '2026-10-01'),
(15, 2, 28, '2026-08-01'),
(1, 3, 35, '2027-01-01'),
(2, 3, 20, '2026-12-01'),
(3, 3, 18, '2027-03-01'),
(4, 3, 40, '2026-07-15'),
(5, 3, 15, '2026-06-21'),
(6, 3, 12, '2026-07-01'),
(7, 3, 25, '2026-12-01'),
(8, 3, 18, '2026-11-01'),
(9, 3, 30, '2027-01-01'),
(10, 3, 90, '2026-09-01'),
(11, 3, 10, '2027-06-01'),
(12, 3, 15, '2027-04-01'),
(13, 3, 20, '2026-06-25'),
(14, 3, 8, '2026-10-01'),
(15, 3, 22, '2026-08-01');

INSERT INTO sales (customer_id, cashier_id, branch_id, sale_date, sale_time) VALUES
(1, 1, 1, '2026-06-01', '08:30:00'),
(2, 1, 1, '2026-06-01', '09:15:00'),
(3, 3, 2, '2026-06-01', '10:00:00'),
(4, 2, 1, '2026-06-01', '11:30:00'),
(5, 4, 2, '2026-06-01', '13:00:00'),
(6, 5, 3, '2026-06-01', '14:30:00'),
(7, 2, 1, '2026-06-02', '09:00:00'),
(8, 3, 2, '2026-06-02', '10:30:00'),
(9, 6, 3, '2026-06-02', '12:00:00'),
(10, 1, 1, '2026-06-02', '15:00:00'),
(1, 4, 2, '2026-06-03', '08:45:00'),
(2, 5, 3, '2026-06-03', '10:15:00'),
(3, 1, 1, '2026-06-03', '11:00:00'),
(4, 6, 3, '2026-06-03', '13:30:00'),
(5, 2, 1, '2026-06-04', '09:30:00'),
(6, 3, 2, '2026-06-04', '11:00:00'),
(7, 5, 3, '2026-06-04', '14:00:00'),
(8, 1, 1, '2026-06-05', '08:00:00'),
(9, 4, 2, '2026-06-05', '10:00:00'),
(10, 6, 3, '2026-06-05', '12:30:00'),
(1, 2, 1, '2026-06-06', '09:00:00'),
(2, 3, 2, '2026-06-06', '11:30:00'),
(3, 5, 3, '2026-06-06', '13:00:00'),
(4, 1, 1, '2026-06-07', '10:00:00'),
(5, 6, 3, '2026-06-07', '14:00:00'),
(6, 4, 2, '2026-06-08', '09:15:00'),
(7, 1, 1, '2026-06-08', '11:00:00'),
(8, 3, 2, '2026-06-08', '13:30:00'),
(9, 5, 3, '2026-06-09', '08:30:00'),
(10, 2, 1, '2026-06-09', '10:45:00');

INSERT INTO sale_items (sale_id, product_id, quantity, unit_price) VALUES
(1, 1, 2, 45.00),
(1, 3, 1, 12.00),
(1, 10, 3, 4.00),
(2, 2, 1, 28.00),
(2, 5, 2, 6.00),
(2, 9, 1, 32.00),
(3, 4, 2, 8.50),
(3, 6, 1, 35.00),
(3, 15, 3, 3.50),
(4, 7, 2, 9.00),
(4, 8, 1, 7.50),
(4, 11, 1, 22.00),
(5, 1, 1, 45.00),
(5, 13, 2, 55.00),
(5, 10, 2, 4.00),
(6, 2, 2, 28.00),
(6, 3, 1, 12.00),
(6, 12, 1, 18.00),
(7, 5, 3, 6.00),
(7, 9, 1, 32.00),
(7, 14, 2, 11.00),
(8, 1, 1, 45.00),
(8, 4, 2, 8.50),
(8, 6, 1, 35.00),
(9, 2, 1, 28.00),
(9, 7, 2, 9.00),
(9, 10, 4, 4.00),
(10, 3, 2, 12.00),
(10, 8, 1, 7.50),
(10, 15, 5, 3.50),
(11, 1, 3, 45.00),
(11, 2, 1, 28.00),
(11, 5, 2, 6.00),
(12, 4, 1, 8.50),
(12, 9, 2, 32.00),
(12, 13, 1, 55.00),
(13, 6, 2, 35.00),
(13, 11, 1, 22.00),
(13, 14, 3, 11.00),
(14, 7, 1, 9.00),
(14, 8, 2, 7.50),
(14, 10, 3, 4.00),
(15, 1, 2, 45.00),
(15, 3, 1, 12.00),
(15, 12, 2, 18.00),
(16, 2, 1, 28.00),
(16, 5, 3, 6.00),
(16, 9, 1, 32.00),
(17, 4, 2, 8.50),
(17, 6, 1, 35.00),
(17, 15, 4, 3.50),
(18, 7, 1, 9.00),
(18, 8, 2, 7.50),
(18, 11, 1, 22.00),
(19, 1, 1, 45.00),
(19, 13, 1, 55.00),
(19, 10, 2, 4.00),
(20, 2, 2, 28.00),
(20, 3, 1, 12.00),
(20, 14, 2, 11.00),
(21, 5, 2, 6.00),
(21, 9, 1, 32.00),
(21, 12, 1, 18.00),
(22, 1, 3, 45.00),
(22, 4, 1, 8.50),
(22, 6, 2, 35.00),
(23, 2, 1, 28.00),
(23, 7, 2, 9.00),
(23, 10, 5, 4.00),
(24, 3, 1, 12.00),
(24, 8, 1, 7.50),
(24, 15, 3, 3.50),
(25, 1, 2, 45.00),
(25, 5, 1, 6.00),
(25, 11, 1, 22.00),
(26, 2, 2, 28.00),
(26, 9, 1, 32.00),
(26, 13, 1, 55.00),
(27, 4, 1, 8.50),
(27, 6, 2, 35.00),
(27, 14, 2, 11.00),
(28, 7, 1, 9.00),
(28, 8, 3, 7.50),
(28, 10, 4, 4.00),
(29, 1, 1, 45.00),
(29, 3, 2, 12.00),
(29, 12, 1, 18.00),
(30, 2, 1, 28.00),
(30, 5, 2, 6.00),
(30, 9, 1, 32.00);

SELECT COUNT(*) FROM branches;
SELECT COUNT(*) FROM cashiers;
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM inventory;
SELECT COUNT(*) FROM sales;
SELECT COUNT(*) FROM sale_items;


SELECT 
    b.branch_name,
    SUM(si.quantity * si.unit_price) AS total_revenue
FROM sales s
JOIN sale_items si ON s.sale_id = si.sale_id
JOIN branches b ON s.branch_id = b.branch_id
GROUP BY b.branch_name
ORDER BY total_revenue DESC;

SELECT 
    s.sale_id,
    s.sale_date,
    s.sale_time,
    c.customer_name,
    ca.cashier_name,
    b.branch_name,
    p.product_name,
    p.category,
    si.quantity,
    si.unit_price,
    (si.quantity * si.unit_price) AS total
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN cashiers ca ON s.cashier_id = ca.cashier_id
JOIN branches b ON s.branch_id = b.branch_id
JOIN sale_items si ON s.sale_id = si.sale_id
JOIN products p ON si.product_id = p.product_id
ORDER BY s.sale_date, s.sale_time;