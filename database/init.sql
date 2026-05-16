-- =============================================================================
-- VeraMarket — Esquema de base de datos (Sprint 5 — Actualizado)
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
    CREATE TYPE negotiation_status_enum AS ENUM (
        'pending', 'accepted', 'paused', 'rejected', 'cancelled', 'delivered'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE report_reason_enum AS ENUM ('spam', 'offensive', 'fraud');
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

    -- Sprint 5 — HU 7.2: Reputación consolidada
    average_rating  NUMERIC(3,2) DEFAULT 0.00,
    total_reviews   INTEGER DEFAULT 0,

    is_verified     BOOLEAN DEFAULT FALSE,

    -- Privacidad (HU 1.3) — el usuario elige qué datos mostrar
    show_email      BOOLEAN DEFAULT FALSE,
    show_phone      BOOLEAN DEFAULT FALSE,

    -- Push Notification (HU 2.3)
    push_subscriptions JSONB DEFAULT '[]'::JSONB,

    -- Ley 1581/2012 — Consentimiento explícito
    accepted_terms_at TIMESTAMPTZ,
    last_active_at  TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON COLUMN users.email IS 'Correo electrónico del usuario registrado.';
COMMENT ON COLUMN users.accepted_terms_at IS 'Registro de aceptación de términos según Ley 1581.';
COMMENT ON COLUMN users.show_email IS 'Privacidad: mostrar email en perfil público (HU 1.3).';
COMMENT ON COLUMN users.show_phone IS 'Privacidad: mostrar teléfono en perfil público (HU 1.3).';
COMMENT ON COLUMN users.average_rating IS 'Promedio de calificaciones recibidas 1-5 (HU 7.2).';
COMMENT ON COLUMN users.total_reviews IS 'Número total de calificaciones recibidas (HU 7.2).';

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
    subcategory VARCHAR(100),
    condition   VARCHAR(50) DEFAULT 'nuevo',
    brand       VARCHAR(100),
    has_free_shipping BOOLEAN DEFAULT FALSE,
    stock       INTEGER DEFAULT 1,
    discount_percentage NUMERIC(5, 2) DEFAULT 0.00,
    warranty_days INTEGER DEFAULT 0,
    is_returnable BOOLEAN DEFAULT FALSE,
    fulfillment_type VARCHAR(50) DEFAULT 'merchant',
    payment_methods JSONB DEFAULT '["efectivo", "transferencia"]'::JSONB,
    promotions  JSONB DEFAULT '[]'::JSONB,
    attributes  JSONB DEFAULT '{}'::JSONB,
    image_urls  JSONB DEFAULT '[]'::JSONB,
    is_active   BOOLEAN DEFAULT TRUE,
    is_deleted  BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON COLUMN products.price IS 'Precio en COP. Debe ser mayor a 0.';

-- =============================================================================
-- Tabla: user_search_quotas (Sprint 3 — límite diario búsquedas inteligentes)
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_search_quotas (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    search_date     DATE NOT NULL,
    searches_used   INTEGER NOT NULL DEFAULT 0,
    daily_limit     INTEGER NOT NULL DEFAULT 10,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_user_search_quota_user_day UNIQUE (user_id, search_date)
);

COMMENT ON TABLE user_search_quotas IS 'Control diario por usuario para uso de búsqueda semántica (Gemini).';

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
-- Tabla: negotiations (Sprint 4 + Sprint 5 — HU 8.1, 8.3, 8.4, 8.5)
-- =============================================================================
CREATE TABLE IF NOT EXISTS negotiations (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    buyer_id            UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id          UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    status              negotiation_status_enum DEFAULT 'pending',
    buyer_confirmed     BOOLEAN DEFAULT FALSE,
    seller_confirmed    BOOLEAN DEFAULT FALSE,
    agreed_price_cop    NUMERIC(12, 2),
    -- HU 8.3: Parámetros extra de compra
    quantity            INTEGER DEFAULT 1,
    buyer_note          TEXT,
    -- HU 8.4/8.5: Método de pago y bloqueo transaccional
    payment_method      VARCHAR(30),
    coupon_code         VARCHAR(30),
    transaction_locked  BOOLEAN DEFAULT FALSE,
    discount_amount     NUMERIC(12, 2) DEFAULT 0.00,
    created_at          TIMESTAMPTZ DEFAULT NOW(),

    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT chk_buyer_seller CHECK (buyer_id <> seller_id)
);

COMMENT ON TABLE negotiations IS 'Registro de negociaciones entre compradores y vendedores.';

-- =============================================================================
-- Tabla: chat_messages (HU 6.1 — Chat P2P)
-- =============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    negotiation_id  UUID NOT NULL REFERENCES negotiations(id) ON DELETE CASCADE,
    sender_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE chat_messages IS 'Mensajes de chat para las negociaciones P2P (HU 6.1).';

-- =============================================================================
-- Tabla: gmv_metrics (HU 6.5 — Registro de volumen transaccional)
-- =============================================================================
CREATE TABLE IF NOT EXISTS gmv_metrics (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    negotiation_id  UUID NOT NULL UNIQUE REFERENCES negotiations(id) ON DELETE CASCADE,
    product_id      UUID REFERENCES products(id) ON DELETE SET NULL,
    buyer_id        UUID REFERENCES users(id) ON DELETE SET NULL,
    seller_id       UUID REFERENCES users(id) ON DELETE SET NULL,
    amount_cop      NUMERIC(12, 2) NOT NULL,
    product_name    VARCHAR(200),
    completed_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE gmv_metrics IS 'Métricas de volumen bruto de mercancía (GMV) (HU 6.5).';

-- =============================================================================
-- Tabla: ratings (Sprint 5 — HU 7.1: Calificación de transacciones)
-- =============================================================================
CREATE TABLE IF NOT EXISTS ratings (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    negotiation_id  UUID NOT NULL REFERENCES negotiations(id) ON DELETE CASCADE,
    reviewer_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reviewed_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stars           INTEGER NOT NULL CHECK (stars >= 1 AND stars <= 5),
    comment         TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_ratings_one_review_per_user UNIQUE (negotiation_id, reviewer_id)
);

COMMENT ON TABLE ratings IS 'Calificaciones de transacciones completadas (HU 7.1).';

-- =============================================================================
-- Tabla: reports (Sprint 5 — HU 7.3: Reportes de comportamiento indebido)
-- =============================================================================
CREATE TABLE IF NOT EXISTS reports (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reporter_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reported_user_id  UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id        UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    reason            report_reason_enum NOT NULL,
    description       TEXT,
    status            VARCHAR(20) DEFAULT 'pending',
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_reports_one_per_user_product UNIQUE (reporter_id, product_id),
    CONSTRAINT ck_reports_no_self_report CHECK (reporter_id != reported_user_id)
);

COMMENT ON TABLE reports IS 'Reportes de comportamiento indebido (HU 7.3). Auto-oculta tras 3 reportes.';

-- =============================================================================
-- Tabla: transactions (Sprint 5 — HU 8.7: Dashboard Financiero)
-- =============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    negotiation_id  UUID NOT NULL UNIQUE REFERENCES negotiations(id) ON DELETE CASCADE,
    product_id      UUID REFERENCES products(id) ON DELETE SET NULL,
    buyer_id        UUID REFERENCES users(id) ON DELETE SET NULL,
    seller_id       UUID REFERENCES users(id) ON DELETE SET NULL,
    product_name    VARCHAR(200),
    quantity        INTEGER DEFAULT 1,
    unit_price_cop  NUMERIC(12, 2) NOT NULL,
    subtotal_cop    NUMERIC(12, 2) NOT NULL,
    discount_cop    NUMERIC(12, 2) DEFAULT 0,
    total_cop       NUMERIC(12, 2) NOT NULL,
    payment_method  VARCHAR(30),
    coupon_code     VARCHAR(30),
    buyer_note      TEXT,
    completed_at    TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE transactions IS 'Detalle final de transacciones para dashboard financiero (HU 8.7).';

-- =============================================================================
-- Tabla: coupons (Sprint 5 — HU 8.9: Cupones de descuento)
-- =============================================================================
CREATE TABLE IF NOT EXISTS coupons (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    seller_id           UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    code                VARCHAR(30) NOT NULL UNIQUE,
    discount_percent    NUMERIC(5, 2),
    discount_fixed_cop  NUMERIC(12, 2),
    max_uses            INTEGER DEFAULT 1,
    current_uses        INTEGER DEFAULT 0,
    is_active           BOOLEAN DEFAULT TRUE,
    expires_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT ck_coupons_one_discount_type
        CHECK ((discount_percent IS NOT NULL AND discount_fixed_cop IS NULL)
            OR (discount_percent IS NULL AND discount_fixed_cop IS NOT NULL)),
    CONSTRAINT ck_coupons_percent_range
        CHECK (discount_percent IS NULL OR (discount_percent > 0 AND discount_percent <= 100)),
    CONSTRAINT ck_coupons_fixed_positive
        CHECK (discount_fixed_cop IS NULL OR discount_fixed_cop > 0)
);

COMMENT ON TABLE coupons IS 'Cupones de descuento creados por vendedores (HU 8.9).';

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

CREATE INDEX IF NOT EXISTS idx_user_search_quotas_user_day
    ON user_search_quotas (user_id, search_date);

CREATE INDEX IF NOT EXISTS idx_negotiations_status
    ON negotiations (status);

CREATE INDEX IF NOT EXISTS idx_negotiations_buyer_id
    ON negotiations (buyer_id);

CREATE INDEX IF NOT EXISTS idx_negotiations_seller_id
    ON negotiations (seller_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_negotiation
    ON chat_messages (negotiation_id);

CREATE INDEX IF NOT EXISTS idx_ratings_reviewed_id
    ON ratings (reviewed_id);

CREATE INDEX IF NOT EXISTS idx_reports_product_id
    ON reports (product_id);

CREATE INDEX IF NOT EXISTS idx_reports_status
    ON reports (status);

CREATE INDEX IF NOT EXISTS idx_transactions_seller_id
    ON transactions (seller_id);

CREATE INDEX IF NOT EXISTS idx_transactions_completed_at
    ON transactions (completed_at);

CREATE INDEX IF NOT EXISTS idx_coupons_seller_id
    ON coupons (seller_id);

CREATE INDEX IF NOT EXISTS idx_coupons_code
    ON coupons (code);

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
