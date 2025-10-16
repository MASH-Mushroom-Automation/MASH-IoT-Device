# MASH Backend Setup and Testing Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- PostgreSQL database (Neon.tech configured)
- Redis server
- PowerShell (for Windows)

### 1. Environment Setup

```powershell
# Copy environment template
Copy-Item "env.template" ".env"

# Edit .env file with your actual values
notepad .env
```

### 2. Install Dependencies

```powershell
npm install
```

### 3. Database Setup

```powershell
# Generate Prisma client
npx prisma generate

# Push schema to database
npx prisma db push

# (Optional) Reset database
npx prisma db push --accept-data-loss
```

### 4. Start Services

```powershell
# Start Redis (if not running)
.\scripts\start-redis.ps1

# Start the application
npm run start:dev
```

## 🧪 Testing the System

### Quick Test
```powershell
.\scripts\quick-test.ps1
```

### Full Setup and Test
```powershell
.\scripts\setup-and-test.ps1
```

### Backend Health Tests
```powershell
.\scripts\test-backend.ps1
```

### Manual Testing

#### 1. Health Check Endpoints
```bash
# Basic health
curl http://localhost:3000/health

# Detailed health
curl http://localhost:3000/api/health

# Ping test
curl http://localhost:3000/ping
```

#### 2. Authentication Flow (with Postman)
1. Import `postman/01-Authentication-API.postman_collection.json`
2. Import `postman/MASH-backend.postman_environment.json`
3. Set `firebaseIdToken` in environment
4. Run the complete authentication flow

### Automated Testing

#### Unit Tests
```powershell
npm test
```

#### E2E Tests
```powershell
npm run test:e2e
```

#### Postman Collection Tests
```powershell
npm run postman:auth
```

## 🔧 System Architecture

### Database Schema
- **Users Table**: Complete user management with email verification
- **Groups Table**: User grouping and permissions
- **Refresh Tokens**: JWT token management
- **Login Sessions**: Session tracking
- **Audit Logs**: Security and activity logging

### Authentication Flow
1. **Firebase Token Exchange**: Exchange Firebase ID token for JWT
2. **Email Verification**: 6-digit code verification system
3. **JWT Management**: Access and refresh token handling
4. **User Profile**: Protected user information endpoints

### Email System
- **SMTP Configuration**: Gmail SMTP with app passwords
- **Queue Processing**: BullMQ with Redis for async email sending
- **Templates**: Professional HTML email templates
- **Rate Limiting**: Prevents email spam and abuse

### Security Features
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: Throttling on auth endpoints
- **Input Validation**: Class-validator for request validation
- **CORS Configuration**: Proper cross-origin handling
- **Error Handling**: Comprehensive error responses

## 📊 Health Monitoring

### Health Endpoints
- `GET /health` - Basic system status
- `GET /api/health` - Detailed system health with database and Redis status
- `GET /ping` - Simple connectivity test

### Monitoring Features
- Database connectivity status
- Redis queue status
- Memory usage tracking
- Response time monitoring
- Uptime tracking

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
Error: P1001: Can't reach database server
```
**Solution**: Check DATABASE_URL in .env file

#### 2. Redis Connection Error
```bash
Error: connect ECONNREFUSED 127.0.0.1:6379
```
**Solution**: Start Redis server with `.\scripts\start-redis.ps1`

#### 3. Email Not Sending
```bash
Error: Authentication failed
```
**Solution**: Verify Gmail app password in .env file

#### 4. TypeScript Compilation Errors
```bash
Property 'emailVerificationCode' does not exist
```
**Solution**: Run `npx prisma generate` and `npx prisma db push`

### Debug Commands

```powershell
# Check Redis status
redis-cli ping

# Check database connection
npx prisma db push --preview-feature

# View application logs
npm run start:dev

# Run specific tests
npm test -- --testNamePattern="AuthService"
```

## 📋 API Endpoints

### Authentication
- `POST /api/auth/exchange` - Exchange Firebase token
- `POST /api/auth/send-verification/:userId` - Send verification code
- `POST /api/auth/verify-code` - Verify email code
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout user

### User Management
- `GET /api/users/profile` - Get user profile (JWT required)
- `GET /api/users/me` - Get current user (JWT required)

### System
- `GET /health` - Basic health check
- `GET /api/health` - Detailed health check
- `GET /ping` - Ping test

## 🔒 Security Considerations

### Environment Variables
- Store sensitive data in .env file
- Never commit .env to version control
- Use strong JWT secrets in production
- Rotate keys regularly

### Database Security
- Use SSL connections for production
- Implement proper backup strategies
- Monitor database performance
- Use connection pooling

### API Security
- Implement rate limiting
- Validate all inputs
- Use HTTPS in production
- Monitor for suspicious activity

## 🚀 Deployment

### Production Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Redis service running
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup procedures in place

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "start:prod"]
```

## 📈 Performance Optimization

### Database
- Use connection pooling
- Optimize queries with indexes
- Monitor query performance
- Implement caching strategies

### Redis
- Monitor memory usage
- Configure persistence
- Use appropriate data structures
- Implement cleanup policies

### Application
- Use compression middleware
- Implement request caching
- Monitor response times
- Optimize bundle size

## 📞 Support

For issues or questions:
1. Check this guide first
2. Review application logs
3. Run health checks
4. Test with Postman collections
5. Check database connectivity

## 🎯 Success Criteria

### Functional Requirements
- [ ] Firebase authentication works
- [ ] Email verification sends codes
- [ ] JWT tokens are generated and validated
- [ ] User profiles are accessible
- [ ] Health endpoints respond correctly

### Performance Requirements
- [ ] Response time < 2 seconds
- [ ] Email sending < 5 seconds
- [ ] Database queries < 1 second
- [ ] System uptime > 99%

### Security Requirements
- [ ] All endpoints properly secured
- [ ] Rate limiting prevents abuse
- [ ] Input validation prevents injection
- [ ] Sensitive data is encrypted
- [ ] Audit logging is functional

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
