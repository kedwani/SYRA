# SYRA Production Deployment Guide - Tailwind CSS Setup

## Overview
This document explains how to deploy the SYRA Medical ID website with compiled Tailwind CSS on PythonAnywhere.

## ⚠️ Important: PythonAnywhere & Node.js

**PythonAnywhere does NOT have Node.js installed by default.** This means you cannot compile Tailwind CSS directly on PythonAnywhere.

### Solution Options:

#### Option A: Build CSS Locally (Recommended)
Build the CSS on your local machine and commit the compiled `output.css` to the repository.

**Steps:**
1. On your local machine with Node.js installed:
   ```bash
   cd /path/to/SYRA
   npm install
   npm run build:css
   ```

2. Commit the changes:
   ```bash
   git add static/css/output.css
   git commit -m "Add compiled Tailwind CSS"
   git push
   ```

3. On PythonAnywhere, pull the changes:
   ```bash
   cd ~/syra
   git pull
   ```

#### Option B: Install Node.js on PythonAnywhere (Bash Console)
PythonAnywhere allows installing packages via pip, but Node.js requires system-level installation which may not be possible on the free tier.

**Try this in PythonAnywhere Bash console:**
```bash
# Check if you can install Node.js
which node
# If not available, you cannot install it on PythonAnywhere
```

If Node.js is unavailable, **use Option A**.

---

## Step-by-Step Production Setup

### Step 1: Local Machine Preparation

1. **Install Node.js** (if not already installed):
   - Windows: Download from https://nodejs.org or use winget: `winget install OpenJS.NodeJS.LTS`
   - Mac: `brew install node`
   - Linux: `sudo apt install nodejs npm`

2. **Clone repository and install dependencies:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/SYRA.git
   cd SYRA
   pip install -r requirements.txt
   npm install
   ```

3. **Build CSS:**
   ```bash
   npm run build:css
   ```

4. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add compiled Tailwind CSS for production"
   git push origin main
   ```

### Step 2: PythonAnywhere Setup

1. **Open PythonAnywhere Dashboard**
   - Go to https://www.pythonanywhere.com/
   - Log in to your account

2. **Open Bash Console**
   - Click on "Files" → Navigate to your project directory
   - Or click on "Consoles" → "Bash"

3. **Pull Latest Code:**
   ```bash
   cd ~/syra  # or your project directory
   git pull
   ```

4. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Collect Static Files:**
   ```bash
   python manage.py collectstatic
   ```
   - Type `yes` when prompted

6. **Reload the Web App:**
   - Go to "Web" tab
   - Click "Reload" button next to your domain

### Step 3: Verify Deployment

1. Visit your website: `https://yourusername.pythonanywhere.com`
2. Open browser Developer Tools (F12)
3. Check Network tab for CSS loading
4. Verify `output.css` is being served (should be ~71KB)

---

## Maintaining Tailwind CSS in Production

### When You Modify Templates:
If you add new Tailwind classes to templates, you need to rebuild:

1. **Locally:**
   ```bash
   npm run build:css
   git add static/css/output.css
   git commit -m "Update compiled CSS"
   git push
   ```

2. **On PythonAnywhere:**
   ```bash
   git pull
   python manage.py collectstatic
   reload
   ```

### Watching for Changes (Development):
```bash
npm run watch:css
```
This watches for changes and rebuilds automatically.

---

## Troubleshooting

### Issue: CSS Not Loading
**Solution:**
1. Check that `output.css` exists: `ls -la static/css/output.css`
2. Verify STATIC_ROOT settings in settings.py
3. Run collectstatic: `python manage.py collectstatic`

### Issue: Styles Look Broken
**Solution:**
1. Make sure compiled CSS is being loaded (check base.html)
2. Verify dark mode classes are working
3. Check browser console for errors

### Issue: Need to Add New Tailwind Classes
**Solution:**
1. Add classes to templates
2. Rebuild locally: `npm run build:css`
3. Commit and push: `git add -A && git commit -m "Update CSS"`
4. Pull on server: `git pull && python manage.py collectstatic`

---

## Files Modified for Tailwind

| File | Purpose |
|------|---------|
| `tailwind.config.js` | Tailwind configuration with medical theme |
| `package.json` | NPM scripts for building CSS |
| `static/css/input.css` | Source CSS with Tailwind directives |
| `static/css/output.css` | Compiled production CSS (71KB) |
| `templates/base.html` | Updated to use compiled CSS |
| `requirements.txt` | Added django-tailwind package |
| `syra/settings.py` | Added Tailwind app and config |

---

## Performance Improvement

| Metric | Before (CDN) | After (Compiled) |
|--------|-------------|------------------|
| CSS Size | ~3MB | 71KB |
| Load Time | Slower | Faster |
| Runtime Compilation | Yes | No |
| Caching | Poor | Excellent |

---

## Questions?

If you have issues, check:
1. PythonAnywhere logs (Web tab)
2. Browser developer console
3. Git repository status
