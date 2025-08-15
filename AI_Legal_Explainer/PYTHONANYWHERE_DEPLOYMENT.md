# 🚀 PythonAnywhere Deployment Guide (100% FREE - No Credit Card)

## ✨ **Why PythonAnywhere?**
- ✅ **100% FREE** - No credit card required
- ✅ **Native Django Support** - Built for Python web apps
- ✅ **MySQL Database Included** - Free database hosting
- ✅ **Custom Domains** - Your own subdomain
- ✅ **SSL/HTTPS** - Secure connections
- ✅ **GitHub Integration** - Easy deployment

## 📋 **Prerequisites**
1. **GitHub Account** (you already have this)
2. **PythonAnywhere Account** (free)
3. **Your Django Project** (already ready)

## 🎯 **Step 1: Create PythonAnywhere Account**

### **1.1 Sign Up (FREE)**
1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Click **"Create a Beginner account"**
3. Choose **FREE** plan
4. **No credit card required!**
5. Verify your email address

### **1.2 Get Your Account Details**
- **Username**: `yourusername` (replace with your actual username)
- **Website URL**: `https://yourusername.pythonanywhere.com`
- **Database Host**: `yourusername.mysql.pythonanywhere-services.com`

## 🔧 **Step 2: Configure Your Django Project**

### **2.1 Update Settings**
Replace `yourusername` in these files with your actual PythonAnywhere username:

**`wsgi_pythonanywhere.py`:**
```python
import os
import sys

# Add the project directory to the Python path
path = '/home/yourusername/AI_Legal_Explainer'  # ← Change this
os.environ.setdefault('PYTHONANYWHERE_SITE_NAME', 'yourusername.pythonanywhere.com')  # ← Change this
```

**`settings.py` (already updated):**
```python
'NAME': os.getenv('DB_NAME', 'yourusername$ai_legal_explainer'),  # ← Change this
'USER': os.getenv('DB_USER', 'yourusername'),  # ← Change this
'HOST': os.getenv('DB_HOST', 'yourusername.mysql.pythonanywhere-services.com'),  # ← Change this
```

### **2.2 Environment Variables**
Create `.env` file on PythonAnywhere:
```bash
SECRET_KEY=your_secret_key_here
DEBUG=False
DB_NAME=yourusername$ai_legal_explainer
DB_USER=yourusername
DB_PASSWORD=your_database_password
DB_HOST=yourusername.mysql.pythonanywhere-services.com
DB_PORT=3306
```

## 🚀 **Step 3: Deploy on PythonAnywhere**

### **3.1 Open PythonAnywhere Dashboard**
1. Login to [pythonanywhere.com](https://pythonanywhere.com)
2. Click **"Dashboard"**

### **3.2 Clone Your Repository**
1. Go to **"Consoles"** → **"Bash"**
2. Run these commands:
```bash
cd ~
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### **3.3 Create Virtual Environment**
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements_pythonanywhere.txt
```

### **3.4 Setup Database**
1. Go to **"Databases"** tab
2. Click **"Create database"**
3. **Database name**: `ai_legal_explainer`
4. **Username**: `yourusername`
5. **Password**: Create a strong password
6. **Host**: `yourusername.mysql.pythonanywhere-services.com`

### **3.5 Configure Web App**
1. Go to **"Web"** tab
2. Click **"Add a new web app"**
3. **Domain**: `yourusername.pythonanywhere.com`
4. **Python version**: `3.9`
5. **Source code**: `/home/yourusername/your-repo-name`
6. **Working directory**: `/home/yourusername/your-repo-name`
7. **WSGI configuration file**: Edit and replace with:
```python
import os
import sys

# Add the project directory to the Python path
path = '/home/yourusername/your-repo-name'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables for PythonAnywhere
os.environ.setdefault('PYTHONANYWHERE_SITE_NAME', 'yourusername.pythonanywhere.com')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI_Legal_Explainer.settings')

# Import Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### **3.6 Setup Static Files**
1. Go to **"Files"** tab
2. Navigate to `/home/yourusername/your-repo-name`
3. Create `static` folder
4. Run in console:
```bash
cd ~/your-repo-name
python manage.py collectstatic --noinput
```

### **3.7 Run Migrations**
```bash
cd ~/your-repo-name
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
```

### **3.8 Reload Web App**
1. Go to **"Web"** tab
2. Click **"Reload"** button

## 🌐 **Step 4: Update Vercel Frontend**

### **4.1 Update Environment Variables**
In your Vercel project, set:
```
DJANGO_API_URL=https://yourusername.pythonanywhere.com
```

### **4.2 Update CORS Settings**
Your Django settings already include PythonAnywhere domains.

## ✅ **Step 5: Test Your Deployment**

### **5.1 Test Backend**
- **Health Check**: `https://yourusername.pythonanywhere.com/api/health/`
- **Admin Panel**: `https://yourusername.pythonanywhere.com/admin/`

### **5.2 Test Frontend**
- **Vercel App**: `https://your-vercel-domain.vercel.app`
- **File Upload**: Test document processing

## 🔧 **Troubleshooting**

### **Common Issues:**

**1. Import Errors**
- Check Python path in WSGI file
- Verify virtual environment activation

**2. Database Connection**
- Verify database credentials
- Check database host and port

**3. Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check static files directory

**4. 500 Server Error**
- Check error logs in **"Web"** → **"Log files"**
- Verify environment variables

## 📱 **Mobile & API Testing**

### **Test API Endpoints:**
```bash
# Health check
curl https://yourusername.pythonanywhere.com/api/health/

# Test upload
curl -X POST https://yourusername.pythonanywhere.com/api/upload/ \
  -F "file=@test_document.pdf"
```

## 🎉 **Success!**

Your Django backend is now hosted on PythonAnywhere:
- **Backend URL**: `https://yourusername.pythonanywhere.com`
- **Database**: MySQL (included free)
- **SSL/HTTPS**: Automatic
- **Cost**: $0 (completely free!)

## 🔄 **Next Steps**

1. **Test your API endpoints**
2. **Update Vercel environment variables**
3. **Test file uploads from frontend**
4. **Monitor PythonAnywhere usage** (free tier limits)

## 📞 **Need Help?**

- **PythonAnywhere Help**: [help.pythonanywhere.com](https://help.pythonanywhere.com)
- **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com)
- **Community Forums**: [pythonanywhere.com/community](https://pythonanywhere.com/community)

---

**🎯 You now have a completely free Django backend hosted on PythonAnywhere with no credit card required!**


