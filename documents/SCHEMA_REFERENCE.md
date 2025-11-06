# MASH Backend - Database Schema Reference

Quick reference guide for all database models and their fields.

---

## 📑 Table of Contents

1. [User & Authentication](#user--authentication)
2. [IoT & Devices](#iot--devices)
3. [E-Commerce](#e-commerce)
4. [Alerts & Notifications](#alerts--notifications)
5. [Analytics & Reports](#analytics--reports)
6. [Import/Export](#importexport)
7. [API Gateway](#api-gateway)
8. [System & Audit](#system--audit)
9. [Enums](#enums)

---

## User & Authentication

### User (`users`)
**Key Fields:** `id`, `clerkId*`, `email*`, `username`, `password`, `firstName`, `lastName`, `role`, `isActive`, `twoFactorEnabled`

**Relations:** addresses, apiKeys, devices, orders, payments, sessions, notifications, alerts

**Indexes:** `createdAt`, `isActive+role`, `email+isActive`

---

### Session (`sessions`)
**Key Fields:** `id`, `userId`, `clerkSessionId`, `token*`, `status`, `deviceInfo`, `ipAddress`, `expiresAt`

**Relations:** user

---

### ApiKey (`api_keys`)
**Key Fields:** `id`, `userId`, `name`, `keyHash*`, `keyPrefix`, `scopes`, `expiresAt`

**Relations:** user

---

### Address (`addresses`)
**Key Fields:** `id`, `userId`, `type`, `firstName`, `lastName`, `street1`, `city`, `state`, `postalCode`, `country`, `isDefault`

**Relations:** user

---

### Permission (`permissions`)
**Key Fields:** `id`, `resource`, `action`, `description`

**Unique:** `[resource, action]`

---

### Role (`roles`)
**Key Fields:** `id`, `name*`, `description`, `isSystem`

**Relations:** rolePermissions, userRoleAssignments

---

### UserRoleAssignment (`user_role_assignments`)
**Key Fields:** `id`, `userId`, `roleId`, `grantedBy`, `grantedAt`

**Unique:** `[userId, roleId]`

---

### RolePermission (`role_permissions`)
**Key Fields:** `id`, `roleId`, `permissionId`

**Unique:** `[roleId, permissionId]`

---

## IoT & Devices

### Device (`devices`)
**Key Fields:** `id`, `name`, `type`, `serialNumber*`, `status`, `userId`, `location`, `firmware`, `ipAddress`, `macAddress`, `lastSeen`, `isActive`

**Relations:** user, sensors, sensorData, alerts, deviceCommands, healthRecords, pushSubscriptions

**Indexes:** `userId+status+isActive`, `status+lastSeen`, `createdAt`

---

### Sensor (`sensors`)
**Key Fields:** `id`, `deviceId`, `type`, `name`, `unit`, `minValue`, `maxValue`, `calibration`, `isActive`

**Relations:** device, sensorData, alerts

---

### SensorData (`sensor_data`)
**Key Fields:** `id`, `deviceId`, `sensorId`, `userId`, `type`, `value`, `unit`, `quality`, `timestamp`

**Relations:** device, sensor, user

**Indexes:** `deviceId+timestamp`, `type+timestamp`

---

### DeviceCommand (`device_commands`)
**Key Fields:** `id`, `deviceId`, `command`, `parameters`, `status`, `response`, `sentAt`, `acknowledgedAt`

**Relations:** device

---

### SensorAlert (`sensor_alerts`)
**Key Fields:** `id`, `deviceId`, `sensorId`, `type`, `severity`, `title`, `message`, `threshold`, `isActive`, `isResolved`, `resolvedAt`

**Relations:** device, sensor

---

### DeviceHealth (`device_health`)
**Key Fields:** `id`, `deviceId`, `timestamp`, `status`, `cpuUsage`, `memoryUsage`, `diskUsage`, `temperature`, `batteryLevel`, `networkLatency`, `uptime`, `errorCount`, `metadata`

**Relations:** device

**Indexes:** `deviceId+timestamp`, `status`, `timestamp`

---

## E-Commerce

### Product (`products`)
**Key Fields:** `id`, `name`, `slug*`, `sku`, `price`, `comparePrice`, `costPrice`, `stock`, `minStock`, `images`, `categories`, `tags`, `isActive`, `isFeatured`, `isDeleted`

**Relations:** orderItems

**Indexes:** `isActive+isFeatured+createdAt`, `slug+isActive`, `stock+minStock`

---

### Category (`categories`)
**Key Fields:** `id`, `name`, `slug*`, `parentId`, `imageUrl`, `isActive`, `sortOrder`

**Relations:** parent (Category), children (Category[])

**Indexes:** `isActive+sortOrder`, `parentId+isActive`

---

### Order (`orders`)
**Key Fields:** `id`, `orderNumber*`, `userId`, `status`, `subtotal`, `tax`, `shipping`, `discount`, `total`, `currency`, `shippingAddress`, `billingAddress`, `trackingNumber`, `shippedAt`, `deliveredAt`

**Relations:** user, orderItems, payments

**Indexes:** `userId+status+createdAt`, `status+createdAt`, `orderNumber`

---

### OrderItem (`order_items`)
**Key Fields:** `id`, `orderId`, `productId`, `quantity`, `price`, `total`

**Relations:** order, product

**Indexes:** `productId`, `orderId`, `productId+orderId`

---

### Payment (`payments`)
**Key Fields:** `id`, `orderId`, `userId`, `amount`, `currency`, `status`, `method`, `transactionId*`, `gatewayResponse`, `processedAt`, `refundedAt`

**Relations:** order, user

**Indexes:** `userId+status+createdAt`, `status+createdAt`, `transactionId`

---

## Alerts & Notifications

### AlertRule (`alert_rules`)
**Key Fields:** `id`, `name`, `category`, `priority`, `eventType`, `condition`, `activeHours`, `cooldownMinutes`, `isActive`, `createdBy`

**Relations:** creator (User), updater (User), recipients, alerts

**Indexes:** `eventType`, `isActive`, `category+priority`

---

### AlertRuleRecipient (`alert_rule_recipients`)
**Key Fields:** `id`, `ruleId`, `recipientType`, `recipientId`, `role`, `email`, `phone`, `enableEmail`, `enableSms`, `enablePush`, `enableInApp`

**Relations:** rule (AlertRule), user

---

### Alert (`alerts`)
**Key Fields:** `id`, `ruleId`, `title`, `message`, `category`, `priority`, `severity`, `status`, `eventType`, `eventId`, `fingerprint`, `groupKey`, `occurrenceCount`, `triggeredAt`, `acknowledgedAt`, `resolvedAt`

**Relations:** rule (AlertRule), notifications, acknowledgments

**Indexes:** `ruleId`, `status`, `priority`, `fingerprint`, `triggeredAt`

---

### Notification (`notifications`)
**Key Fields:** `id`, `alertId`, `userId`, `channel`, `status`, `recipientEmail`, `recipientPhone`, `subject`, `body`, `templateId`, `queuedAt`, `sentAt`, `deliveredAt`, `retryCount`, `provider`

**Relations:** alert, user, template

**Indexes:** `alertId`, `userId`, `status`, `channel`, `userId+status+createdAt`

---

### AlertAcknowledgment (`alert_acknowledgments`)
**Key Fields:** `id`, `alertId`, `userId`, `action`, `comment`, `metadata`

**Relations:** alert, user

---

### NotificationTemplate (`notification_templates`)
**Key Fields:** `id`, `name*`, `category`, `channel`, `subject`, `body`, `variables`, `isActive`, `createdBy`

**Relations:** creator (User), notifications

---

### AlertEscalationPolicy (`alert_escalation_policies`)
**Key Fields:** `id`, `name`, `priority[]`, `category[]`, `unacknowledgedMin`, `steps`, `isActive`

---

### UserNotification (`user_notifications`)
**Key Fields:** `id`, `userId`, `type`, `title`, `message`, `data`, `isRead`, `readAt`

**Relations:** user

---

## Analytics & Reports

### Report (`reports`)
**Key Fields:** `id`, `name`, `type`, `configuration`, `schedule`, `isActive`, `createdBy`

**Relations:** executions, subscriptions

**Indexes:** `type`, `createdBy`, `isActive+type`

---

### ReportExecution (`report_executions`)
**Key Fields:** `id`, `reportId`, `status`, `startedAt`, `completedAt`, `duration`, `resultData`, `resultUrl`, `errorMessage`, `executedBy`

**Relations:** report

**Indexes:** `reportId`, `status`, `startedAt`

---

### ReportSubscription (`report_subscriptions`)
**Key Fields:** `id`, `reportId`, `userId`, `channel`, `frequency`, `isActive`, `lastSentAt`

**Relations:** report

**Unique:** `[reportId, userId, channel]`

---

### SearchLog (`search_logs`)
**Key Fields:** `id`, `query`, `index`, `resultsCount`, `took`, `filters`, `sort`, `userId`, `clickedResult`, `isSlowQuery`

**Indexes:** `query`, `createdAt`, `isSlowQuery+took`, `userId+createdAt`

---

## Import/Export

### ImportExportJob (`import_export_jobs`)
**Key Fields:** `id`, `type`, `entityType`, `status`, `priority`, `fileName`, `fileFormat`, `fileSize`, `fileUrl`, `resultFileUrl`, `totalRecords`, `processedRecords`, `successCount`, `failureCount`, `progressPercent`, `createdBy`

**Relations:** createdByUser (User), errors

**Indexes:** `status+createdAt`, `entityType+type`, `createdBy`

---

### ImportExportError (`import_export_errors`)
**Key Fields:** `id`, `jobId`, `rowNumber`, `columnName`, `errorType`, `severity`, `errorCode`, `message`, `suggestion`, `originalValue`

**Relations:** job

**Indexes:** `jobId+severity`

---

### ImportExportTemplate (`import_export_templates`)
**Key Fields:** `id`, `name`, `entityType`, `fileFormat`, `headers`, `sampleData`, `validation`, `isActive`, `createdBy`

**Indexes:** `entityType+fileFormat`

---

## API Gateway

### ApiGatewayConfig (`api_gateway_configs`)
**Key Fields:** `id`, `serviceName*`, `basePath`, `targetUrl`, `healthCheckUrl`, `timeout`, `retryAttempts`, `circuitBreaker`, `loadBalancing`, `isActive`, `priority`

---

### RateLimitOverride (`rate_limit_overrides`)
**Key Fields:** `id`, `userId`, `apiKey`, `endpoint`, `requestLimit`, `timeWindowMs`, `strategy`, `priority`, `reason`, `expiresAt`

**Relations:** user

**Unique:** `[userId, endpoint]`

---

### ApiUsageLog (`api_usage_logs`)
**Key Fields:** `id`, `userId`, `apiKey`, `endpoint`, `method`, `version`, `statusCode`, `responseTime`, `requestSize`, `responseSize`, `ipAddress`, `rateLimitHit`, `throttled`, `queueTime`

**Relations:** user

**Indexes:** `userId+timestamp`, `endpoint+timestamp`, `timestamp`, `apiKey`

---

### RequestQueue (`request_queues`)
**Key Fields:** `id`, `userId`, `endpoint`, `method`, `priority`, `payload`, `headers`, `status`, `estimatedWaitMs`, `queuedAt`, `processedAt`, `expiresAt`, `retryCount`

**Relations:** user

**Indexes:** `status+priority+queuedAt`, `userId`, `expiresAt`

---

### ApiVersionUsage (`api_version_usage`)
**Key Fields:** `id`, `version`, `endpoint`, `userId`, `requestCount`, `lastUsedAt`

**Relations:** user

**Unique:** `[version, endpoint, userId]`

---

### CircuitBreakerState (`circuit_breaker_states`)
**Key Fields:** `id`, `serviceName*`, `state`, `failureCount`, `successCount`, `lastFailureAt`, `lastSuccessAt`, `nextRetryAt`, `openedAt`

**Indexes:** `state`

---

### PushSubscription (`push_subscriptions`)
**Key Fields:** `id`, `userId`, `deviceId`, `endpoint*`, `keys`, `userAgent`, `isActive`

**Relations:** user, device

**Indexes:** `userId`, `deviceId`, `isActive`

---

## System & Audit

### SystemConfig (`system_config`)
**Key Fields:** `id`, `key*`, `value`, `description`, `category`, `isPublic`

**Indexes:** `category+isPublic`, `key+isPublic`

---

### AuditLog (`audit_logs`)
**Key Fields:** `id`, `userId`, `action`, `entity`, `entityId`, `oldValues`, `newValues`, `ipAddress`, `userAgent`, `timestamp`

**Indexes:** `userId+timestamp`, `entity+entityId`

---

### SecurityLog (`security_logs`)
**Key Fields:** `id`, `userId`, `event`, `severity`, `ipAddress`, `userAgent`, `metadata`, `timestamp`

**Indexes:** `userId+timestamp`, `event`, `severity`, `timestamp`

---

### RateLimitLog (`rate_limit_logs`)
**Key Fields:** `id`, `identifier`, `endpoint`, `count`, `windowStart`, `windowEnd`, `blocked`

**Unique:** `[identifier, endpoint, windowStart]`

**Indexes:** `identifier+windowStart`, `endpoint`

---

## Enums

### UserRole
`USER`, `ADMIN`, `SUPER_ADMIN`, `GROWER`, `BUYER`

### SessionStatus
`ACTIVE`, `EXPIRED`, `REVOKED`

### DeviceType
`MUSHROOM_CHAMBER`, `ENVIRONMENTAL_SENSOR`, `IRRIGATION_SYSTEM`, `HVAC_CONTROLLER`, `CAMERA`, `pH_SENSOR`, `HUMIDITY_CONTROLLER`

### DeviceStatus
`ONLINE`, `OFFLINE`, `MAINTENANCE`, `ERROR`

### DeviceHealthStatus
`HEALTHY`, `WARNING`, `CRITICAL`, `OFFLINE`, `MAINTENANCE`

### OrderStatus
`PENDING`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`, `REFUNDED`

### PaymentStatus
`PENDING`, `PAID`, `FAILED`, `REFUNDED`

### PaymentMethod
`CREDIT_CARD`, `DEBIT_CARD`, `PAYPAL`, `GCASH`, `MAYA`, `BANK_TRANSFER`

### NotificationType
`ALERT`, `INFO`, `WARNING`, `SUCCESS`, `DEVICE_STATUS`, `ORDER_UPDATE`, `PAYMENT_UPDATE`

### AlertCategory
`SYSTEM`, `SECURITY`, `BUSINESS`, `USER`, `SENSOR`, `ORDER`, `PAYMENT`

### AlertPriority
`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`

### AlertStatus
`PENDING`, `SENT`, `ACKNOWLEDGED`, `RESOLVED`, `ESCALATED`, `SNOOZED`, `CANCELLED`

### NotificationChannel
`EMAIL`, `SMS`, `PUSH`, `IN_APP`, `WEBHOOK`

### NotificationStatus
`PENDING`, `QUEUED`, `SENDING`, `SENT`, `DELIVERED`, `FAILED`, `BOUNCED`, `RETRYING`, `CANCELLED`

### RecipientType
`USER`, `ROLE`, `EMAIL`, `PHONE`

### AcknowledgmentAction
`ACKNOWLEDGED`, `RESOLVED`, `ESCALATED`, `SNOOZED`, `COMMENTED`, `CANCELLED`

### ReportType
`SALES`, `REVENUE`, `USERS`, `PRODUCTS`, `ORDERS`, `DEVICES`, `CUSTOM`

### ExecutionStatus
`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`

### SubscriptionFrequency
`DAILY`, `WEEKLY`, `MONTHLY`, `REAL_TIME`

### JobType
`IMPORT`, `EXPORT`

### EntityType
`PRODUCT`, `ORDER`, `USER`, `CATEGORY`, `SELLER`, `BUYER`, `TRANSACTION`, `INVENTORY`

### JobStatus
`QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED`

### JobPriority
`URGENT`, `NORMAL`, `LOW`

### FileFormat
`CSV`, `EXCEL`, `JSON`, `XML`

### ErrorType
`VALIDATION`, `CONSTRAINT`, `FORMAT`, `BUSINESS_RULE`

### ErrorSeverity
`ERROR`, `WARNING`

### LoadBalancingStrategy
`ROUND_ROBIN`, `LEAST_CONNECTIONS`, `WEIGHTED_ROUND_ROBIN`, `IP_HASH`, `HEALTH_BASED`

### RateLimitStrategy
`TOKEN_BUCKET`, `LEAKY_BUCKET`, `FIXED_WINDOW`, `SLIDING_WINDOW`, `ADAPTIVE`

### RequestQueueStatus
`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `EXPIRED`

### CircuitBreakerStateEnum
`CLOSED`, `OPEN`, `HALF_OPEN`

---

## Legend

- `*` = Unique field
- `[]` = Array field
- Fields marked with `+` in indexes are composite indexes
