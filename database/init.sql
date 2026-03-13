-- =============================================================================
-- VeraMarket — Esquema de base de datos (Sprint 1)
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
    CREATE TYPE vendor_status_type AS ENUM ('pending', 'approved', 'rejected');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE negotiation_status AS ENUM ('pending', 'accepted', 'rejected', 'completed');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- =============================================================================
-- Tabla: users (Sprint 1 — OTP auth, sin password, con privacy settings)
-- Campos alineados con ORM: String(50), String(150), String(255), etc.
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    institutional_id VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    role            user_role NOT NULL DEFAULT 'comprador',
    vendor_status   vendor_status_type NOT NULL DEFAULT 'pending',
    sinapsis_code   VARCHAR(50) UNIQUE,
    reputation      NUMERIC(3,2) DEFAULT 0.00,
    is_verified     BOOLEAN DEFAULT FALSE,

    -- Privacidad (HU 1.3) — el usuario elige qué datos mostrar
    show_email      BOOLEAN DEFAULT FALSE,
    show_phone      BOOLEAN DEFAULT FALSE,

    -- Ley 1581/2012 — Consentimiento explícito
    accepted_terms_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON COLUMN users.email IS 'Correo electrónico del usuario registrado.';
COMMENT ON COLUMN users.accepted_terms_at IS 'Registro de aceptación de términos según Ley 1581.';
COMMENT ON COLUMN users.show_email IS 'Privacidad: mostrar email en perfil público (HU 1.3).';
COMMENT ON COLUMN users.show_phone IS 'Privacidad: mostrar teléfono en perfil público (HU 1.3).';

-- =============================================================================
-- Tabla: otp_codes (HU 1.1 — autenticación por código de un solo uso)
-- =============================================================================
CREATE TABLE IF NOT EXISTS otp_codes (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email       VARCHAR(255) NOT NULL,
    code        VARCHAR(6) NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    is_used     BOOLEAN DEFAULT FALSE,
    attempts    INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_otp_codes_email ON otp_codes (email);
CREATE INDEX IF NOT EXISTS idx_otp_codes_expires ON otp_codes (expires_at);

COMMENT ON TABLE otp_codes IS 'Códigos OTP de un solo uso para autenticación sin contraseña (HU 1.1).';

-- =============================================================================
-- Tabla: products (campos alineados con ORM: String(200))
-- =============================================================================
CREATE TABLE IF NOT EXISTS products (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(200) NOT NULL,
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
-- Tabla: locations (PostGIS — campos alineados con ORM)
-- =============================================================================
CREATE TABLE IF NOT EXISTS locations (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    campus      VARCHAR(100) DEFAULT 'UAO',
    coordinates GEOMETRY(Point, 4326),
    label       VARCHAR(200),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
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
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_self_access ON users
    FOR ALL
    USING (id = current_setting('app.current_user_id', TRUE)::UUID);

CREATE POLICY users_public_read ON users
    FOR SELECT
    USING (TRUE);

-- =============================================================================
-- Índices
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_locations_coordinates
    ON locations USING GIST (coordinates);

CREATE INDEX IF NOT EXISTS idx_products_category
    ON products (category);

CREATE INDEX IF NOT EXISTS idx_products_is_active
    ON products (is_active);

CREATE INDEX IF NOT EXISTS idx_products_seller_id
    ON products (seller_id);

CREATE INDEX IF NOT EXISTS idx_users_institutional_id
    ON users (institutional_id);

CREATE INDEX IF NOT EXISTS idx_negotiations_status
    ON negotiations (status);

CREATE INDEX IF NOT EXISTS idx_negotiations_buyer_id
    ON negotiations (buyer_id);

CREATE INDEX IF NOT EXISTS idx_negotiations_seller_id
    ON negotiations (seller_id);

-- =============================================================================
-- Datos semilla para desarrollo
-- =============================================================================
INSERT INTO users (institutional_id, name, email, phone, role, is_verified, accepted_terms_at)
VALUES (
    '2210000',
    'Admin VeraMarket',
    'admin@uao.edu.co',
    '3001234567',
    'vendedor',
    TRUE,
    NOW()
)
ON CONFLICT (institutional_id) DO NOTHING;
