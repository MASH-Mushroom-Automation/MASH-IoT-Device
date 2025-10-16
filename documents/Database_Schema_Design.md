# M.A.S.H. Database Schema Design
## Complete PostgreSQL Schema with Optimization

### Core Entity Tables

```sql
-- Users (Clerk Integration)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'seller', 'moderator')),
    profile_image_url TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- User Profiles (Extended Information)
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date_of_birth DATE,
    gender VARCHAR(20),
    address JSONB,
    bio TEXT,
    website VARCHAR(255),
    social_links JSONB DEFAULT '{}',
    notification_preferences JSONB DEFAULT '{}',
    privacy_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Devices (IoT Integration)
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    device_type VARCHAR(100) NOT NULL,
    model VARCHAR(100),
    serial_number VARCHAR(255) UNIQUE,
    mac_address VARCHAR(17) UNIQUE,
    firmware_version VARCHAR(50),
    hardware_version VARCHAR(50),
    status VARCHAR(50) DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'error', 'maintenance')),
    configuration JSONB DEFAULT '{}',
    location JSONB,
    timezone VARCHAR(50) DEFAULT 'UTC',
    last_seen TIMESTAMP,
    last_heartbeat TIMESTAMP,
    uptime_seconds BIGINT DEFAULT 0,
    total_downtime_seconds BIGINT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Sensor Types (Reference Table)
CREATE TABLE sensor_types (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL,
    unit VARCHAR(20) NOT NULL,
    min_value DECIMAL(15,4),
    max_value DECIMAL(15,4),
    accuracy DECIMAL(10,4),
    description TEXT,
    calibration_interval_days INTEGER DEFAULT 365,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sensor Readings (Time-Series Data)
CREATE TABLE sensor_readings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    sensor_type_id UUID REFERENCES sensor_types(id),
    value DECIMAL(15,4) NOT NULL,
    quality_indicator VARCHAR(20) DEFAULT 'good' CHECK (quality_indicator IN ('good', 'uncertain', 'bad')),
    timestamp TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (timestamp);

-- Device Commands (Control System)
CREATE TABLE device_commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    command_type VARCHAR(100) NOT NULL,
    command_data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'acknowledged', 'completed', 'failed', 'timeout')),
    sent_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product Categories
CREATE TABLE product_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES product_categories(id),
    image_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES product_categories(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    short_description TEXT,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    compare_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    min_stock_level INTEGER DEFAULT 5,
    max_stock_level INTEGER DEFAULT 1000,
    weight DECIMAL(8,2),
    dimensions JSONB,
    sku VARCHAR(100) UNIQUE,
    barcode VARCHAR(100),
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'inactive', 'out_of_stock', 'discontinued')),
    featured BOOLEAN DEFAULT FALSE,
    seo_title VARCHAR(255),
    seo_description TEXT,
    tags TEXT[],
    images JSONB DEFAULT '[]',
    variants JSONB DEFAULT '[]',
    attributes JSONB DEFAULT '{}',
    shipping_info JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL
);

-- Orders
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    email VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    payment_status VARCHAR(50) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed', 'refunded', 'partially_refunded')),
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
    tax_amount DECIMAL(10,2) DEFAULT 0 CHECK (tax_amount >= 0),
    shipping_amount DECIMAL(10,2) DEFAULT 0 CHECK (shipping_amount >= 0),
    discount_amount DECIMAL(10,2) DEFAULT 0 CHECK (discount_amount >= 0),
    total_amount DECIMAL(10,2) NOT NULL CHECK (total_amount >= 0),
    currency VARCHAR(3) DEFAULT 'PHP',
    billing_address JSONB NOT NULL,
    shipping_address JSONB NOT NULL,
    shipping_method JSONB,
    payment_method JSONB,
    notes TEXT,
    internal_notes TEXT,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP,
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Items
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,
    product_sku VARCHAR(100),
    variant_info JSONB,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    total_price DECIMAL(10,2) NOT NULL CHECK (total_price >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts & Notifications
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID REFERENCES devices(id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    threshold_config JSONB,
    trigger_value DECIMAL(15,4),
    current_value DECIMAL(15,4),
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP,
    auto_resolve BOOLEAN DEFAULT FALSE,
    escalation_level INTEGER DEFAULT 1,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    channels VARCHAR(50)[] DEFAULT '{}', -- email, sms, push, in_app
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    delivery_status JSONB DEFAULT '{}',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- System Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id VARCHAR(255),
    request_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Indexes and Performance Optimization

```sql
-- Performance Indexes
CREATE INDEX CONCURRENTLY idx_users_clerk_id ON users(clerk_user_id);
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
CREATE INDEX CONCURRENTLY idx_users_role ON users(role) WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY idx_devices_user_id ON devices(user_id);
CREATE INDEX CONCURRENTLY idx_devices_status ON devices(status);
CREATE INDEX CONCURRENTLY idx_devices_type ON devices(device_type);
CREATE INDEX CONCURRENTLY idx_devices_last_seen ON devices(last_seen);

