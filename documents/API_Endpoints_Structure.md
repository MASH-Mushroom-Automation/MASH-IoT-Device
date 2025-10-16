# M.A.S.H. API Endpoints Structure
## Complete RESTful API Design

### Authentication Endpoints (Clerk Integration)

```typescript
// Authentication with Clerk
POST /api/auth/webhook          // Clerk webhook handler for user sync
GET  /api/auth/me              // Get current authenticated user
PUT  /api/auth/profile         // Update user profile
POST /api/auth/logout          // Logout user session
GET  /api/auth/session         // Get session information
```

### User Management Endpoints

```typescript
// User CRUD Operations
GET    /api/users              // Get all users (admin only)
GET    /api/users/:id          // Get user by ID
PUT    /api/users/:id          // Update user information
DELETE /api/users/:id          // Delete user (soft delete)
GET    /api/users/:id/devices  // Get user's devices
GET    /api/users/:id/orders   // Get user's order history
POST   /api/users/:id/suspend  // Suspend user account (admin)
POST   /api/users/:id/activate // Activate user account (admin)

// User Profile Management
GET  /api/users/:id/profile    // Get user profile
PUT  /api/users/:id/profile    // Update user profile
POST /api/users/:id/avatar     // Upload profile image
GET  /api/users/:id/preferences // Get user preferences
PUT  /api/users/:id/preferences // Update user preferences
```

### Device Management Endpoints

```typescript
// Device CRUD Operations
GET    /api/devices            // Get user's devices
POST   /api/devices            // Register new device
GET    /api/devices/:id        // Get device details
PUT    /api/devices/:id        // Update device configuration
DELETE /api/devices/:id        // Delete device
POST   /api/devices/:id/reset  // Factory reset device

// Device Control and Status
GET  /api/devices/:id/status   // Get real-time device status
POST /api/devices/:id/commands // Send command to device
GET  /api/devices/:id/commands // Get command history
PUT  /api/devices/:id/commands/:commandId // Update command status

// Device Configuration
GET  /api/devices/:id/config   // Get device configuration
PUT  /api/devices/:id/config   // Update device configuration
POST /api/devices/:id/firmware // Update device firmware
GET  /api/devices/:id/logs     // Get device logs
```

### Sensor Data Endpoints

```typescript
// Sensor Data Collection
POST /api/sensors/data         // Store sensor readings (MQTT handler)
GET  /api/sensors/data         // Get aggregated sensor data
GET  /api/sensors/data/:deviceId // Get device sensor data
GET  /api/sensors/data/:deviceId/latest // Get latest readings
GET  /api/sensors/data/:deviceId/history // Get historical data

// Sensor Analytics
GET  /api/sensors/analytics/:deviceId // Get sensor analytics
GET  /api/sensors/analytics/:deviceId/trends // Get data trends
GET  /api/sensors/analytics/:deviceId/alerts // Get alert triggers
POST /api/sensors/analytics/:deviceId/export // Export data

// Sensor Configuration
GET  /api/sensors/types        // Get available sensor types
GET  /api/sensors/:deviceId/calibration // Get calibration data
POST /api/sensors/:deviceId/calibrate   // Calibrate sensors
```

### Alert and Notification Endpoints

```typescript
// Alert Management
GET    /api/alerts             // Get user alerts
POST   /api/alerts             // Create custom alert
GET    /api/alerts/:id         // Get alert details
PUT    /api/alerts/:id         // Update alert configuration
DELETE /api/alerts/:id         // Delete alert
POST   /api/alerts/:id/acknowledge // Acknowledge alert
POST   /api/alerts/:id/resolve // Resolve alert

// Alert Configuration
GET  /api/alerts/config/:deviceId // Get alert configuration
PUT  /api/alerts/config/:deviceId // Update alert thresholds
POST /api/alerts/test/:deviceId   // Test alert system

// Notifications
GET    /api/notifications      // Get user notifications
PUT    /api/notifications/:id/read // Mark notification as read
DELETE /api/notifications/:id  // Delete notification
POST   /api/notifications/preferences // Update notification preferences
GET    /api/notifications/unread-count // Get unread count
```

### E-commerce Product Endpoints

```typescript
// Product Management
GET    /api/products           // Get all products (with filters)
POST   /api/products           // Create product (sellers only)
GET    /api/products/:id       // Get product details
PUT    /api/products/:id       // Update product
DELETE /api/products/:id       // Delete product (soft delete)
POST   /api/products/:id/images // Upload product images

// Product Categories
GET  /api/categories           // Get product categories
POST /api/categories           // Create category (admin)
PUT  /api/categories/:id       // Update category
GET  /api/categories/:id/products // Get products in category

// Inventory Management
GET  /api/products/:id/inventory // Get product inventory
PUT  /api/products/:id/inventory // Update stock levels
POST /api/products/:id/stock-alert // Set low stock alerts
GET  /api/inventory/low-stock   // Get low stock products
```

### Order Management Endpoints

