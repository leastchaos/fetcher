.ONESHELL:
SHELL = /bin/bash
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
ENV = fetcher

install_redis:
	curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
	sudo apt-get -y update
	sudo apt-get -y install redis

start_fetcher_redis:
	echo "starting redis-server conf/redis_bot.conf"
	redis-server config/redis.conf

start_app:
	echo "starting app"
	uvicorn src.app:app --reload 

start_exchange_app:
	echo "starting app server"
	uvicorn src.exchange.app:app --reload

start_exchange_server:
	echo "starting exchange server"
	$(CONDA_ACTIVATE) $(ENV)
	python src/exchange/main.py

start_wallet_app:
	echo "starting wallet app"
	uvicorn src.wallet.app:app --reload

update_ccxt:
	pip install -U git+https://github.com/leastchaos/ccxt.git#subdirectory=python