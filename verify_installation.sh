#!/bin/bash

# Telegram Bot Installation Verification Script
# This script checks if all required files and configurations are in place

echo "🔍 Verifying Telegram Bot Installation..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check file existence
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 missing"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check directory existence
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 directory exists"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 directory missing"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo "📁 Checking Core Files..."
check_file "telegram_main.py"
check_file "config.toml"
check_file "pyproject.toml"
echo ""

echo "📁 Checking Source Files..."
check_file "src/telegram_bot.py"
check_file "src/telegram_handlers.py"
check_file "src/telegram_integration.py"
check_file "src/config.py"
check_file "src/rip.py"
echo ""

echo "📁 Checking Documentation..."
check_file "QUICK_START.md"
check_file "TELEGRAM_BOT_SETUP.md"
check_file "TELEGRAM_BOT_SETUP_MM.md"
check_file "CHANGES_SUMMARY.md"
check_file "BOT_WORKFLOW.md"
check_file "README_MM.md"
echo ""

echo "🔧 Checking Configuration..."
if [ -f "config.toml" ]; then
    if grep -q "botToken.*YOUR_BOT_TOKEN_HERE" config.toml; then
        echo -e "${YELLOW}⚠${NC} Bot token not configured (still using placeholder)"
        echo "   Please edit config.toml and add your bot token"
    else
        echo -e "${GREEN}✓${NC} Bot token appears to be configured"
        ((CHECKS_PASSED++))
    fi
    
    if grep -q "enable = true" config.toml; then
        echo -e "${GREEN}✓${NC} Telegram bot is enabled"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Telegram bot is disabled"
        echo "   Set 'enable = true' in [telegram] section"
    fi
else
    echo -e "${RED}✗${NC} config.toml not found"
    echo "   Run: cp config.example.toml config.toml"
    ((CHECKS_FAILED++))
fi
echo ""

echo "🐍 Checking Python Version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (>= 3.11 required)"
        ((CHECKS_PASSED++))
    else
        echo -e "${RED}✗${NC} Python $PYTHON_VERSION (3.11+ required)"
        echo "   Please install Python 3.11 or higher"
        ((CHECKS_FAILED++))
    fi
else
    echo -e "${RED}✗${NC} Python 3 not found"
    ((CHECKS_FAILED++))
fi
echo ""

echo "📦 Checking Poetry..."
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version | cut -d' ' -f3)
    echo -e "${GREEN}✓${NC} Poetry $POETRY_VERSION installed"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Poetry not found"
    echo "   Install: curl -sSL https://install.python-poetry.org | python3 -"
fi
echo ""

echo "📊 Checking Python Syntax..."
SYNTAX_ERRORS=0
for file in telegram_main.py src/telegram_bot.py src/telegram_handlers.py src/telegram_integration.py; do
    if [ -f "$file" ]; then
        if python3 -m py_compile "$file" 2>/dev/null; then
            echo -e "${GREEN}✓${NC} $file syntax OK"
            ((CHECKS_PASSED++))
        else
            echo -e "${RED}✗${NC} $file has syntax errors"
            ((CHECKS_FAILED++))
            ((SYNTAX_ERRORS++))
        fi
    fi
done
echo ""

echo "═══════════════════════════════════════════════════════"
echo "📋 Verification Summary"
echo "═══════════════════════════════════════════════════════"
echo -e "Checks Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Checks Failed: ${RED}$CHECKS_FAILED${NC}"
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "🚀 Next Steps:"
    echo "1. Edit config.toml and add your Telegram bot token"
    echo "2. Set 'enable = true' in [telegram] section"
    echo "3. Run: poetry install"
    echo "4. Run: poetry run python telegram_main.py"
    echo ""
    echo "📚 Documentation:"
    echo "   Quick Start: cat QUICK_START.md"
    echo "   Full Guide:  cat TELEGRAM_BOT_SETUP.md"
    echo "   မြန်မာ:      cat TELEGRAM_BOT_SETUP_MM.md"
    exit 0
else
    echo -e "${RED}❌ Some checks failed!${NC}"
    echo ""
    echo "Please fix the issues above before running the bot."
    echo ""
    echo "📚 Need Help?"
    echo "   Read: TELEGRAM_BOT_SETUP.md"
    echo "   Or:   TELEGRAM_BOT_SETUP_MM.md (မြန်မာ)"
    exit 1
fi
