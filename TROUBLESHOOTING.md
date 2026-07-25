# Troubleshooting

Common issues and solutions when working with SuperDev AI Suite.

## Installation Issues

### `pip install` fails with build errors

**Problem:** Python package installation fails due to missing build dependencies.

**Solution:**
```bash
# Install build tools
pip install --upgrade pip setuptools wheel

# On Windows, you may need Microsoft C++ Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# On Ubuntu/Debian:
sudo apt-get install python3-dev build-essential libpq-dev
```

### `pnpm install` fails

**Problem:** Frontend dependencies fail to install.

**Solution:**
```bash
# Clear pnpm cache
pnpm store prune

# Delete node_modules and reinstall
rm -rf node_modules
pnpm install

# Ensure Node.js 20+ is active
node --version
```

## Database Issues

### Alembic migration fails

**Problem:** `alembic upgrade head` fails with connection or schema errors.

**Solution:**
```bash
# Check database is running
docker compose ps postgres

# Check connection string in .env
# Ensure DATABASE_URL is correct

# Reset and re-run migrations
alembic downgrade base
alembic upgrade head
```

### Connection refused to PostgreSQL

**Problem:** Application cannot connect to PostgreSQL.

**Solution:**
- Ensure PostgreSQL is running: `docker compose up -d postgres`
- Check the port mapping: `docker compose ps`
- Verify DATABASE_URL in `.env` matches docker compose configuration
- Wait a few seconds after starting for PostgreSQL to initialize

## Docker Issues

### Port already in use

**Problem:** Docker Compose fails because ports 3000, 8000, 5432, or 6379 are in use.

**Solution:**
```bash
# Find what's using the port
netstat -ano | findstr :8000   # Windows
lsof -i :8000                  # Linux/macOS

# Change port mapping in docker-compose.yml or stop the conflicting service
```

### Docker build fails

**Solution:**
```bash
# Rebuild without cache
docker compose build --no-cache

# Check Docker disk space
docker system df

# Prune unused resources
docker system prune -a
```

## Runtime Issues

### API returns 500 errors

**Solution:**
- Check API logs: `docker compose logs api`
- Verify all environment variables are set
- Ensure database migrations are up to date
- Check Redis connectivity

### WebSocket connections fail

**Solution:**
- Ensure the API is configured for WebSocket upgrades
- Check proxy/load balancer WebSocket support
- Verify `CORS_ORIGINS` includes the frontend URL
- Check browser console for detailed error messages

### Slow response times

**Solution:**
- Check if Redis caching is configured
- Verify database connection pool settings
- Monitor resource usage: `docker compose stats`
- Add indexes for frequently queried columns

## Frontend Issues

### Blank page on load

**Solution:**
- Check browser console for JavaScript errors
- Verify the API is reachable from the browser
- Clear browser cache and hard reload
- Check `NEXT_PUBLIC_API_URL` is set correctly in `.env`

### Styling broken

**Solution:**
- Rebuild the CSS: `cd frontend && pnpm build`
- Clear Tailwind CSS cache: `rm -rf frontend/.next`
- Ensure all dependencies are installed

## Getting Help

If the above solutions don't resolve your issue:

1. Search existing GitHub issues
2. Check the logs for error messages
3. Run with `LOG_LEVEL=DEBUG` for detailed output
4. Open a new GitHub issue with:
   - Steps to reproduce
   - Environment details (OS, Python version, Node version)
   - Relevant logs and error messages
   - What you've tried so far
