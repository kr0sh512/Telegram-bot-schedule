CREATE DATABASE IF NOT EXISTS tg_schedule;

CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    group VARCHAR(255) DEFAULT 'other',
    timeout INT DEFAULT 10,
    allow_message BOOLEAN DEFAULT TRUE,
    thread VARCHAR(255) DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS schedule(
    id BIGSERIAL PRIMARY KEY,
    day_of_week VARCHAR(255),
    begin_time VARCHAR(20),
    end_time VARCHAR(20),
    course VARCHAR(255),
    lector VARCHAR(255),
    is_lecture BOOLEAN DEFAULT FALSE,
    room VARCHAR(20),
    group VARCHAR(10),
    parity VARCHAR(10),
);