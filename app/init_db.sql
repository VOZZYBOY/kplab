-- SQL script to initialize the database schema

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role_id INT REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialty VARCHAR(100),
    availability TEXT
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    doctor_id INT REFERENCES doctors(id),
    service_id INT REFERENCES services(id),
    appointment_time TIMESTAMP NOT NULL,
    UNIQUE(user_id, doctor_id, appointment_time) -- Prevent double booking
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patient_records (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    record TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default roles
INSERT INTO roles (name) VALUES ('Administrator'), ('Editor'), ('User');

CREATE TABLE ApiData (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255),
    category_name VARCHAR(255),
    price VARCHAR(50),
    filial_name VARCHAR(255),
    specialist_name VARCHAR(255),
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE NeuralNetworkInput (
    id SERIAL PRIMARY KEY,
    api_data_id INT REFERENCES ApiData(id),
    neural_input TEXT,
    response TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION add_api_data(
    service_name TEXT,
    category_name TEXT,
    price TEXT,
    filial_name TEXT,
    specialist_name TEXT
) RETURNS VOID AS $$
BEGIN
    INSERT INTO ApiData (service_name, category_name, price, filial_name, specialist_name)
    VALUES (service_name, category_name, price, filial_name, specialist_name);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION prepare_neural_input()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO NeuralNetworkInput (api_data_id, neural_input)
    VALUES (NEW.id, 
            CONCAT('Service: ', NEW.service_name, 
                   ', Category: ', NEW.category_name, 
                   ', Price: ', NEW.price, 
                   ', Filial: ', NEW.filial_name, 
                   ', Specialist: ', NEW.specialist_name));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER api_data_trigger
AFTER INSERT ON ApiData
FOR EACH ROW
EXECUTE FUNCTION prepare_neural_input();


CREATE OR REPLACE FUNCTION prepare_neural_input()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO NeuralNetworkInput (api_data_id, neural_input)
    VALUES (NEW.id, 
            CONCAT('Service: ', NEW.service_name, 
                   ', Category: ', NEW.category_name, 
                   ', Price: ', NEW.price, 
                   ', Filial: ', NEW.filial_name, 
                   ', Specialist: ', NEW.specialist_name));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER api_data_trigger
AFTER INSERT ON ApiData
FOR EACH ROW
EXECUTE FUNCTION prepare_neural_input();

CREATE OR REPLACE FUNCTION update_processed_status(api_data_id INT, response TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE ApiData SET processed = TRUE WHERE id = api_data_id;
    UPDATE NeuralNetworkInput SET response = response, processed_at = CURRENT_TIMESTAMP WHERE api_data_id = api_data_id;
END;
$$ LANGUAGE plpgsql;

