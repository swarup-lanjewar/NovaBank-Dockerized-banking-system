CREATE DATABASE IF NOT EXISTS novabank;

USE novabank;

-- =========================
-- USERS
-- =========================

CREATE TABLE users(

    id INT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) NOT NULL UNIQUE,

    password VARCHAR(255) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

-- =========================
-- ACCOUNTS
-- =========================

CREATE TABLE accounts(

    id INT AUTO_INCREMENT PRIMARY KEY,

    user_id INT NOT NULL,

    account_number BIGINT NOT NULL UNIQUE,

    balance DECIMAL(12,2) DEFAULT 0.00,

    status ENUM('ACTIVE','BLOCKED') DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)
    REFERENCES users(id)
    ON DELETE CASCADE

);

-- =========================
-- TRANSACTIONS
-- =========================

CREATE TABLE transactions(

    id INT AUTO_INCREMENT PRIMARY KEY,

    sender_account BIGINT,

    receiver_account BIGINT,

    transaction_type ENUM(
        'Deposit',
        'Withdraw',
        'Transfer'
    ),

    amount DECIMAL(12,2) NOT NULL,

    status ENUM(
        'SUCCESS',
        'FAILED'
    ) DEFAULT 'SUCCESS',

    remarks VARCHAR(255),

    reference_id CHAR(36),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);