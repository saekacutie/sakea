#!/bin/bash
# ============================================
# SAEKAX TOOL - ONE-COMMAND SETUP
# Created by Saeka Tojirp
# Repo: github.com/saekacutie/sakea
# ============================================

clear

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
RESET='\033[0m'

# Centered bold title
center_text() {
    local text="$1"
    local width=$(tput cols)
    local pad=$(( (width - ${#text}) / 2 ))
    printf "%*s%s\n" $pad "" "$text"
}

clear
echo ""
echo ""
center_text "$(echo -e "${CYAN}${BOLD}SAEKA TOOL${RESET}")"
echo ""

# Function for animated loading
loading_spinner() {
    local pid=$1
    local package=$2
    local frames='◜◠◝◞◡◟'
    local i=0
    while kill -0 $pid 2>/dev/null; do
        local frame="${frames:$i:1}"
        local width=$(tput cols)
        local text="Installing ${package}..."
        local total=$(( ${#text} + 2 ))
        local pad=$(( (width - total) / 2 ))
        printf "\r%*s%s %s" $pad "" "$frame" "$text"
        i=$(( (i + 1) % 6 ))
        sleep 0.1
    done
}

# Update packages
{ pkg update -y -qq && pkg upgrade -y -qq; } &
loading_spinner $! "system packages"
echo ""

# Install Python and Git
{ pkg install python python-pip git -y -qq; } &
loading_spinner $! "Python and Git"
echo ""

# Install Python dependencies
{ pip install requests beautifulsoup4 colorama -q; } &
loading_spinner $! "Python modules"
echo ""

# Download main script
{ curl -sL https://raw.githubusercontent.com/saekacutie/sakea/main/main.py -o $HOME/main.py && chmod +x $HOME/main.py; } &
loading_spinner $! "main script"
echo ""

# Create alias
if ! grep -q "alias saeka=" $HOME/.bashrc 2>/dev/null; then
    echo "alias saeka='python3 $HOME/main.py'" >> $HOME/.bashrc
fi

echo ""
center_text "$(echo -e "${GREEN}${BOLD}✔ All Requirements is now on your Device${RESET}")"
echo ""
center_text "$(echo -e "${WHITE}Type ${CYAN}${BOLD}\"saeka\"${RESET}${WHITE} to run the tool${RESET}")"
echo ""
