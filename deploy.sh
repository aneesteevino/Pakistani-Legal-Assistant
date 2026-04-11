#!/bin/bash

# 🚀 Pakistani Legal Assistant - Deployment Script

echo "⚖️  Pakistani Legal Assistant - Deployment Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    print_error "Vercel CLI is not installed. Installing..."
    npm install -g vercel
fi

# Check if user is logged in to Vercel
print_status "Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    print_warning "Not logged in to Vercel. Please login:"
    vercel login
fi

# Deploy Backend
print_status "Deploying backend to Vercel..."
cd backend

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    print_error "requirements.txt not found in backend directory"
    exit 1
fi

# Deploy backend
print_status "Starting backend deployment..."
vercel --prod

if [ $? -eq 0 ]; then
    print_success "Backend deployed successfully!"
    BACKEND_URL=$(vercel --prod 2>/dev/null | grep -o 'https://[^[:space:]]*')
    print_status "Backend URL: $BACKEND_URL"
else
    print_error "Backend deployment failed!"
    exit 1
fi

cd ..

# Update frontend environment
print_status "Updating frontend environment variables..."
if [ ! -z "$BACKEND_URL" ]; then
    echo "REACT_APP_API_URL=$BACKEND_URL" > frontend/.env.production
    print_success "Updated frontend/.env.production with backend URL"
fi

# Deploy Frontend
print_status "Deploying frontend to Vercel..."
cd frontend

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_error "package.json not found in frontend directory"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Build the project
print_status "Building frontend..."
npm run build

if [ $? -eq 0 ]; then
    print_success "Frontend build completed!"
else
    print_error "Frontend build failed!"
    exit 1
fi

# Deploy frontend
print_status "Starting frontend deployment..."
vercel --prod

if [ $? -eq 0 ]; then
    print_success "Frontend deployed successfully!"
    FRONTEND_URL=$(vercel --prod 2>/dev/null | grep -o 'https://[^[:space:]]*')
    print_status "Frontend URL: $FRONTEND_URL"
else
    print_error "Frontend deployment failed!"
    exit 1
fi

cd ..

# Summary
echo ""
echo "🎉 Deployment Complete!"
echo "======================"
print_success "Backend:  $BACKEND_URL"
print_success "Frontend: $FRONTEND_URL"
print_success "API Docs: $BACKEND_URL/docs"
echo ""
print_status "Next steps:"
echo "1. Test your application at the frontend URL"
echo "2. Verify API endpoints at the backend URL"
echo "3. Check API documentation at /docs endpoint"
echo "4. Set up custom domains if needed"
echo ""
print_warning "Don't forget to set environment variables in Vercel dashboard:"
echo "- GEMINI_API_KEY for the backend"
echo ""
print_success "Happy coding! ⚖️"