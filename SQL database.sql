CREATE DATABASE security_project;

USE security_project;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

INSERT INTO users (username, password)
VALUES ('admin', 'admin123');

CREATE TABLE attack_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);c