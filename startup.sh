~/darkscript.sh

# Set horizontal scrolling as normal
echo
echo ---------------------------------
echo scrolling distance xinput setting prop
echo ---------------------------------
echo
# xinput set-prop 13 332 -228, -228
xinput set-prop 13 331 -228, -228

# Disable touch input
# xinput disable 11
# xinput disable 12
echo
echo ---------------------------------
echo Mounting D Drive
echo ---------------------------------
echo
sudo mkdir /media/vivojay/DATA/
sudo mount /dev/sda1 /media/vivojay/DATA/

echo
echo ---------------------------------
echo Mounting C Drive
echo ---------------------------------
echo
sudo mkdir /media/vivojay/Windows/
sudo mount /dev/nvme0n1p3 /media/vivojay/Windows/

echo
echo ---------------------------------
echo "Killing Komorebi (Background thing)"
echo ---------------------------------
echo
pkill -9 -f "komorebi"

echo
echo ---------------------------------
echo Opening imp links in brave
echo ---------------------------------
echo
python3 ~/startup_helper_1.py

# Run Ubuntu Update
echo
echo ---------------------------------
echo preparing to run updates
echo ---------------------------------
echo
sudo apt update
sudo apt-get upgrade
sudo apt-get update

echo
echo ---------------------------------
echo Quick Pic disp
echo ---------------------------------
echo
#kitty python3 /media/vivojay/DATA/Vivo\ Jay/tools/file_view.py "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/mae/EM/31.jpg.enc"
kitty python3 "/media/vivojay/VIVOSANDISK/VIVAN/personal/__past__/up-here-s1/1684162410_197_(vlc)_[Vivo Jay_VIVO-JAY].png.enc"

echo
echo ---------------------------------
echo Initiating mariana
echo ---------------------------------
echo
~/mariana.sh
