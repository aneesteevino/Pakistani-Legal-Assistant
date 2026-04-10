# Deploy Backend to Vercel

## Steps to deploy your backend:

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Vercel CLI (if not already installed):**
   ```bash
   npm install -g vercel
   ```

3. **Deploy to Vercel:**
   ```bash
   vercel
   ```

4. **Set environment variables in Vercel dashboard:**
   - Go to your Vercel project settings
   - Add these environment variables:
     - `OPENAI_API_KEY`: Your OpenAI API key
     - `SUPABASE_URL`: Your Supabase URL  
     - `SUPABASE_KEY`: Your Supabase key

5. **Update frontend environment:**
   - After backend deployment, copy the backend URL
   - Update `frontend/.env.production` with your backend URL:
     ```
     REACT_APP_API_URL=https://your-backend-url.vercel.app
     ```

6. **Redeploy frontend:**
   ```bash
   cd ../frontend
   vercel --prod
   ```

## Alternative: Quick Fix for Testing

If you want to test locally first:

1. **Start backend locally:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **In another terminal, start frontend:**
   ```bash
   cd frontend  
   npm start
   ```

Your app should now work locally at http://localhost:3000