```typescript
// Order Processing
POST /api/orders               // Create new order
GET  /api/orders               // Get user orders
GET  /api/orders/:id           // Get order details
PUT  /api/orders/:id/status    // Update order status
DELETE /api/orders/:id         // Cancel order

// Order Fulfillment
POST /api/orders/:id/ship      // Mark order as shipped
POST /api/orders/:id/deliver   // Mark order as delivered
POST /api/orders/:id/return    // Process return request
GET  /api/orders/:id/tracking  // Get tracking information

// Order Analytics
GET  /api/orders/analytics     // Get order analytics
GET  /api/orders/reports       // Generate order reports
GET  /api/orders/revenue       // Get revenue statistics
```

### Payment Processing Endpoints

```typescript
// Payment Gateway Integration
POST /api/payments/intent      // Create payment intent
POST /api/payments/confirm     // Confirm payment
GET  /api/payments/:id         // Get payment details
POST /api/payments/:id/refund  // Process refund
GET  /api/payments/methods     // Get available payment methods

// Payment Webhooks
POST /api/payments/webhooks/stripe  // Stripe webhook handler
POST /api/payments/webhooks/paypal  // PayPal webhook handler
POST /api/payments/webhooks/gcash   // GCash webhook handler
```

### File Upload and Media Endpoints

```typescript
// File Management
POST /api/files/upload         // Upload files
GET  /api/files/:id            // Get file details
DELETE /api/files/:id          // Delete file
GET  /api/files/:id/download   // Download file

// Image Processing
POST /api/images/upload        // Upload and process images
POST /api/images/resize        // Resize images
POST /api/images/optimize      // Optimize images
GET  /api/images/:id/variants  // Get image variants
```

### Admin Dashboard Endpoints

```typescript
// System Administration
GET  /api/admin/dashboard      // Get admin dashboard data
GET  /api/admin/users          // Get all users
GET  /api/admin/devices        // Get all devices
GET  /api/admin/orders         // Get all orders
GET  /api/admin/analytics      // Get system analytics

// User Management
POST /api/admin/users/:id/ban  // Ban user account
POST /api/admin/users/:id/unban // Unban user account
GET  /api/admin/users/reports  // Get user reports
POST /api/admin/users/bulk-action // Bulk user actions

// System Configuration
GET  /api/admin/config         // Get system configuration
PUT  /api/admin/config         // Update system configuration
GET  /api/admin/logs           // Get system logs
POST /api/admin/maintenance    // Enable maintenance mode
```

### Real-time WebSocket Events

```typescript
// WebSocket Event Handlers
'device:status'                // Device status updates
'sensor:data'                  // Real-time sensor data
'alert:new'                    // New alert notifications
'alert:resolved'               // Alert resolution updates
'order:status'                 // Order status changes
'notification:new'             // New notifications
'user:online'                  // User online status
'system:maintenance'           // System maintenance alerts

// WebSocket Authentication
'auth:connect'                 // Authenticate WebSocket connection
'room:join'                    // Join specific room
'room:leave'                   // Leave room
'heartbeat'                    // Connection heartbeat
```

### Health Check and Monitoring Endpoints

```typescript
// System Health
GET /api/health                // Basic health check
GET /api/health/detailed       // Detailed health status
GET /api/health/database       // Database connection status
GET /api/health/redis          // Redis connection status
GET /api/health/mqtt           // MQTT broker status

// Monitoring and Metrics
GET /api/metrics               // Application metrics
GET /api/metrics/performance   // Performance metrics
GET /api/metrics/usage         // Usage statistics
GET /api/status                // System status page
```

### API Response Standards

```typescript
// Success Response Format
{
  "success": true,
  "data": {},
  "message": "Operation completed successfully",
  "timestamp": "2025-10-02T10:00:00Z",
  "requestId": "req_123456"
}

// Error Response Format
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "timestamp": "2025-10-02T10:00:00Z",
  "requestId": "req_123456"
}

// Pagination Response Format
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5,
    "hasNext": true,
    "hasPrev": false
  }
}
```

### API Rate Limiting

```typescript
// Rate Limit Headers
"X-RateLimit-Limit": "100"      // Requests per window
"X-RateLimit-Remaining": "95"   // Remaining requests
"X-RateLimit-Reset": "1635724800" // Reset timestamp
"X-RateLimit-Window": "3600"    // Window size in seconds

// Rate Limit Tiers
- Public endpoints: 60 requests/hour
- Authenticated users: 1000 requests/hour
- Premium users: 5000 requests/hour
- Admin users: Unlimited
```

### API Versioning Strategy

```typescript
// URL Versioning
/api/v1/users                  // Version 1
/api/v2/users                  // Version 2

// Header Versioning
GET /api/users
Headers: {
  "API-Version": "1.0",
  "Accept": "application/vnd.mash.v1+json"
}

// Backward Compatibility
- Maintain v1 for 6 months after v2 release
- Deprecation warnings in response headers
- Migration guides for version updates
```