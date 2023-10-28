#include <iostream>
#include <pqxx/pqxx>
#include <modbus.h>
#include <nlohmann/json.hpp>
#include <fstream>

int main() {
    // Konfigurationsdatei einlesen
    std::ifstream config_file("config.json");
    nlohmann::json config;
    config_file >> config;

    // Datenbankverbindung aufbauen
    pqxx::connection db_connection(config["database"]["connection_string"].get<std::string>());
    db_connection.prepare("insert_sensor_data", "INSERT INTO sensor_data (sensor_id, value) VALUES ($1, $2)");

    // Modbus-Verbindung aufbauen
    modbus_t *mb = modbus_new_rtu(
        config["modbus"]["port"].get<std::string>().c_str(),
        config["modbus"]["baudrate"].get<int>(),
        config["modbus"]["parity"].get<std::string>().c_str()[0],
        config["modbus"]["bytesize"].get<int>(),
        config["modbus"]["stopbits"].get<int>()
    );
    modbus_set_slave(mb, 1);  // Default Slave-ID
    if (modbus_connect(mb) == -1) {
        std::cerr << "Connection failed: " << modbus_strerror(errno) << std::endl;
        modbus_free(mb);
        return -1;
    }

    // Sensordaten auslesen und in die Datenbank schreiben
    for (const auto& sensor : config["sensors"]) {
        int slave_id = sensor.value("slave_id", 1).get<int>();
        modbus_set_slave(mb, slave_id);

        uint16_t tab_reg[32];
        int register_address = sensor["register_address"].get<int>();
        int rc = modbus_read_registers(mb, register_address, 1, tab_reg);
        if (rc == -1) {
            std::cerr << "Failed to read register for sensor " << slave_id << ": " << modbus_strerror(errno) << std::endl;
            continue;
        }

        int sensor_id = sensor["id"].get<int>();
        int value = tab_reg[0];
        pqxx::work transaction(db_connection);
        transaction.exec_prepared("insert_sensor_data", sensor_id, value);
        transaction.commit();

        std::cout << "Sensor " << sensor_id << " (" << sensor["type"].get<std::string>() << "): " << value << std::endl;
    }

    // Verbindung schließen
    modbus_close(mb);
    modbus_free(mb);

    return 0;
}
