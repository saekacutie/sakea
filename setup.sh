#!/bin/bash
clear
G='\033[0;32m'; C='\033[0;36m'; W='\033[1;37m'; B='\033[1m'; R='\033[0m'
w=$(stty size 2>/dev/null | cut -d' ' -f2 || echo 80)
c(){ local t="$1"; local cl=$(echo -e "$t"|sed 's/\x1b\[[0-9;]*m//g'); local p=$(((w-${#cl})/2)); [ $p -lt 0 ]&&p=0; printf "%*s%b\n" $p "" "$t"; }
echo ""; echo ""; c "${C}${B}SAEKA TOOL${R}"; echo ""
s(){ local pid=$1 pkg=$2 fr='◜◠◝◞◡◟' i=0; while kill -0 $pid 2>/dev/null; do local f="${fr:$i:1}"; local t="Installing ${pkg}..."; local cl=$(echo -e "$t"|sed 's/\x1b\[[0-9;]*m//g'); local pad=$(((w-${#cl}-2)/2)); [ $pad -lt 0 ]&&pad=0; printf "\r%*s%s %s" $pad "" "$f" "$cl"; i=$(((i+1)%6)); sleep 0.1; done; printf "\r%*s✔ %s\n" $pad "" "$cl"; }
(pkg update -y -qq && pkg upgrade -y -qq) &>/dev/null & s $! "system packages"
(pkg install python python-pip git -y -qq) &>/dev/null & s $! "Python and Git"
(pip install requests beautifulsoup4 colorama -q) &>/dev/null & s $! "Python modules"
(curl -sL https://raw.githubusercontent.com/saekacutie/sakea/main/main.py -o $HOME/main.py && chmod +x $HOME/main.py) &>/dev/null & s $! "main script"
grep -q "alias saeka=" $HOME/.bashrc 2>/dev/null || echo "alias saeka='python3 $HOME/main.py'" >> $HOME/.bashrc
echo ""; c "${G}${B}✔ All Requirements is now on your Device${R}"; echo ""; c "${W}Type ${C}${B}\"saeka\"${R}${W} to run the tool${R}"; echo ""
