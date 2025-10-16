# MASH Backend - Comprehensive Testing Guide

This document provides a complete guide to the automated testing suite for the MASH (Mushroom Automation System Hub) Backend.

## 🧪 Test Suite Overview

The MASH Backend includes a comprehensive testing suite with multiple layers of testing to ensure reliability, performance, and maintainability.

### Test Categories

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions and API endpoints
3. **End-to-End Tests** - Test complete user workflows
4. **Performance Tests** - Test system performance and scalability
5. **System Tests** - Test the entire system with Postman collections

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- PostgreSQL (for integration/e2e tests)
- Redis (for queue and caching tests)
- Firebase project (for authentication tests)

### Installation

```bash
# Install dependencies
npm install

# Set up test environment
cp .env.example .env.test

# Run database migrations
npm run prisma:deploy
```

### Running Tests

```bash
# Run all tests
npm run test:all

# Run specific test types
npm run test:unit          # Unit tests only
npm run test:integration   # Integration tests only
npm run test:e2e          # End-to-end tests only
npm run test:performance  # Performance tests only

# Run with coverage
npm run test:coverage

# Run CI tests (includes linting)
npm run test:ci
```

## 📁 Test Structure

```
test/
├── setup.ts                          # Global test setup and utilities
├── jest.config.js                    # Jest configuration
├── jest-e2e.json                     # E2E test configuration
├── unit/                             # Unit tests
│   ├── auth.service.spec.ts         # Auth service unit tests
│   ├── auth.controller.spec.ts      # Auth controller unit tests
│   ├── users.controller.spec.ts     # Users controller unit tests
│   └── app.controller.spec.ts       # App controller unit tests
├── integration/                      # Integration tests
│   ├── auth.integration.spec.ts     # Auth API integration tests
│   └── users.integration.spec.ts    # Users API integration tests
├── e2e/                              # End-to-end tests
│   ├── complete-auth-flow.e2e-spec.ts  # Complete authentication workflow
│   └── system-health.e2e-spec.ts    # System health and monitoring
├── performance/                      # Performance tests
│   └── api-performance.spec.ts      # API performance benchmarks
└── scripts/                          # Test utilities and runners
    ├── test-runner.ts               # Comprehensive test runner
    └── ci-test.sh                   # CI/CD test script
```

## 🔧 Test Configuration

### Environment Variables

Create a `.env.test` file with the following variables:

```env
NODE_ENV=test
JWT_SECRET=test-jwt-secret-key
DATABASE_URL=postgresql://test:test@localhost:5432/mash_test
REDIS_HOST=localhost
REDIS_PORT=6379
FIREBASE_PROJECT_ID=test-project
FIREBASE_AUTH_EMULATOR_HOST=127.0.0.1:9099
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=test
SMTP_PASS=test
SMTP_FROM=test@example.com
```

### Jest Configuration

The test suite uses Jest with the following configuration:

- **Test Environment**: Node.js
- **Coverage Threshold**: 80% for branches, functions, lines, and statements
- **Timeout**: 30 seconds per test
- **Setup**: Global test setup with database and Firebase initialization

## 🧩 Test Types

### Unit Tests

Unit tests focus on testing individual components in isolation using mocks and stubs.

**Coverage:**
- Auth Service (`auth.service.spec.ts`)
- Auth Controller (`auth.controller.spec.ts`)
- Users Controller (`users.controller.spec.ts`)
- App Controller (`app.controller.spec.ts`)

**Key Features:**
- Mocked dependencies (Prisma, Firebase, Email Queue)
- Isolated component testing
- Fast execution
- High coverage of business logic

### Integration Tests

Integration tests verify that different components work together correctly.

**Coverage:**
- Authentication API endpoints
- User management API endpoints
- Database operations
- External service integrations

**Key Features:**
- Real database connections
- Mocked external services
- API endpoint testing
- Data persistence verification

### End-to-End Tests

E2E tests simulate complete user workflows from start to finish.

**Coverage:**
- Complete authentication flow (registration → verification → login)
- User profile management
- System health checks
- Error handling scenarios

**Key Features:**
- Full application setup
- Real database operations
- Complete user journeys
- Error scenario testing

### Performance Tests

Performance tests ensure the system meets performance requirements.

**Coverage:**
- Response time benchmarks
- Concurrent request handling
- Memory usage monitoring
- Database performance
- Rate limiting efficiency

**Key Features:**
- Response time assertions
- Load testing scenarios
- Memory usage monitoring
- Performance regression detection

## 🎯 Test Scenarios

### Authentication Flow Tests

