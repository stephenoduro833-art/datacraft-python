CREATE DATABASE retailiq;
USE retailiq;
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    pin VARCHAR(10) NOT NULL,
    role ENUM('cashier', 'manager') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    reorder_level INT DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    quantity INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
CREATE TABLE sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    cashier_id INT NOT NULL,
    sale_date DATE NOT NULL,
    sale_time TIME NOT NULL,
    payment_method ENUM('cash', 'momo', 'card') NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    is_voided BOOLEAN DEFAULT FALSE,
    voided_by INT NULL,
    void_reason VARCHAR(255) NULL,
    FOREIGN KEY (cashier_id) REFERENCES users(user_id),
    FOREIGN KEY (voided_by) REFERENCES users(user_id)
);
CREATE TABLE sale_items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
CREATE TABLE stock_movements (
    movement_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    movement_type ENUM('stock_in', 'adjustment', 'sale') NOT NULL,
    quantity INT NOT NULL,
    reason VARCHAR(255) NULL,
    recorded_by INT NOT NULL,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (recorded_by) REFERENCES users(user_id)
);
CREATE TABLE activity_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
SHOW TABLES;
INSERT INTO users (full_name, pin, role) VALUES
('Kwame Mensah', '1234', 'manager'),
('Ama Serwaa', '5678', 'cashier'),
('Kofi Boateng', '9012', 'cashier');

INSERT INTO products (product_name, category, selling_price, cost_price, reorder_level) VALUES
('Rice 5kg', 'Grains', 45.00, 32.00, 20),
('Cooking Oil 1L', 'Oils', 28.00, 19.00, 15),
('Sugar 1kg', 'Baking', 12.00, 8.00, 25),
('Milk 500ml', 'Dairy', 8.50, 5.50, 30),
('Bread', 'Bakery', 6.00, 3.50, 20),
('Eggs 30pcs', 'Dairy', 35.00, 24.00, 15),
('Milo 400g', 'Beverages', 32.00, 22.00, 15),
('Water 1.5L', 'Beverages', 4.00, 1.50, 50),
('Detergent 1kg', 'Household', 22.00, 14.00, 20),
('Noodles 70g', 'Grains', 3.50, 1.80, 40);

INSERT INTO inventory (product_id, quantity) VALUES
(1, 50),
(2, 30),
(3, 45),
(4, 25),
(5, 40),
(6, 20),
(7, 35),
(8, 100),
(9, 28),
(10, 60);

SELECT * FROM users;
SELECT * FROM products;
SELECT * FROM inventory;