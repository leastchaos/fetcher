.ONESHELL:
SHELL = /bin/bash
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

install_redis:
	curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
	echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
	sudo apt-get -y update
	sudo apt-get -y install redis

start_fetcher_redis:
	echo "starting redis-server conf/redis_bot.conf"
	redis-server fetcher/config/redis.conf

start_app:
	echo "starting app server"
	uvicorn fetcher.app:app --reload