-- Semilla de Datos VeraMarket para Demostración Final (Sprint 5)

-- 1. Usuarios
INSERT INTO users (id, email, name, institutional_id, role, is_verified, vendor_status, accepted_terms_at, phone, average_rating, total_reviews)
VALUES 
('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'comprador@uao.edu.co', 'Comprador UAO', '2200111', 'comprador', true, 'pending', now(), '3119876543', 0.0, 0),
('b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'vendedor@uao.edu.co', 'Emprendedor Vera', '2200222', 'vendedor', true, 'approved', now(), '3001234567', 5.0, 1);

-- 2. Ubicación
INSERT INTO locations (id, user_id, campus, label, coordinates)
VALUES (uuid_generate_v4(), 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'UAO', 'Cafetería Central', ST_GeomFromText('POINT(-76.5320 3.3516)', 4326));

-- 3. Cupones
INSERT INTO coupons (id, seller_id, code, discount_percent, discount_fixed_cop, max_uses, is_active)
VALUES 
(uuid_generate_v4(), 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'PROMO10', 10.0, 0, 100, true),
(uuid_generate_v4(), 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'UAO5000', 0, 5000.0, 50, true);

-- 4. Productos
INSERT INTO products (id, seller_id, name, description, category, price, stock, condition, fulfillment_type, payment_methods, image_urls, is_active, discount_percentage, has_free_shipping, warranty_days)
VALUES 
('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Notebook Profesional', 'Cuaderno de alta calidad para apuntes.', 'papelería', 55000, 10, 'nuevo', 'merchant', '["nequi", "daviplata"]'::jsonb, '["https://images.unsplash.com/photo-1517842645767-c639042777db"]'::jsonb, true, 0, false, 30),
('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Smartphone Reacondicionado', 'iPhone 12 en excelente estado.', 'tecnología', 1200000, 2, 'reacondicionado', 'veramarket', '["nequi"]'::jsonb, '["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9"]'::jsonb, true, 15.0, false, 0),
('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Morral Ergonómico', 'Ideal para cargar portátiles pesados.', 'accesorios', 85000, 5, 'nuevo', 'merchant', '["efectivo"]'::jsonb, '["https://images.unsplash.com/photo-1553062407-98eeb64c6a62"]'::jsonb, true, 0, true, 0),
('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Libro Cálculo Stewart', 'Sétima edición, muy poco uso.', 'libros', 45000, 1, 'usado', 'merchant', '["efectivo", "nequi"]'::jsonb, '["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c"]'::jsonb, true, 0, false, 0),
('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a05', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Café Gourmet UAO', 'Grano seleccionado del Cauca.', 'comida', 6000, 50, 'nuevo', 'merchant', '["efectivo"]'::jsonb, '["https://images.unsplash.com/photo-1509042239860-f550ce710b93"]'::jsonb, true, 5.0, false, 0),
('p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a06', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Audífonos Bluetooth', 'Cancelación de ruido activa.', 'tecnología', 150000, 0, 'nuevo', 'merchant', '["daviplata"]'::jsonb, '["https://images.unsplash.com/photo-1505740420928-5e560c06d30e"]'::jsonb, false, 0, false, 0);

-- 5. Negociaciones
-- Venta 1: Entregada (Café)
INSERT INTO negotiations (id, buyer_id, seller_id, product_id, status, agreed_price_cop, quantity, payment_method, transaction_locked, buyer_confirmed, seller_confirmed)
VALUES ('n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a05', 'delivered', 6000, 2, 'efectivo', true, true, true);

-- Venta 2: Entregada (Libro con Cupón)
INSERT INTO negotiations (id, buyer_id, seller_id, product_id, status, agreed_price_cop, quantity, payment_method, coupon_code, discount_amount, transaction_locked, buyer_confirmed, seller_confirmed)
VALUES ('n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04', 'delivered', 45000, 1, 'nequi', 'UAO5000', 5000, true, true, true);

-- Otras Negociaciones
INSERT INTO negotiations (id, buyer_id, seller_id, product_id, status, agreed_price_cop, quantity)
VALUES 
('n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01', 'accepted', 55000, 1),
('n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'pending', 1200000, 1),
('n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a05', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a03', 'cancelled', 85000, 1);

-- Mensaje de Chat
INSERT INTO chat_messages (id, negotiation_id, sender_id, content)
VALUES (uuid_generate_v4(), 'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'Hola, ¿todavía lo tienes disponible?');

-- 6. Transacciones y Métricas GMV
INSERT INTO transactions (id, negotiation_id, product_id, buyer_id, seller_id, product_name, quantity, unit_price_cop, subtotal_cop, discount_cop, total_cop, payment_method, completed_at)
VALUES 
('t0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01', 'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a05', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Café Gourmet UAO', 2, 6000, 12000, 0, 12000, 'efectivo', now() - interval '2 days'),
('t0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 'Libro Cálculo Stewart', 1, 45000, 45000, 5000, 40000, 'nequi', now() - interval '5 hours');

INSERT INTO gmv_metrics (id, negotiation_id, product_id, buyer_id, seller_id, amount_cop, product_name)
VALUES 
(uuid_generate_v4(), 'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a01', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a05', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 12000, 'Café Gourmet UAO'),
(uuid_generate_v4(), 'n0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'p0eebc99-9c0b-4ef8-bb6d-6bb9bd380a04', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 40000, 'Libro Cálculo Stewart');

-- 7. Calificación
INSERT INTO ratings (id, transaction_id, rater_id, rated_user_id, score, comment)
VALUES (uuid_generate_v4(), 't0eebc99-9c0b-4ef8-bb6d-6bb9bd380a02', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'b0eebc99-9c0b-4ef8-bb6d-6bb9bd380a22', 5, 'Excelente vendedor, el libro está como nuevo.');