1. **User Registration**
   - Firebase token exchange
   - User creation in database
   - Email verification code generation

2. **Email Verification**
   - Verification code sending
   - Code validation
   - User account activation

3. **User Login**
   - Token refresh
   - Protected route access
   - Session management

4. **Error Scenarios**
   - Invalid tokens
   - Expired codes
   - Rate limiting
   - Database errors

### System Health Tests

1. **Health Endpoints**
   - Basic health check
   - Detailed system health
   - Ping endpoint

2. **Database Connectivity**
   - Connection verification
   - CRUD operations
   - Performance benchmarks

3. **External Services**
   - Redis connectivity
   - Firebase integration
   - Email service

## 📊 Coverage Reports

### Running Coverage

```bash
npm run test:coverage
```

### Coverage Reports

- **Terminal**: Real-time coverage during test execution
- **HTML**: Detailed report at `coverage/lcov-report/index.html`
- **LCOV**: Machine-readable format at `coverage/lcov.info`

### Coverage Thresholds

- **Branches**: 80%
- **Functions**: 80%
- **Lines**: 80%
- **Statements**: 80%

## 🚀 CI/CD Integration

### GitHub Actions

The project includes a comprehensive GitHub Actions workflow (`.github/workflows/test.yml`) that runs:

1. **Main Test Suite**
   - Unit tests
   - Integration tests
   - E2E tests
   - Coverage reporting

2. **Security Scans**
   - npm audit
   - Snyk security scanning

3. **Performance Tests**
   - API performance benchmarks
   - Load testing

### Local CI Simulation

```bash
# Run CI tests locally
npm run test:ci

# Run with Docker services
./test/scripts/ci-test.sh
```

## 🔍 Debugging Tests

### Debug Mode

```bash
# Run tests in debug mode
npm run test:debug

# Run specific test file
npm test -- --testNamePattern="AuthService"
```

### Common Issues

1. **Database Connection Issues**
   - Ensure PostgreSQL is running
   - Check connection string in `.env.test`
   - Verify database permissions

2. **Firebase Issues**
   - Ensure Firebase project is configured
   - Check Firebase emulator setup
   - Verify service account keys

3. **Redis Issues**
   - Ensure Redis is running
   - Check Redis connection settings
   - Verify Redis permissions

## 📈 Performance Benchmarks

### Response Time Targets

- **Health Endpoints**: < 100ms
- **Authentication**: < 500ms
- **Protected Routes**: < 300ms
- **Database Operations**: < 1000ms

### Load Testing

- **Concurrent Requests**: 100+ simultaneous requests
- **Memory Usage**: < 50MB increase under load
- **Database Pool**: Efficient connection management

## 🛠️ Test Utilities

### Test Helpers

The test suite includes utility functions in `test/setup.ts`:

- `createTestUser()` - Create test users
- `cleanupTestUser()` - Clean up test data
- `generateMockFirebaseToken()` - Generate test tokens
- `waitForRedis()` - Wait for Redis readiness

### Mocking

Common mocks used throughout the test suite:

- **PrismaService**: Database operations
- **FirebaseAdminService**: Firebase authentication
- **EmailQueueService**: Email operations
- **JwtService**: Token operations

## 📝 Writing New Tests

### Test Structure

```typescript
describe('ComponentName', () => {
  let component: ComponentName;
  let mockDependency: jest.Mocked<DependencyType>;

  beforeEach(async () => {
    // Setup test module and mocks
  });

  describe('methodName', () => {
    it('should handle success case', async () => {
      // Arrange
      // Act
      // Assert
    });

    it('should handle error case', async () => {
      // Arrange
      // Act
      // Assert
    });
  });
});
```

### Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Naming**: Use descriptive test names
3. **Mock External Dependencies**: Don't rely on external services
4. **Test Edge Cases**: Include error scenarios
5. **Performance Awareness**: Keep tests fast and efficient

## 🔧 Troubleshooting

### Common Commands

```bash
# Clear test database
npm run prisma:reset

# Rebuild test database
npm run prisma:deploy

# Run tests with verbose output
npm test -- --verbose

# Run specific test pattern
npm test -- --testNamePattern="AuthService"
```

### Log Files

- **Test Results**: `test-results.json`
- **Coverage Reports**: `coverage/` directory
- **Performance Results**: `performance-results.json`

## 📚 Additional Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [NestJS Testing](https://docs.nestjs.com/fundamentals/testing)
- [Supertest Documentation](https://github.com/visionmedia/supertest)
- [Prisma Testing](https://www.prisma.io/docs/guides/testing)

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Maintainer**: MASH Development Team

