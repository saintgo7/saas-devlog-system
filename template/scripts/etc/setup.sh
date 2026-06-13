#!/bin/bash
# Workstation Manager - Initial Setup Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo "================================================"
echo "  Workstation Manager - Setup Script"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are installed"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Check environment
echo ""
print_info "Select environment:"
echo "  1) Development (default)"
echo "  2) Production"
read -p "Enter choice [1-2]: " env_choice

case $env_choice in
    2)
        ENVIRONMENT="production"
        COMPOSE_FILE="docker-compose.prod.yml"
        ;;
    *)
        ENVIRONMENT="development"
        COMPOSE_FILE="docker-compose.dev.yml"
        ;;
esac

print_info "Environment: $ENVIRONMENT"

# Create .env files if they don't exist
echo ""
print_info "Setting up environment files..."

if [ ! -f .env ]; then
    print_warning ".env file not found, creating from template..."
    cp .env.example .env

    # Generate random secrets
    SECRET_KEY=$(openssl rand -base64 32)
    AGENT_API_KEY=$(openssl rand -hex 32)
    ENCRYPTION_KEY=$(openssl rand -base64 32 | head -c 32)
    JWT_SECRET=$(openssl rand -base64 32)

    # Update .env with generated secrets
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
        sed -i '' "s/your-agent-api-key-change-this-in-production/$AGENT_API_KEY/" .env
        sed -i '' "s/your-encryption-key-32-chars-exactly/$ENCRYPTION_KEY/" .env
        sed -i '' "s/your-jwt-secret-key-change-this/$JWT_SECRET/" .env
    else
        # Linux
        sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
        sed -i "s/your-agent-api-key-change-this-in-production/$AGENT_API_KEY/" .env
        sed -i "s/your-encryption-key-32-chars-exactly/$ENCRYPTION_KEY/" .env
        sed -i "s/your-jwt-secret-key-change-this/$JWT_SECRET/" .env
    fi

    print_success "Created .env file with generated secrets"
else
    print_success ".env file already exists"
fi

if [ ! -f server/.env.$ENVIRONMENT ]; then
    print_warning "server/.env.$ENVIRONMENT not found, creating from template..."
    cp server/.env.example server/.env.$ENVIRONMENT
    print_success "Created server/.env.$ENVIRONMENT"
else
    print_success "server/.env.$ENVIRONMENT already exists"
fi

if [ ! -f frontend/.env.local ]; then
    print_warning "frontend/.env.local not found, creating from template..."
    cp frontend/.env.local.example frontend/.env.local
    print_success "Created frontend/.env.local"
else
    print_success "frontend/.env.local already exists"
fi

# Generate SSL certificates for development
if [ "$ENVIRONMENT" == "development" ]; then
    echo ""
    print_info "Generating self-signed SSL certificates for development..."

    if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=KR/ST=Seoul/L=Seoul/O=Development/CN=localhost" \
            2>/dev/null

        chmod 600 nginx/ssl/key.pem
        print_success "SSL certificates generated"
    else
        print_success "SSL certificates already exist"
    fi
fi

# Create necessary directories
echo ""
print_info "Creating directories..."
mkdir -p backups
mkdir -p logs
print_success "Directories created"

# Build Docker images
echo ""
print_info "Building Docker images..."
if [ "$ENVIRONMENT" == "development" ]; then
    docker-compose -f $COMPOSE_FILE build
else
    docker-compose -f $COMPOSE_FILE build
fi
print_success "Docker images built"

# Start services
echo ""
read -p "Do you want to start the services now? [Y/n]: " start_services

if [ "$start_services" != "n" ] && [ "$start_services" != "N" ]; then
    print_info "Starting services..."
    docker-compose -f $COMPOSE_FILE up -d

    # Wait for services to be healthy
    print_info "Waiting for services to be ready..."
    sleep 10

    # Check service status
    docker-compose -f $COMPOSE_FILE ps

    echo ""
    print_success "Setup complete!"
    echo ""
    echo "================================================"
    echo "  Access Information"
    echo "================================================"

    if [ "$ENVIRONMENT" == "development" ]; then
        echo "Frontend Dashboard: http://localhost:3000"
        echo "Backend API:        http://localhost:8000"
        echo "API Documentation:  http://localhost:8000/docs"
        echo "pgAdmin:            http://localhost:5050"
        echo "  - Email: admin@workstation.com"
        echo "  - Password: admin"
        echo "Redis Commander:    http://localhost:8081"
        echo ""
        echo "Default Credentials:"
        echo "  - Username: admin"
        echo "  - Password: admin123"
        echo ""
        print_warning "IMPORTANT: Change the default password after first login!"
    else
        echo "Frontend Dashboard: https://your-domain.com"
        echo "Backend API:        https://your-domain.com/api"
        echo "API Documentation:  https://your-domain.com/docs"
        echo ""
        print_warning "IMPORTANT: Configure your domain and SSL certificates!"
        print_warning "IMPORTANT: Change all default passwords!"
    fi

    echo "================================================"
else
    echo ""
    print_success "Setup complete!"
    echo ""
    print_info "To start services, run:"
    echo "  docker-compose -f $COMPOSE_FILE up -d"
fi

echo ""
print_info "Useful commands:"
echo "  View logs:      docker-compose -f $COMPOSE_FILE logs -f"
echo "  Stop services:  docker-compose -f $COMPOSE_FILE down"
echo "  Restart:        docker-compose -f $COMPOSE_FILE restart"
echo "  Backup DB:      ./scripts/backup.sh"
echo ""
