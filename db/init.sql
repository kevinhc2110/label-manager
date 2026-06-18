CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS printer (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    ip_address VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    location VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS label_template (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    content_template TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS print_job (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    printer_id UUID NOT NULL REFERENCES Printer(id),
    template_id UUID REFERENCES label_template(id),
    text TEXT,
    qr_data TEXT,
    copies INTEGER NOT NULL DEFAULT 1,
    variables JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_print_job_status ON print_job(status);

CREATE OR REPLACE FUNCTION notify_print_job()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('print_jobs', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_print_job_insert ON print_job;
CREATE TRIGGER trg_print_job_insert
    AFTER INSERT ON print_job
    FOR EACH ROW
    EXECUTE FUNCTION notify_print_job();

INSERT INTO Printer (id, name, ip_address, port, location, is_active)
VALUES
    ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'Almacén Principal', '192.168.1.100', 9100, 'Planta Baja - Sector A', TRUE),
    ('b2c3d4e5-f6a7-8901-bcde-f12345678901', 'Oficina Admin', '192.168.1.101', 9100, 'Piso 2 - Admin', FALSE),
    ('c3d4e5f6-a7b8-9012-cdef-123456789012', 'Kyocera Pruebas', '192.168.69.50', 9100, 'Laboratorio - IoT', TRUE)
ON CONFLICT (id) DO NOTHING;

INSERT INTO label_template (name, content_template)
VALUES
    ('default', 'Etiqueta estándar'),
    ('shipping', 'Pedido {{order_id}} - {{customer}}')
ON CONFLICT (name) DO NOTHING;
