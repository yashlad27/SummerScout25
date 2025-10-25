#!/bin/bash
# Pre-Push Security Check - Run before pushing to GitHub

echo "🔍 PRE-PUSH SECURITY CHECK"
echo "======================================================================"
echo ""

ISSUES_FOUND=0

# 1. Check if .env is properly gitignored
echo "1️⃣ Checking .env file..."
if git check-ignore .env > /dev/null 2>&1; then
    echo "   ✅ .env is properly ignored"
else
    echo "   ❌ WARNING: .env is NOT ignored!"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# 2. Search for potential API keys or passwords
echo ""
echo "2️⃣ Searching for potential secrets in tracked files..."
SECRETS_PATTERN="(password|api_key|secret|smtp_pass).*=.*['\"][^']+"
if git grep -iE "$SECRETS_PATTERN" -- ':!.env*' ':!*.md' ':!tests/*' > /dev/null 2>&1; then
    echo "   ⚠️  Found potential secrets in tracked files:"
    git grep -iE "$SECRETS_PATTERN" -- ':!.env*' ':!*.md' ':!tests/*' | head -5
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo "   ✅ No secrets found in tracked files"
fi

# 3. Check if .env.example has no real secrets
echo ""
echo "3️⃣ Checking .env.example..."
if [ -f .env.example ]; then
    if grep -qE "(changeme|your-|example|REPLACE)" .env.example; then
        echo "   ✅ .env.example uses placeholder values"
    else
        echo "   ⚠️  .env.example might contain real values"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo "   ⚠️  .env.example not found"
fi

# 4. Check for large files
echo ""
echo "4️⃣ Checking for large files (>5MB)..."
LARGE_FILES=$(find . -type f -size +5M -not -path "./.git/*" -not -path "./docs/archive/*" 2>/dev/null)
if [ -z "$LARGE_FILES" ]; then
    echo "   ✅ No large files found"
else
    echo "   ⚠️  Large files found:"
    echo "$LARGE_FILES"
fi

# 5. Check Docker/Python cache
echo ""
echo "5️⃣ Checking for cache directories..."
if [ -d "__pycache__" ] || [ -d ".pytest_cache" ] || [ -d "node_modules" ]; then
    echo "   ⚠️  Cache directories found (should be gitignored)"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo "   ✅ No cache directories in root"
fi

# 6. Verify essential files exist
echo ""
echo "6️⃣ Verifying essential files..."
ESSENTIAL_FILES=("README.md" "docker-compose.yml" ".gitignore" "scrape.sh" "show_jobs.sh")
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file exists"
    else
        echo "   ❌ $file is missing!"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
done

# 7. Check git status
echo ""
echo "7️⃣ Checking git status..."
if git status --porcelain | grep -q '^??'; then
    echo "   ⚠️  Untracked files exist:"
    git status --porcelain | grep '^??'
    echo "   (This is OK if they're intentional)"
fi

echo ""
echo "======================================================================"

# Summary
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED! Safe to push to GitHub."
    echo ""
    echo "Ready to publish as public repo!"
    echo ""
    echo "Next steps:"
    echo "  git add ."
    echo "  git commit -m 'Initial commit: InternTracker v1.0'"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/InternTracker.git"
    echo "  git push -u origin main"
    exit 0
else
    echo "❌ FOUND $ISSUES_FOUND ISSUE(S)! Please fix before pushing."
    echo ""
    echo "Review the issues above and fix them."
    exit 1
fi
