CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    full_name VARCHAR(100) NOT NULL
);

CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    product VARCHAR(100) NOT NULL,
    amount NUMERIC(15, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    date VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    month VARCHAR(50) NOT NULL,
    segment VARCHAR(50) NOT NULL
);

CREATE TABLE upload_history (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(200) NOT NULL,
    upload_date VARCHAR(50) NOT NULL,
    records_imported INTEGER NOT NULL,
    uploaded_by VARCHAR(100) NOT NULL
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    tag VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    desc TEXT NOT NULL
);

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    desc TEXT NOT NULL,
    time VARCHAR(50) NOT NULL
);

-- Seed Data for Users
INSERT INTO users (username, password, role, full_name) VALUES
('shrikant', 'shrikant123', 'CEO', 'Shrikant Keche'),
('manager', 'manager123', 'Manager', 'Manager'),
('analyst', 'analyst123', 'Analyst', 'Analyst');
