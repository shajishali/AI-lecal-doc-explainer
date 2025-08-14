# Render Deployment Guide for Django Backend

## 🆓 Free Hosting on Render

**Render** offers the best free tier for Django applications:
- **Free Tier**: 750 hours/month (31 days)
- **Auto-sleep**: After 15 minutes of inactivity
- **PostgreSQL Database**: Included in free tier
- **Custom Domains**: Supported
- **SSL/HTTPS**: Automatic

## 🚀 Quick Deployment Steps

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)
4. Verify your email address

### Step 2: Deploy from GitHub
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository: `shajishali/AI-lecal-doc-explainer`
4. Configure the service:
   - **Name**: `ai-legal-explainer-backend`
   - **Root Directory**: `AI_Legal_Explainer`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn AI_Legal_Explainer.wsgi:application`

### Step 3: Add Environment Variables
Click "Environment" tab and add:
```
PYTHON_VERSION=3.9.16
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.onrender.com
RENDER=true
```

### Step 4: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `ai-legal-explainer-db`
3. Database: `ai_legal_explainer`
4. User: `ai_legal_explainer_user`
5. Plan: Free

### Step 5: Link Database to Web Service
1. Go back to your web service
2. In "Environment" tab, add:
```
DATABASE_URL=postgresql://user:password@host:port/database
```
(Get this from your PostgreSQL service)

## 📁 Files Created for Render

### 1. `build.sh` - Build Script
```bash
#!/usr/bin/env bash
set -o errexit
pip install -r requirements_render.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

### 2. `render.yaml` - Infrastructure as Code
```yaml
services:
  - type: web
    name: ai-legal-explainer-backend
    env: python
    plan: free
    buildCommand: "./build.sh"
    startCommand: "gunicorn AI_Legal_Explainer.wsgi:application"

databases:
  - name: ai-legal-explainer-db
    plan: free
```

### 3. `requirements_render.txt` - Production Dependencies
- Django 5.2.5
- PostgreSQL adapter (psycopg2-binary)
- Gunicorn web server
- WhiteNoise for static files
- Production-ready packages

## 🔧 Manual Deployment (Alternative)

If you prefer manual setup:

### 1. Create Web Service
- **Name**: `ai-legal-explainer-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `master`
- **Root Directory**: `AI_Legal_Explainer`

### 2. Build & Deploy Settings
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn AI_Legal_Explainer.wsgi:application`
- **Auto-Deploy**: Enable

### 3. Environment Variables
```
PYTHON_VERSION=3.9.16
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=.onrender.com
RENDER=true
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 🌐 Database Configuration

### PostgreSQL Connection
Your Django app automatically detects Render environment and uses:
- **Engine**: `django.db.backends.postgresql`
- **Host**: Render-provided PostgreSQL host
- **Port**: 5432 (default)
- **Database**: `ai_legal_explainer`
- **User**: `ai_legal_explainer_user`

### Database Migration
The build script automatically runs:
```bash
python manage.py migrate
```

## 📊 Monitoring & Logs

### View Logs
1. Go to your web service in Render dashboard
2. Click "Logs" tab
3. Monitor real-time application logs

### Health Check
Your app will be available at:
`https://ai-legal-explainer-backend.onrender.com`

## 🔒 Security Features

### Environment Variables
- Never commit secrets to Git
- Use Render's environment variable system
- Automatic HTTPS/SSL

### CORS Configuration
Updated Django settings to allow:
- Vercel frontend domains
- Render backend domains
- Local development

## 🚨 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements_render.txt` for compatibility
   - Verify Python version (3.9.16)
   - Check build script permissions

2. **Database Connection Error**
   - Verify `DATABASE_URL` environment variable
   - Check PostgreSQL service status
   - Ensure database exists

3. **Static Files Not Loading**
   - Check `STATIC_ROOT` configuration
   - Verify WhiteNoise is installed
   - Check build script execution

4. **App Not Starting**
   - Check start command syntax
   - Verify Gunicorn installation
   - Check application logs

### Debug Steps

1. **Check Build Logs**
   - Go to "Logs" → "Build Logs"
   - Look for error messages
   - Verify dependency installation

2. **Check Runtime Logs**
   - Go to "Logs" → "Runtime Logs"
   - Look for Django error messages
   - Check database connection

3. **Test Locally**
   - Test with `requirements_render.txt`
   - Verify PostgreSQL connection
   - Test Gunicorn startup

## 📈 Performance Optimization

### Free Tier Limitations
- **Memory**: 512MB RAM
- **CPU**: Shared resources
- **Sleep**: After 15 min inactivity
- **Cold Start**: ~30 seconds after sleep

### Optimization Tips
1. **Database Queries**: Use select_related/prefetch_related
2. **Static Files**: Enable WhiteNoise compression
3. **Caching**: Implement Redis if needed
4. **Async**: Use async views where possible

## 🔄 Updating Your App

### Automatic Deployment
- Push to `master` branch
- Render automatically rebuilds and deploys
- Zero downtime updates

### Manual Deployment
1. Go to your service in Render dashboard
2. Click "Manual Deploy"
3. Select branch/commit
4. Click "Deploy latest commit"

## 🌍 Custom Domain (Optional)

### Add Custom Domain
1. Go to "Settings" → "Custom Domains"
2. Add your domain (e.g., `api.yourdomain.com`)
3. Update DNS records as instructed
4. Update `ALLOWED_HOSTS` in environment variables

## 📞 Support

### Render Support
- **Documentation**: [render.com/docs](https://render.com/docs)
- **Community**: [render.com/community](https://render.com/community)
- **Status**: [status.render.com](https://status.render.com)

### Next Steps
After successful deployment:
1. Test your API endpoints
2. Update Vercel environment variables
3. Test frontend-backend integration
4. Monitor performance and logs
5. Set up custom domain (optional)

## 🎯 Success Checklist

- [ ] Render account created
- [ ] Web service deployed
- [ ] PostgreSQL database created
- [ ] Environment variables set
- [ ] Build successful
- [ ] App accessible via URL
- [ ] Database migrations completed
- [ ] API endpoints responding
- [ ] Vercel frontend connected
- [ ] CORS working properly

Your Django backend will be running at:
`https://ai-legal-explainer-backend.onrender.com`
