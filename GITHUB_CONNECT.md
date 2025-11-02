# How to Connect to GitHub and Upload Your Project

## Option 1: Install GitHub CLI (Easiest Method) ⭐

### Step 1: Install GitHub CLI

**Windows:**
1. Download from: https://cli.github.com/
2. Or use winget: `winget install --id GitHub.cli`
3. Or use Chocolatey: `choco install gh`

**After installation:**
```powershell
gh auth login
```
Follow the prompts to authenticate with your GitHub account.

### Step 2: Create Repository and Push

```powershell
# Create repository on GitHub and push
gh repo create ddos-detection-mitigation --public --source=. --remote=origin --push
```

## Option 2: Manual Method (No GitHub CLI)

### Step 1: Create GitHub Repository

1. Go to https://github.com
2. Sign in to your account
3. Click the **+** icon (top right) → **New repository**
4. Repository name: `ddos-detection-mitigation` (or any name you want)
5. Choose **Public** or **Private** (recommend **Private** for security)
6. **DO NOT** check "Add a README file" (you already have one)
7. Click **Create repository**

### Step 2: Get Your Personal Access Token

Since GitHub doesn't accept passwords anymore, you need a token:

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Token name: `My Computer` or `Local Dev`
4. Expiration: Choose how long (90 days, 1 year, or no expiration)
5. Select scopes: Check **`repo`** (this gives full access to repositories)
6. Click **Generate token** at the bottom
7. **COPY THE TOKEN IMMEDIATELY** - you won't see it again! 
   - It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Configure Git (if not done)

```powershell
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```
Use the same email you use for GitHub!

### Step 4: Add Files and Commit

```powershell
# Add all files
git add .

# Create commit
git commit -m "Initial commit: DDoS Detection and Mitigation System"
```

### Step 5: Connect to GitHub and Push

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name:

```powershell
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**When prompted:**
- **Username**: Your GitHub username
- **Password**: Paste your Personal Access Token (the `ghp_...` token from Step 2)

### Step 6: Save Credentials (Optional but Recommended)

To avoid entering credentials every time:

**Windows:**
```powershell
git config --global credential.helper wincred
```

Or use GitHub Desktop which handles this automatically.

## Option 3: Use GitHub Desktop (GUI Method)

1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in with your GitHub account
3. Click **File** → **Add Local Repository**
4. Click **Choose** and select your project folder
5. Click **Publish repository**
6. Enter repository name and choose public/private
7. Click **Publish Repository**

## Quick Command Summary (Manual Method)

```powershell
# 1. Configure Git (if needed)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 2. Add and commit files
git add .
git commit -m "Initial commit: DDoS Detection and Mitigation System"

# 3. Connect to GitHub (replace YOUR_USERNAME/YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Troubleshooting

**"remote origin already exists"**
```powershell
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

**"Authentication failed"**
- Make sure you're using a Personal Access Token, not your password
- Check that the token has `repo` scope selected

**"Permission denied"**
- Verify your GitHub username is correct
- Make sure the repository exists on GitHub
- Check that your token hasn't expired

## Security Note ⚠️

**Make your repository PRIVATE** when creating it. This project simulates DDoS attacks which could be misused if public.

