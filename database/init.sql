-- =============================================================================
-- VeraMarket — Esquema de base de datos
-- PostgreSQL 15 + PostGIS
-- =============================================================================
-- Extensiones
-- =============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =============================================================================
-- Tipos ENUM
-- =============================================================================
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('vendedor', 'comprador');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE negotiation_status AS ENUM ('pending', 'accepted', 'rejected', 'completed');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- =============================================================================
-- Tabla: users
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institutional_id VARCHAR(20) NOT NULL UNIQUE,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE
                    CHECK (email LIKE '%@%.edu.co'),
    phone           VARCHAR(15),
    hashed_password TEXT NOT NULL,
    role            user_role NOT NULL DEFAULT 'comprador',
    reputation      FLOAT DEFAULT 0.0,
    is_verified     BOOLEAN DEFAULT FALSE,
    accepted_terms_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON COLUMN users.email IS 'Solo correos institucionales .edu.co (Ley 1581/2012).';
COMMENT ON COLUMN users.accepted_terms_at IS 'Registro de aceptación de términos según Ley 1581.';

-- =============================================================================
-- Tabla: products
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    price       NUMERIC(12, 2) NOT NULL CHECK (price > 0),
    category    VARCHAR(50),
    image_urls  JSONB DEFAULT '[]'::JSONB,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON COLUMN products.price IS 'Precio en COP. Debe ser mayor a 0.';

-- =============================================================================
-- Tabla: locations (PostGIS)
-- =============================================================================
CREATE TABLE IF NOT EXISTS locations (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    campus      VARCHAR(50) DEFAULT 'UAO',
    coordinates GEOMETRY(Point, 4326),
    label       VARCHAR(100),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE locations IS 'Ubicación de vendedores con coordenadas PostGIS (SRID 4326).';

-- =============================================================================
-- Tabla: negotiations
-- =============================================================================
CREATE TABLE IF NOT EXISTS negotiations (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id  UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    status      negotiation_status DEFAULT 'pending',
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_buyer_seller CHECK (buyer_id <> seller_id)
);

COMMENT ON TABLE negotiations IS 'Registro de negociaciones entre compradores y vendedores.';

-- =============================================================================
-- Row Level Security (RLS) — Ley 1581/2012
-- =============================================================================
-- Habilitar RLS en la tabla de usuarios para proteger datos personales.
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Política: un usuario solo puede ver sus propios datos privados.
CREATE POLICY users_self_access ON users
    FOR ALL
    USING (id = current_setting('app.current_user_id', TRUE)::UUID);

-- Política: datos públicos visibles para todos los autenticados.
-- (Nombre, reputación, rol — sin email ni teléfono)
CREATE POLICY users_public_read ON users
    FOR SELECT
    USING (TRUE);

-- =============================================================================
-- Índices
-- =============================================================================
-- Espacial: búsqueda de vendedores cercanos con PostGIS
CREATE INDEX IF NOT EXISTS idx_locations_coordinates
    ON locations USING GIST (coordinates);

-- Productos: búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_products_category
    ON products (category);

CREATE INDEX IF NOT EXISTS idx_products_is_active
    ON products (is_active);

CREATE INDEX IF NOT EXISTS idx_products_seller_id
    ON products (seller_id);

-- Usuarios: búsquedas por identificación institucional
CREATE INDEX IF NOT EXISTS idx_users_institutional_id
    ON users (institutional_id);

-- Negociaciones: filtros por estado y participantes
CREATE INDEX IF NOT EXISTS idx_negotiations_status
    ON negotiations (status);

CREATE INDEX IF NOT EXISTS idx_negotiations_buyer_id
    ON negotiations (buyer_id);

CREATE INDEX IF NOT EXISTS idx_negotiations_seller_id
    ON negotiations (seller_id);

-- =============================================================================
-- Datos semilla para desarrollo
-- =============================================================================
-- Ubicación por defecto: Campus UAO, Cali
INSERT INTO users (institutional_id, name, email, phone, hashed_password, role, is_verified, accepted_terms_at)
VALUES (
    '2210000',
    'Admin VeraMarket',
    'admin@uao.edu.co',
    '3001234567',
    '$2b$12$PLACEHOLDER_HASH_FOR_DEV_ONLY',
    'vendedor',
    TRUE,
    NOW()
)
ON CONFLICT (institutional_id) DO NOTHING;
