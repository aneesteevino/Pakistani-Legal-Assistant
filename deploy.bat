@echo off
echo ⚖️  Pakistani Legal Assistant - Deployment Script
echo ==================================================

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Vercel CLI is not installed. Installing...
    npm install -g vercel
)

REM Check if user is logged in to Vercel
echo [INFO] Checking Vercel authentication...
vercel whoami >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Not logged in to Vercel. Please login:
    vercel login
)

REM Deploy Backend
echo [INFO] Deploying backend to Vercel...
cd backend

if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in backend directory
    exit /b 1
)

echo [INFO] Starting backend deployment...
vercel --prod

if %errorlevel% equ 0 (
    echo [SUCCESS] Backend deployed successfully!
) else (
    echo [ERROR] Backend deployment failed!
    exit /b 1
)

cd ..

REM Deploy Frontend
echo [INFO] Deploying frontend to Vercel...
cd frontend

if not exist "package.json" (
    echo [ERROR] package.json not found in frontend directory
    exit /b 1
)

if not exist "node_modules" (
    echo [INFO] Installing frontend dependencies...
    npm install
)

echo [INFO] Building frontend...
npm run build

if %errorlevel% equ 0 (
    echo [SUCCESS] Frontend build completed!
) else (
    echo [ERROR] Frontend build failed!
    exit /b 1
)

echo [INFO] Starting frontend deployment...
vercel --prod

if %errorlevel% equ 0 (
    echo [SUCCESS] Frontend deployed successfully!
) else (
    echo [ERROR] Frontend deployment failed!
    exit /b 1
)

cd ..

echo.
echo 🎉 Deployment Complete!
echo ======================
echo [SUCCESS] Check your Vercel dashboard for deployment URLs
echo [INFO] Next steps:
echo 1. Test your application at the frontend URL
echo 2. Verify API endpoints at the backend URL
echo 3. Check API documentation at /docs endpoint
echo 4. Set up custom domains if needed
echo.
echo [WARNING] Don't forget to set environment variables in Vercel dashboard:
echo - GEMINI_API_KEY for the backend
echo.
echo [SUCCESS] Happy coding! ⚖️

pause