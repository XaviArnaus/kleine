PYTHON = python3
PIP = pip3
POETRY ?= poetry
APT ?= sudo apt

ifeq (, $(shell which python ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif
PYTHON_VERSION_MIN=3.11
CURRENT_PYTHON_VERSION=$(shell $(PYTHON) -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)")
PYTHON_VERSION_OK=$(shell $(PYTHON) -c 'import sys;print(int(float("%d.%d"% sys.version_info[0:2]) >= $(PYTHON_VERSION_MIN)))' )

ifeq ($(OS), Darwin)
	OPEN := open
else
	OPEN := xdg-open
endif

.PHONY: install_system
install_system:
	$(APT) update
# Dependencies for packages to be able to build properly
	$(APT) install -y python3-dev
# Dependencies for Pillow
	$(APT) install -y libjpeg-dev zlib1g-dev libfreetype6-dev
# Dependencies for rpi.lgpio
	$(APT) install -y swig liblgpio-dev
# Dependencies for sounddevice and PyAudio
	$(APT) install -y portaudio19-dev python3-pyaudio
# Dependencies for pypub
	$(APT) install -y ffmpeg
# Dependencies for sounddevice
	$(APT) install -y portaudio19-dev
# This is not a dependency but brings tools for i2c
	$(APT) install -y i2c-tools
# Now make sure that the .bashrc has the export PATH updated for the bin folder.
	if [ -f ~/.bashrc ]; then
		echo 'export PATH="$$HOME/.local/bin:$$PATH"' >> ~/.bashrc
	fi

.PHONY: init
init:
	$(POETRY) install

.PHONY: update
update:
	$(POETRY) lock
	$(POETRY) install

.PHONY: kleine
kleine:
# Use this for a run inside Poetry. Not recommended for Raspberry Pi as uses virtual environment.
	@begin=$$(date +%s); \
	echo "Starting Kleine... \n"; \
	make run; \
	echo "\nKleine Ended...\n"; \
	end=$$(date +%s); \
	echo "Total time used: $$((end - begin)) s."

.PHONY: run
run:
	@$(POETRY) run main

.PHONY: sound_devices
sound_devices:
	@$(POETRY) run sound_devices

.PHONY: pygame_devices
pygame_devices:
	@$(POETRY) run pygame_devices

.PHONY: where-is-python
where-is-python:
	$(POETRY) run whereis $(PYTHON)

######### -------------- Raspberry Pi specific targets --------------

.PHONY: kleine-rpi
kleine-rpi:
# WARNING! DO NOT USE
# Modern OS/Python are pointing out the difference between having Python budled to support internal applications,
#	not for the end user. That's why we should always use a Virtual Environment.
#	Keeping it here for knowledge sharing, but should not be used.
#
# Use this for a run outside Poetry. Raspberry Pi as uses OS-bundled Python. Run `make rpi-install` first!
	@begin=$$(date +%s); \
	echo "Starting Kleine... \n"; \
	$(PYTHON) runner.py; \
	echo "\nKleine Ended...\n"; \
	end=$$(date +%s); \
	echo "Total time used: $$((end - begin)) s."

.PHONY: rpi-install
rpi-install:
# WARNING! DO NOT USE
# Modern OS/Python are pointing out the difference between having Python budled to support internal applications,
#	not for the end user. That's why we should always use a Virtual Environment.
#	Keeping it here for knowledge sharing, but should not be used.
#
# The Python bundled in the system has to have Python 3.11
# Check it or fail otherwise, stopping the execution.
ifeq ($(PYTHON_VERSION_OK),0)
  $(error "Needs Python Version $(PYTHON_VERSION_MIN) or above. Current Python version: $(CURRENT_PYTHON_VERSION)")
endif
# It is required to create the virtual environment and pull the dependencies.
# This way we ensure it should work with these.
	make init
# This creates the requirements file based on the dependencies above.
	$(POETRY) export -f requirements.txt --without-hashes > requirements.txt
# Now install them
	$(PIP) install -r requirements.txt