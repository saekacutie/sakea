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

get_width() {
    stty size 2>/dev/null | cut -d' ' -f2 || echo 80
}

center_text() {
    local text="$1"
    local width=$(get_width)
    local clean_text=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
    local pad=$(( (width - ${#clean_text}) / 2 ))
    [ $pad -lt 0 ] && pad=0
    printf "%*s%b\n" $pad "" "$text"
}

clear
echo ""
echo ""
center_text "${CYAN}${BOLD}SAEKA TOOL${RESET}"
echo ""

loading_spinner() {
    local pid=$1
    local package=$2
    local frames='◜◠◝◞◡◟'
    local i=0
    while kill -0 $pid 2>/dev/null; do
        local frame="${frames:$i:1}"
        local text="Installing ${package}..."
        local width=$(get_width)
        local total=$(( ${#text} + 2 ))
        local pad=$(( (width - total) / 2 ))
        [ $pad -lt 0 ] && pad=0
        printf "\r%*s%s %s" $pad "" "$frame" "$text"
        i=$(( (i + 1) % 6 ))
        sleep 0.1
    done
    printf "\r%*s%s %s\n" $pad "" "✔" "$text"
}

# Suppress all output
exec 3>&2
exec 2>/dev/null

{ pkg update -y -qq && pkg upgrade -y -qq; } &
loading_spinner $! "system packages"

{ pkg install python python-pip git -y -qq; } &
loading_spinner $! "Python and Git"

{ pip install requests beautifulsoup4 colorama -q; } &
loading_spinner $! "Python modules"

{ curl -sL https://raw.githubusercontent.com/saekacutie/sakea/main/main.py -o $HOME/main.py && chmod +x $HOME/main.py; } &
loading_spinner $! "main script"

# Restore stderr
exec 2>&3

if ! grep -q "alias saeka=" $HOME/.bashrc 2>/dev/null; then
    echo "alias saeka='python3 $HOME/main.py'" >> $HOME/.bashrc
fi

echo ""
center_text "${GREEN}${BOLD}✔ All Requirements is now on your Device${RESET}"
echo ""
center_text "${WHITE}Type ${CYAN}${BOLD}\"saeka\"${RESET}${WHITE} to run the tool${RESET}"
echo ""
