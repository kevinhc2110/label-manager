CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS Printer (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    ip_address VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    location VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

INSERT INTO Printer (id, name, ip_address, port, location, is_active)
VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Almacén Principal', '192.168.1.100', 9100, 'Planta Baja - Sector A', TRUE),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'Oficina Admin', '192.168.1.101', 9100, 'Piso 2 - Admin', FALSE),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'Kyocera Pruebas', '192.168.69.50', 9100, 'Laboratorio - IoT', TRUE)
ON CONFLICT (id) DO NOTHING;

