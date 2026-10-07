-- Observ monitoring portal database seed (lab)
CREATE DATABASE IF NOT EXISTS observ;

CREATE USER IF NOT EXISTS 'observ_app'@'localhost' IDENTIFIED BY 'Pr0dDbAcc3ss!2023';
GRANT ALL PRIVILEGES ON observ.* TO 'observ_app'@'localhost';
GRANT ALL PRIVILEGES ON observ.* TO 'observ_app'@'127.0.0.1' IDENTIFIED BY 'Pr0dDbAcc3ss!2023';
FLUSH PRIVILEGES;

USE observ;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    password VARCHAR(128) NOT NULL
);

-- The admin password is strong and not meant to be cracked; the intended
-- path into the panel is the SQL injection on the login form.
INSERT INTO users (username, password) VALUES
    ('admin', 'Z7#kR2$wP9!mN4&xL8');

CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    author VARCHAR(64),
    body TEXT
);

-- Realism / breadcrumb: the devops note hints at the sudo health-check setup
-- used for privilege escalation, and confirms credential reuse practices.
INSERT INTO notes (author, body) VALUES
    ('devops', 'Runbook: the developer account runs /opt/health/check.py via sudo for scheduled health checks. Service DB password is reused for the developer login until the rotation ticket is done.');
