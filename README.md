# cortex_fe

To set up:
git clone https://github.com/kx499/cortex_fe.git
virtualenv cortex_fe
cd cortex_fe
bin/pip install -r requirements.txt

running:
./run.py

Note: if not running on localhost, add host=0.0.0.0 to app.run() in run.py, or use ./run.py --prod

On Debian or Ubuntu systems, you will need to sudo apt install git python-virtualenv python-pip python-dev
