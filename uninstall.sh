# This script is the uninstallation script of dlfetch
dir=$(pwd)
echo "Removing dlfetch directory..."
rm -rf "$HOME/dlfetch"
echo "Cleaning up ~/.zshrc..."
sed -i '' '/# DLFetch start/,/# DLFetch end/d' "$HOME/.zshrc"
echo "Removing session..."
rm -r "$HOME/.dlfetch_session"
echo "Uninstallation finished!"
cd "$dir" || exit 1