CREATE INDEX CONCURRENTLY idx_sensor_readings_device_timestamp ON sensor_readings(device_id, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_sensor_readings_type_timestamp ON sensor_readings(sensor_type_id, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_sensor_readings_timestamp ON sensor_readings(timestamp DESC);

CREATE INDEX CONCURRENTLY idx_products_seller ON products(seller_id) WHERE status = 'active';
CREATE INDEX CONCURRENTLY idx_products_category ON products(category_id) WHERE status = 'active';
CREATE INDEX CONCURRENTLY idx_products_status ON products(status);
CREATE INDEX CONCURRENTLY idx_products_featured ON products(featured) WHERE status = 'active';

CREATE INDEX CONCURRENTLY idx_orders_user ON orders(user_id);
CREATE INDEX CONCURRENTLY idx_orders_status ON orders(status);
CREATE INDEX CONCURRENTLY idx_orders_date ON orders(created_at DESC);
CREATE INDEX CONCURRENTLY idx_orders_number ON orders(order_number);

CREATE INDEX CONCURRENTLY idx_alerts_device ON alerts(device_id);
CREATE INDEX CONCURRENTLY idx_alerts_severity ON alerts(severity) WHERE resolved = FALSE;
CREATE INDEX CONCURRENTLY idx_alerts_unacknowledged ON alerts(acknowledged) WHERE acknowledged = FALSE;

CREATE INDEX CONCURRENTLY idx_notifications_user ON notifications(user_id) WHERE read = FALSE;
CREATE INDEX CONCURRENTLY idx_notifications_sent ON notifications(sent, created_at DESC);
```

### Prisma Schema Configuration

```prisma
// schema.prisma
generator client {
  provider = "prisma-client-js"
  previewFeatures = ["fullTextSearch", "postgresqlExtensions"]
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  extensions = [uuidOssp(map: "uuid-ossp")]
}

model User {
  id                String    @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  clerkUserId       String    @unique @map("clerk_user_id")
  email             String    @unique
  firstName         String?   @map("first_name")
  lastName          String?   @map("last_name")
  phone             String?
  role              Role      @default(USER)
  profileImageUrl   String?   @map("profile_image_url")
  emailVerified     Boolean   @default(false) @map("email_verified")
  phoneVerified     Boolean   @default(false) @map("phone_verified")
  isActive          Boolean   @default(true) @map("is_active")
  lastLogin         DateTime? @map("last_login")
  preferences       Json      @default("{}")
  metadata          Json      @default("{}")
  createdAt         DateTime  @default(now()) @map("created_at")
  updatedAt         DateTime  @updatedAt @map("updated_at")
  deletedAt         DateTime? @map("deleted_at")

  // Relations
  profile           UserProfile?
  devices           Device[]
  products          Product[]
  orders            Order[]
  notifications     Notification[]
  auditLogs         AuditLog[]
  acknowledgedAlerts Alert[] @relation("AlertAcknowledgedBy")
  resolvedAlerts    Alert[] @relation("AlertResolvedBy")

  @@map("users")
}

enum Role {
  ADMIN
  USER
  SELLER
  MODERATOR
}

model Device {
  id                  String    @id @default(dbgenerated("gen_random_uuid()")) @db.Uuid
  userId              String    @map("user_id") @db.Uuid
  name                String
  description         String?
  deviceType          String    @map("device_type")
  model               String?
  serialNumber        String?   @unique @map("serial_number")
  macAddress          String?   @unique @map("mac_address")
  firmwareVersion     String?   @map("firmware_version")
  hardwareVersion     String?   @map("hardware_version")
  status              DeviceStatus @default(OFFLINE)
  configuration       Json      @default("{}")
  location            Json?
  timezone            String    @default("UTC")
  lastSeen            DateTime? @map("last_seen")
  lastHeartbeat       DateTime? @map("last_heartbeat")
  uptimeSeconds       BigInt    @default(0) @map("uptime_seconds")
  totalDowntimeSeconds BigInt   @default(0) @map("total_downtime_seconds")
  createdAt           DateTime  @default(now()) @map("created_at")
  updatedAt           DateTime  @updatedAt @map("updated_at")
  deletedAt           DateTime? @map("deleted_at")

  // Relations
  user                User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  sensorReadings      SensorReading[]
  deviceCommands      DeviceCommand[]
  alerts              Alert[]

  @@map("devices")
}

enum DeviceStatus {
  ONLINE
  OFFLINE
  ERROR
  MAINTENANCE
}
```

### Database Migration Strategy

1. **Initial Schema Setup**
   - Create all tables with proper constraints
   - Add performance indexes
   - Set up foreign key relationships

2. **Data Seeding**
   - Add default sensor types
   - Create admin user accounts
   - Initialize product categories

3. **Performance Optimization**
   - Configure connection pooling
   - Set up query optimization
   - Implement caching strategies

4. **Backup and Recovery**
   - Automated daily backups
   - Point-in-time recovery setup
   - Disaster recovery procedures