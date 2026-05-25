"""Create initial GasBot schema.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-05-25
"""

from collections.abc import Sequence

from alembic import op

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply initial schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    op.execute(
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email VARCHAR(255) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            phone VARCHAR(20),
            address TEXT,
            role VARCHAR(20) NOT NULL DEFAULT 'customer'
                CONSTRAINT ck_users_role CHECK (role IN ('customer', 'staff', 'admin')),
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_users_email ON users(email);
        CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL;
        CREATE INDEX idx_users_role ON users(role);
        COMMENT ON TABLE users IS 'User accounts: customers, staff (handle escalations), admins';
        COMMENT ON COLUMN users.role IS 'customer (default), staff (chat support), admin (full access)';
        """
    )

    op.execute(
        """
        CREATE TABLE products (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            sku VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            brand VARCHAR(100) NOT NULL,
            size_kg NUMERIC(5,2) NOT NULL,
            price NUMERIC(10,2) NOT NULL CONSTRAINT ck_products_price CHECK (price >= 0),
            stock_quantity INTEGER NOT NULL DEFAULT 0
                CONSTRAINT ck_products_stock_quantity CHECK (stock_quantity >= 0),
            description TEXT,
            image_url TEXT,
            safety_info TEXT,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_products_sku ON products(sku);
        CREATE INDEX idx_products_brand ON products(brand);
        CREATE INDEX idx_products_active ON products(is_active);
        CREATE INDEX idx_products_name_trgm ON products USING gin (name gin_trgm_ops);
        COMMENT ON TABLE products IS 'Gas LPG products available for sale';
        COMMENT ON COLUMN products.size_kg IS 'Gas cylinder size in kg (typically 6, 12, or 45)';
        COMMENT ON COLUMN products.safety_info IS 'Vietnamese safety instructions specific to this product';
        """
    )

    op.execute(
        """
        CREATE TABLE orders (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            order_number VARCHAR(20) UNIQUE NOT NULL,
            user_id UUID NULL REFERENCES users(id),
            customer_name VARCHAR(255) NOT NULL,
            customer_phone VARCHAR(20) NOT NULL,
            customer_email VARCHAR(255),
            delivery_address TEXT NOT NULL,
            delivery_ward VARCHAR(100),
            delivery_district VARCHAR(100),
            delivery_city VARCHAR(100) NOT NULL DEFAULT 'TP. Hồ Chí Minh',
            delivery_notes TEXT,
            different_recipient_name VARCHAR(255),
            different_recipient_phone VARCHAR(20),
            subtotal NUMERIC(10,2) NOT NULL CONSTRAINT ck_orders_subtotal CHECK (subtotal >= 0),
            shipping_fee NUMERIC(10,2) NOT NULL DEFAULT 0
                CONSTRAINT ck_orders_shipping_fee CHECK (shipping_fee >= 0),
            total_amount NUMERIC(10,2) NOT NULL
                CONSTRAINT ck_orders_total_amount CHECK (total_amount >= 0),
            vat_invoice_requested BOOLEAN NOT NULL DEFAULT FALSE,
            vat_info JSONB,
            payment_method VARCHAR(20) NOT NULL DEFAULT 'cod'
                CONSTRAINT ck_orders_payment_method CHECK (payment_method IN ('cod', 'bank_transfer')),
            payment_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                CONSTRAINT ck_orders_payment_status CHECK (payment_status IN ('pending', 'paid', 'refunded')),
            status VARCHAR(20) NOT NULL DEFAULT 'pending'
                CONSTRAINT ck_orders_status CHECK (status IN ('pending', 'confirmed', 'shipping', 'delivered', 'cancelled')),
            source VARCHAR(20) NOT NULL DEFAULT 'website'
                CONSTRAINT ck_orders_source CHECK (source IN ('website', 'chatbot')),
            referral_conversation_id UUID,
            idempotency_key UUID UNIQUE,
            customer_notes TEXT,
            internal_notes TEXT,
            cancelled_at TIMESTAMPTZ,
            cancelled_reason TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            delivered_at TIMESTAMPTZ
        );
        CREATE INDEX idx_orders_order_number ON orders(order_number);
        CREATE INDEX idx_orders_user_id ON orders(user_id) WHERE user_id IS NOT NULL;
        CREATE INDEX idx_orders_customer_phone ON orders(customer_phone);
        CREATE INDEX idx_orders_status ON orders(status);
        CREATE INDEX idx_orders_source ON orders(source);
        CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
        CREATE INDEX idx_orders_idempotency ON orders(idempotency_key)
            WHERE idempotency_key IS NOT NULL;
        CREATE INDEX idx_orders_referral_conv ON orders(referral_conversation_id)
            WHERE referral_conversation_id IS NOT NULL;
        COMMENT ON TABLE orders IS 'Customer orders with embedded delivery and optional VAT info';
        COMMENT ON COLUMN orders.user_id IS 'Nullable to support guest checkout';
        COMMENT ON COLUMN orders.order_number IS 'Format: GB-YYYYMMDD-XXXX, auto-generated by trigger';
        COMMENT ON COLUMN orders.vat_info IS 'JSONB: {company_name, tax_code, address} when vat_invoice_requested=TRUE';
        COMMENT ON COLUMN orders.source IS 'website or chatbot';
        COMMENT ON COLUMN orders.idempotency_key IS 'Client-provided UUID to prevent duplicate orders on retry';
        """
    )

    op.execute(
        """
        CREATE TABLE order_items (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id UUID REFERENCES products(id),
            product_name VARCHAR(255) NOT NULL,
            product_brand VARCHAR(100),
            product_size_kg NUMERIC(5,2),
            quantity INTEGER NOT NULL CONSTRAINT ck_order_items_quantity CHECK (quantity > 0),
            unit_price NUMERIC(10,2) NOT NULL
                CONSTRAINT ck_order_items_unit_price CHECK (unit_price >= 0),
            subtotal NUMERIC(10,2) NOT NULL
                CONSTRAINT ck_order_items_subtotal CHECK (subtotal >= 0),
            is_exchange BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_order_items_order_id ON order_items(order_id);
        CREATE INDEX idx_order_items_product_id ON order_items(product_id)
            WHERE product_id IS NOT NULL;
        COMMENT ON TABLE order_items IS 'Order line items with snapshot fields';
        COMMENT ON COLUMN order_items.product_id IS 'Nullable to preserve order history if product deleted';
        COMMENT ON COLUMN order_items.is_exchange IS 'TRUE if customer is exchanging an old gas cylinder';
        """
    )

    op.execute(
        """
        CREATE TABLE conversations (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id),
            session_id VARCHAR(100) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'active'
                CONSTRAINT ck_conversations_status CHECK (status IN ('active', 'escalated', 'resolved', 'abandoned')),
            assigned_to UUID REFERENCES users(id),
            escalated_at TIMESTAMPTZ,
            escalation_reason TEXT,
            resolved_at TIMESTAMPTZ,
            satisfaction_rating INTEGER
                CONSTRAINT ck_conversations_satisfaction_rating CHECK (satisfaction_rating BETWEEN 1 AND 5),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_conversations_user_id ON conversations(user_id) WHERE user_id IS NOT NULL;
        CREATE INDEX idx_conversations_session_id ON conversations(session_id);
        CREATE INDEX idx_conversations_status ON conversations(status);
        CREATE INDEX idx_conversations_assigned ON conversations(assigned_to)
            WHERE assigned_to IS NOT NULL;
        COMMENT ON TABLE conversations IS 'Chatbot conversation sessions, supports authenticated and anonymous users';
        COMMENT ON COLUMN conversations.user_id IS 'NULL for anonymous users tracked via session_id';
        COMMENT ON COLUMN conversations.assigned_to IS 'Staff member handling escalation (NULL if bot is handling)';
        """
    )

    op.execute(
        """
        ALTER TABLE orders
        ADD CONSTRAINT fk_orders_referral_conversation
        FOREIGN KEY (referral_conversation_id) REFERENCES conversations(id);

        CREATE TABLE messages (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL
                CONSTRAINT ck_messages_role CHECK (role IN ('user', 'assistant', 'staff', 'system')),
            content TEXT NOT NULL,
            intent VARCHAR(50),
            intent_confidence NUMERIC(3,2)
                CONSTRAINT ck_messages_intent_confidence CHECK (intent_confidence BETWEEN 0 AND 1),
            llm_provider VARCHAR(50),
            llm_model VARCHAR(100),
            tokens_used INTEGER,
            latency_ms INTEGER,
            retrieved_documents JSONB,
            feedback_score INTEGER CONSTRAINT ck_messages_feedback_score CHECK (feedback_score IN (-1, 0, 1)),
            flagged_for_review BOOLEAN NOT NULL DEFAULT FALSE,
            reviewed_by UUID REFERENCES users(id),
            reviewed_at TIMESTAMPTZ,
            review_action VARCHAR(20)
                CONSTRAINT ck_messages_review_action CHECK (review_action IN ('approved', 'rejected', 'added_to_kb')),
            corrected_content TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
        CREATE INDEX idx_messages_role ON messages(role);
        CREATE INDEX idx_messages_intent ON messages(intent) WHERE intent IS NOT NULL;
        CREATE INDEX idx_messages_flagged ON messages(flagged_for_review)
            WHERE flagged_for_review = TRUE;
        CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
        COMMENT ON TABLE messages IS 'Chat messages with intent classification and review flag';
        COMMENT ON COLUMN messages.flagged_for_review IS 'Auto-flagged when feedback_score=-1 or intent_confidence<0.6';
        COMMENT ON COLUMN messages.retrieved_documents IS 'JSONB array of KB documents used by RAG';
        COMMENT ON COLUMN messages.corrected_content IS 'Staff-edited correction for training data';
        """
    )

    op.execute(
        """
        CREATE TABLE knowledge_base (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            category VARCHAR(50) NOT NULL
                CONSTRAINT ck_knowledge_base_category CHECK (category IN ('safety', 'product_info', 'delivery', 'pricing', 'company', 'faq', 'technical')),
            source VARCHAR(255),
            embedding VECTOR(768),
            metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            source_message_id UUID REFERENCES messages(id),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX idx_kb_category ON knowledge_base(category);
        CREATE INDEX idx_kb_active ON knowledge_base(is_active);
        CREATE INDEX idx_kb_embedding ON knowledge_base
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
        CREATE INDEX idx_kb_title_trgm ON knowledge_base USING gin (title gin_trgm_ops);
        CREATE INDEX idx_kb_content_trgm ON knowledge_base USING gin (content gin_trgm_ops);
        COMMENT ON TABLE knowledge_base IS 'Knowledge base documents for RAG retrieval (Vietnamese)';
        COMMENT ON COLUMN knowledge_base.embedding IS 'Vietnamese SBERT embedding, 768 dimensions';
        COMMENT ON COLUMN knowledge_base.source_message_id IS 'Reference to message if KB entry was created from approved chat';
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION generate_order_number()
        RETURNS VARCHAR AS $$
        DECLARE
            new_number VARCHAR;
            today_date VARCHAR;
            counter INTEGER;
        BEGIN
            today_date := TO_CHAR(NOW(), 'YYYYMMDD');
            SELECT COALESCE(MAX(CAST(SUBSTRING(order_number FROM 13) AS INTEGER)), 0) + 1
            INTO counter
            FROM orders
            WHERE order_number LIKE 'GB-' || today_date || '-%';
            new_number := 'GB-' || today_date || '-' || LPAD(counter::TEXT, 4, '0');
            RETURN new_number;
        END;
        $$ LANGUAGE plpgsql;

        CREATE OR REPLACE FUNCTION set_order_number()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.order_number IS NULL OR NEW.order_number = '' THEN
                NEW.order_number := generate_order_number();
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_set_order_number
            BEFORE INSERT ON orders
            FOR EACH ROW
            EXECUTE FUNCTION set_order_number();

        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        CREATE TRIGGER trigger_products_updated_at BEFORE UPDATE ON products
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        CREATE TRIGGER trigger_orders_updated_at BEFORE UPDATE ON orders
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        CREATE TRIGGER trigger_conversations_updated_at BEFORE UPDATE ON conversations
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        CREATE TRIGGER trigger_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION match_documents(
            query_embedding VECTOR(768),
            match_threshold FLOAT,
            match_count INT,
            filter_category TEXT DEFAULT NULL
        )
        RETURNS TABLE (
            id UUID,
            title VARCHAR,
            content TEXT,
            category VARCHAR,
            similarity FLOAT
        )
        LANGUAGE plpgsql STABLE AS $$
        BEGIN
            RETURN QUERY
            SELECT
                kb.id,
                kb.title,
                kb.content,
                kb.category,
                1 - (kb.embedding <=> query_embedding) AS similarity
            FROM knowledge_base kb
            WHERE kb.is_active = TRUE
              AND kb.embedding IS NOT NULL
              AND (filter_category IS NULL OR kb.category = filter_category)
              AND 1 - (kb.embedding <=> query_embedding) > match_threshold
            ORDER BY kb.embedding <=> query_embedding
            LIMIT match_count;
        END;
        $$;

        CREATE OR REPLACE FUNCTION get_customer_orders(
            p_phone VARCHAR,
            p_limit INTEGER DEFAULT 10
        )
        RETURNS TABLE (
            order_id UUID,
            order_number VARCHAR,
            total_amount NUMERIC,
            status VARCHAR,
            created_at TIMESTAMPTZ
        )
        LANGUAGE plpgsql STABLE AS $$
        BEGIN
            RETURN QUERY
            SELECT o.id, o.order_number, o.total_amount, o.status, o.created_at
            FROM orders o
            WHERE o.customer_phone = p_phone
               OR o.user_id IN (SELECT id FROM users WHERE phone = p_phone)
            ORDER BY o.created_at DESC
            LIMIT p_limit;
        END;
        $$;

        CREATE OR REPLACE FUNCTION calculate_order_total(p_order_id UUID)
        RETURNS NUMERIC AS $$
        DECLARE
            v_total NUMERIC;
        BEGIN
            SELECT
                COALESCE(SUM(oi.subtotal), 0) +
                COALESCE((SELECT shipping_fee FROM orders WHERE id = p_order_id), 0)
            INTO v_total
            FROM order_items oi
            WHERE oi.order_id = p_order_id;
            RETURN v_total;
        END;
        $$ LANGUAGE plpgsql STABLE;
        """
    )

    op.execute(
        """
        ALTER TABLE users ENABLE ROW LEVEL SECURITY;
        ALTER TABLE products ENABLE ROW LEVEL SECURITY;
        ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
        ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;
        ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
        ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
        ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;

        CREATE POLICY products_public_active_select ON products
            FOR SELECT USING (is_active = TRUE);
        CREATE POLICY knowledge_base_public_active_select ON knowledge_base
            FOR SELECT USING (is_active = TRUE);
        CREATE POLICY orders_guest_insert ON orders FOR INSERT WITH CHECK (TRUE);
        CREATE POLICY conversations_guest_insert ON conversations FOR INSERT WITH CHECK (TRUE);
        CREATE POLICY messages_insert ON messages FOR INSERT WITH CHECK (TRUE);
        """
    )


def downgrade() -> None:
    """Reverse initial schema."""
    op.execute(
        """
        DROP POLICY IF EXISTS messages_insert ON messages;
        DROP POLICY IF EXISTS conversations_guest_insert ON conversations;
        DROP POLICY IF EXISTS orders_guest_insert ON orders;
        DROP POLICY IF EXISTS knowledge_base_public_active_select ON knowledge_base;
        DROP POLICY IF EXISTS products_public_active_select ON products;

        DROP FUNCTION IF EXISTS calculate_order_total(UUID);
        DROP FUNCTION IF EXISTS get_customer_orders(VARCHAR, INTEGER);
        DROP FUNCTION IF EXISTS match_documents(VECTOR(768), FLOAT, INT, TEXT);

        DROP TRIGGER IF EXISTS trigger_knowledge_base_updated_at ON knowledge_base;
        DROP TRIGGER IF EXISTS trigger_conversations_updated_at ON conversations;
        DROP TRIGGER IF EXISTS trigger_orders_updated_at ON orders;
        DROP TRIGGER IF EXISTS trigger_products_updated_at ON products;
        DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;
        DROP FUNCTION IF EXISTS update_updated_at_column();

        DROP TRIGGER IF EXISTS trigger_set_order_number ON orders;
        DROP FUNCTION IF EXISTS set_order_number();
        DROP FUNCTION IF EXISTS generate_order_number();

        DROP TABLE IF EXISTS knowledge_base;
        DROP TABLE IF EXISTS messages;
        ALTER TABLE orders DROP CONSTRAINT IF EXISTS fk_orders_referral_conversation;
        DROP TABLE IF EXISTS conversations;
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS users;
        """
    )
