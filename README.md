# Temperature Monitor

## Navigate to: Interface Options → I2C → Enable

```bash
sudo raspi-config  
```

```bash
sudo apt install i2c-tools
i2cdetect -y 1
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install adafruit-circuitpython-ssd1306
```