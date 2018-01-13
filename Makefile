ENV_TYPE?=devel
ENV_USER?=cestiadvokati.cz
WORKING_DIR?=/home/$(ENV_USER)/analysis-$(ENV_TYPE)
PYTHON_ENV?=$(ENV_TYPE)-analysis

deploy:
	sudo rm -rf $(WORKING_DIR); \
	sudo cp -r . $(WORKING_DIR); \
	sudo chown $(ENV_USER):$(ENV_USER) -R $(WORKING_DIR); \
	sudo chmod 775 $(WORKING_DIR);
