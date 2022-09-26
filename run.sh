#/bin/bash

git clone "https://github.com/2w00fs/T1A3.git"
cd T1A3
pip install kucoin-python

touch credentials.py
echo Please input your API Key
read api_key
echo api_key= \"$api_key\" >> credentials.py
echo Please input your API Secret
read api_secret
echo api_secret= \"$api_secret\" >> credentials.py
echo Please input your API Passphrase
read api_passphrase
echo api_passphrase= \"$api_passphrase\" >> credentials.py

python3 main.py
