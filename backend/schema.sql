CREATE TABLE organizations (
	id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	business_type VARCHAR(100), 
	currency VARCHAR(20), 
	alert_threshold_percent FLOAT, 
	address VARCHAR(255), 
	phone VARCHAR(50), 
	email VARCHAR(100), 
	created_at DATETIME, 
	PRIMARY KEY (id)
);
CREATE INDEX ix_organizations_id ON organizations (id);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	role VARCHAR(50), 
	password_hash VARCHAR(255), 
	is_active BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_users_id ON users (id);
CREATE TABLE products (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	name VARCHAR(255) NOT NULL, 
	sku VARCHAR(50), 
	category VARCHAR(100) NOT NULL, 
	unit VARCHAR(50) NOT NULL, 
	unit_ratio FLOAT, 
	package_quantity FLOAT, 
	package_unit VARCHAR(50), 
	current_stock FLOAT, 
	minimum_stock FLOAT, 
	description TEXT, 
	is_active BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_products_name ON products (name);
CREATE INDEX ix_products_id ON products (id);
CREATE INDEX ix_products_sku ON products (sku);
CREATE INDEX ix_products_category ON products (category);
CREATE TABLE suppliers (
	id INTEGER NOT NULL, 
	organization_id INTEGER, 
	name VARCHAR(255) NOT NULL, 
	contact_name VARCHAR(255), 
	phone VARCHAR(50), 
	email VARCHAR(100), 
	address VARCHAR(255), 
	notes TEXT, 
	delivery_cost FLOAT, 
	minimum_order_amount FLOAT, 
	source_type VARCHAR(50), 
	is_global BOOLEAN, 
	is_demo BOOLEAN, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_suppliers_name ON suppliers (name);
CREATE INDEX ix_suppliers_id ON suppliers (id);
CREATE TABLE import_batches (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	file_name VARCHAR(255) NOT NULL, 
	import_type VARCHAR(50) NOT NULL, 
	status VARCHAR(20), 
	rows_total INTEGER, 
	rows_imported INTEGER, 
	rows_skipped INTEGER, 
	error_summary TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE
);
CREATE INDEX ix_import_batches_id ON import_batches (id);
CREATE TABLE supplier_offers (
	id INTEGER NOT NULL, 
	organization_id INTEGER, 
	product_id INTEGER NOT NULL, 
	supplier_id INTEGER NOT NULL, 
	offered_price FLOAT NOT NULL, 
	unit VARCHAR(50) NOT NULL, 
	package_quantity FLOAT, 
	minimum_order_quantity FLOAT, 
	delivery_cost FLOAT, 
	valid_until DATE, 
	updated_at DATETIME, 
	source_type VARCHAR(50), 
	price_source VARCHAR(50), 
	is_demo BOOLEAN, 
	is_active BOOLEAN, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE
);
CREATE INDEX ix_supplier_offers_id ON supplier_offers (id);
CREATE TABLE purchase_orders (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	order_number VARCHAR(50) NOT NULL, 
	supplier_id INTEGER NOT NULL, 
	order_date DATE NOT NULL, 
	status VARCHAR(20), 
	subtotal_amount FLOAT, 
	delivery_cost FLOAT, 
	total_amount FLOAT, 
	notes TEXT, 
	created_by_user_id INTEGER, 
	received_at DATETIME, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE RESTRICT, 
	FOREIGN KEY(created_by_user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_purchase_orders_id ON purchase_orders (id);
CREATE INDEX ix_purchase_orders_order_number ON purchase_orders (order_number);
CREATE INDEX ix_purchase_orders_order_date ON purchase_orders (order_date);
CREATE TABLE inventory_movements (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	movement_type VARCHAR(30) NOT NULL, 
	quantity FLOAT NOT NULL, 
	unit VARCHAR(50) NOT NULL, 
	previous_stock FLOAT, 
	resulting_stock FLOAT, 
	reason VARCHAR(255) NOT NULL, 
	reference_id VARCHAR(100), 
	user_id INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_inventory_movements_id ON inventory_movements (id);
CREATE TABLE notifications (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	description TEXT NOT NULL, 
	severity VARCHAR(20), 
	notification_type VARCHAR(50) NOT NULL, 
	related_product_id INTEGER, 
	is_read BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(related_product_id) REFERENCES products (id) ON DELETE SET NULL
);
CREATE INDEX ix_notifications_id ON notifications (id);
CREATE TABLE activity_logs (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	user_id INTEGER, 
	user_name VARCHAR(255), 
	action VARCHAR(100) NOT NULL, 
	entity_type VARCHAR(100) NOT NULL, 
	entity_id VARCHAR(100), 
	details TEXT, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_activity_logs_id ON activity_logs (id);
CREATE TABLE report_templates (
	id INTEGER NOT NULL, 
	organization_id INTEGER, 
	title VARCHAR(255) NOT NULL, 
	description TEXT, 
	report_type VARCHAR(50) NOT NULL, 
	config TEXT NOT NULL, 
	is_system BOOLEAN, 
	is_archived BOOLEAN, 
	created_by_user_id INTEGER, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(created_by_user_id) REFERENCES users (id) ON DELETE SET NULL
);
CREATE INDEX ix_report_templates_id ON report_templates (id);
CREATE TABLE offer_price_history (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	offer_id INTEGER, 
	product_id INTEGER NOT NULL, 
	supplier_id INTEGER NOT NULL, 
	old_price FLOAT NOT NULL, 
	new_price FLOAT NOT NULL, 
	change_percent FLOAT, 
	changed_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(offer_id) REFERENCES supplier_offers (id) ON DELETE SET NULL, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE
);
CREATE INDEX ix_offer_price_history_id ON offer_price_history (id);
CREATE TABLE purchase_order_items (
	id INTEGER NOT NULL, 
	purchase_order_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	ordered_quantity FLOAT NOT NULL, 
	received_quantity FLOAT, 
	unit VARCHAR(50) NOT NULL, 
	unit_price FLOAT NOT NULL, 
	total_price FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE RESTRICT
);
CREATE INDEX ix_purchase_order_items_id ON purchase_order_items (id);
CREATE TABLE purchases (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	supplier_id INTEGER NOT NULL, 
	purchase_date DATE NOT NULL, 
	quantity FLOAT NOT NULL, 
	unit VARCHAR(50) NOT NULL, 
	unit_price FLOAT NOT NULL, 
	total_price FLOAT NOT NULL, 
	source VARCHAR(50), 
	import_batch_id INTEGER, 
	purchase_order_id INTEGER, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE, 
	FOREIGN KEY(import_batch_id) REFERENCES import_batches (id) ON DELETE SET NULL, 
	FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id) ON DELETE SET NULL
);
CREATE INDEX ix_purchases_id ON purchases (id);
CREATE INDEX ix_purchases_purchase_date ON purchases (purchase_date);
CREATE TABLE financial_transactions (
	id INTEGER NOT NULL, 
	organization_id INTEGER NOT NULL, 
	transaction_date DATE NOT NULL, 
	description VARCHAR(255) NOT NULL, 
	category VARCHAR(100) NOT NULL, 
	amount FLOAT NOT NULL, 
	transaction_type VARCHAR(20) NOT NULL, 
	payment_method VARCHAR(50), 
	source VARCHAR(50), 
	supplier_id INTEGER, 
	purchase_order_id INTEGER, 
	import_batch_id INTEGER, 
	is_archived BOOLEAN, 
	created_at DATETIME, 
	PRIMARY KEY (id), 
	FOREIGN KEY(organization_id) REFERENCES organizations (id) ON DELETE CASCADE, 
	FOREIGN KEY(supplier_id) REFERENCES suppliers (id) ON DELETE SET NULL, 
	FOREIGN KEY(purchase_order_id) REFERENCES purchase_orders (id) ON DELETE SET NULL, 
	FOREIGN KEY(import_batch_id) REFERENCES import_batches (id) ON DELETE SET NULL
);
CREATE INDEX ix_financial_transactions_category ON financial_transactions (category);
CREATE INDEX ix_financial_transactions_transaction_date ON financial_transactions (transaction_date);
CREATE INDEX ix_financial_transactions_id ON financial_transactions (id);
