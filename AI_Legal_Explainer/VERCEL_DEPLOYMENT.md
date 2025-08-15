# Vercel Deployment Guide for AI Legal Document Explainer

## Overview
This guide explains how to deploy your AI Legal Document Explainer project on Vercel. The project is structured with:
- **Frontend**: Static HTML/CSS/JS files hosted on Vercel
- **Backend**: Django API hosted separately (e.g., on Railway, Heroku, or DigitalOcean)
- **API Proxy**: Vercel serverless functions that forward requests to the Django backend

## Prerequisites
1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be on GitHub
3. **Django Backend**: Hosted and accessible via HTTPS
4. **Vercel CLI** (optional): `npm i -g vercel`

## Step 1: Deploy Django Backend

### Option A: Railway (Recommended for Django)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Create a new project
4. Add environment variables:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-app.railway.app
   DATABASE_URL=your-database-url
   ```
5. Deploy and get your app URL (e.g., `https://your-app.railway.app`)

### Option B: Heroku
1. Create a Heroku account
2. Install Heroku CLI
3. Create a new app
4. Add PostgreSQL addon
5. Deploy using Git

### Option C: DigitalOcean App Platform
1. Create a DigitalOcean account
2. Create a new app
3. Connect your repository
4. Configure environment variables
5. Deploy

## Step 2: Update Environment Variables

Update the `vercel.json` file with your Django backend URL:

```json
{
  "env": {
    "DJANGO_API_URL": "https://your-django-backend.railway.app"
  }
}
```

## Step 3: Deploy to Vercel

### Method 1: Vercel Dashboard (Recommended)
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository
4. Configure project settings:
   - **Framework Preset**: Other
   - **Root Directory**: `AI_Legal_Explainer`
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
5. Click "Deploy"

### Method 2: Vercel CLI
```bash
# Navigate to your project directory
cd AI_Legal_Explainer

# Deploy to Vercel
vercel

# Follow the prompts to configure your project
```

## Step 4: Configure Custom Domain (Optional)

1. In your Vercel dashboard, go to your project
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Step 5: Test Your Deployment

1. Visit your Vercel app URL
2. Test file upload functionality
3. Verify API calls are working
4. Check console for any errors

## Project Structure for Vercel

```
AI_Legal_Explainer/
├── vercel.json              # Vercel configuration
├── frontend/                # Static frontend files
│   ├── index.html          # Main HTML file
│   ├── styles.css          # CSS styles
│   └── script.js           # JavaScript functionality
├── api/                    # Vercel serverless functions
│   ├── index.py            # API proxy to Django
│   └── requirements.txt    # Python dependencies
└── AI_Legal_Explainer/     # Django backend (not deployed to Vercel)
```

## Environment Variables

### Vercel Environment Variables
- `DJANGO_API_URL`: URL of your Django backend

### Django Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Your domain names
- `DATABASE_URL`: Database connection string
- `CORS_ALLOWED_ORIGINS`: Include your Vercel domain

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure Django CORS settings include Vercel domains
   - Check that `CORS_ALLOW_ALL_ORIGINS` is False in production

2. **API Connection Failed**
   - Verify `DJANGO_API_URL` is correct
   - Check Django backend is accessible
   - Ensure HTTPS is working

3. **File Upload Issues**
   - Check Django file upload settings
   - Verify media storage configuration
   - Check file size limits

4. **Build Errors**
   - Ensure all required files are in the correct directories
   - Check `vercel.json` configuration
   - Verify Python version compatibility

### Debug Steps

1. **Check Vercel Logs**
   - Go to your project dashboard
   - Click "Functions" to see serverless function logs

2. **Test API Endpoints**
   - Use tools like Postman or curl
   - Test both Vercel proxy and direct Django endpoints

3. **Browser Console**
   - Check for JavaScript errors
   - Monitor network requests
   - Verify API responses

## Performance Optimization

1. **Enable Caching**
   - Add cache headers in Django
   - Use Vercel's edge caching

2. **Optimize Images**
   - Use WebP format
   - Implement lazy loading

3. **Minimize Bundle Size**
   - Compress CSS/JS files
   - Use CDN for external libraries

## Security Considerations

1. **Environment Variables**
   - Never commit secrets to Git
   - Use Vercel's environment variable system

2. **CORS Configuration**
   - Restrict allowed origins in production
   - Implement proper authentication

3. **API Security**
   - Use HTTPS for all API calls
   - Implement rate limiting
   - Add authentication middleware

## Monitoring and Analytics

1. **Vercel Analytics**
   - Enable Vercel Analytics in dashboard
   - Monitor performance metrics

2. **Error Tracking**
   - Integrate Sentry for error monitoring
   - Set up logging in Django

3. **Performance Monitoring**
   - Use Vercel's built-in monitoring
   - Track API response times

## Support and Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Django Deployment**: [docs.djangoproject.com/en/stable/howto/deployment/](https://docs.djangoproject.com/en/stable/howto/deployment/)
- **GitHub Repository**: [github.com/shajishali/AI-lecal-doc-explainer](https://github.com/shajishali/AI-lecal-doc-explainer)

## Next Steps

After successful deployment:
1. Set up monitoring and analytics
2. Configure custom domain
3. Implement CI/CD pipeline
4. Add performance optimizations
5. Set up backup and recovery procedures


