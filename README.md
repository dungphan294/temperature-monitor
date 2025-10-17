# 🌡️ Raspberry Pi CPU Monitor and Fan Controller (MQTT-Based)

This repository contains the code for a full-stack system designed to **monitor the CPU temperature of a Raspberry Pi** in real-time and allow **remote control of a cooling fan**. The communication backbone for the entire system is the **MQTT protocol**, providing a lightweight and efficient way to send and receive data between the Raspberry Pi (the producer) and a cross-platform mobile application (the consumer/controller).

## ✨ Features

* **Real-time Temperature Monitoring:** Raspberry Pi publishes its current CPU temperature via MQTT.
* **Real-time Dashboard:** A mobile-friendly dashboard displays the temperature data as a live chart.
* **Remote Fan Control:** Users can toggle the cooling fan **ON/OFF** from the mobile application.
* **Cross-Platform Mobile App:** Built with **Ionic** and **Capacitor**, enabling deployment to iOS, Android, and the web.
* **Lightweight Communication:** Uses **MQTT** for low-latency, low-bandwidth data exchange.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Data Publisher (Raspberry Pi)** | **Python 3.x** | Collects CPU temperature and publishes it to an MQTT broker. |
| **Data Protocol** | **MQTT** | The communication protocol for real-time data transfer. |
| **Client/Dashboard (Mobile App)** | **Ionic 7** (Angular) | Front-end framework for the cross-platform application. |
| **Native Bridge** | **Capacitor** | Wraps the Ionic app into native mobile apps (iOS/Android). |
| **Real-time Plotting** | **Charting Library** | Used within the Ionic app to plot the temperature data. |

---

## 📂 Repository Structure

The project is divided into two main sections: the Python scripts for the Raspberry Pi and the Ionic/Capacitor application.

```txt
.
├── monitorApp/            # The Ionic/Capacitor Mobile Application
│   ├── src/
│   │   ├── app/
│   │   │   ├── home/            # Main temperature dashboard and fan control page
│   │   │   └── services/
│   │   │       └── mqtt.service.ts  # MQTT client logic for subscribe/publish
│   ├── android/             # Android project files (Capacitor)
│   └── ios/                 # iOS project files (Capacitor)
├── utils/                 # General Python utility scripts (e.g., to read CPU temp)
├── test_component/        # Python scripts for testing components (fan, OLED, MQTT)
│   ├── fan.py             # Script to control the cooling fan (likely via GPIO)
│   └── mqtt.py            # Basic MQTT publisher/subscriber test
├── requirements.txt       # Python dependencies
└── demo.gif               # Project demonstration (as per file list)
```

---

## Getting Started

Follow these steps to set up the Raspberry Pi publisher and the mobile application.

### 1. Prerequisites

Before starting, you'll need:

* A Raspberry Pi (with an attached fan/GPIO setup if fan control is desired).
* An MQTT Broker (e.g., Mosquitto running locally or a public broker).
* Python 3 and Node.js/npm installed on their respective machines.

### 2. Raspberry Pi Setup (Publisher)This part handles collecting the temperature and publishing it

#### A. Install Dependencies

On your Raspberry Pi, navigate to the root of the cloned repository and install the Python requirements:

```Bash
pip install -r requirements.txt
```

#### B. Configuration

You'll need to configure the MQTT broker details (address, port, topics) within the Python scripts (likely in test_component/mqtt.py or a dedicated config file if you created one).The main topics used are:

| Function | Topic | Direction |
| :--- | :--- | :--- |
| Publish Temperature | rpi/cpu/temperature | Pi → Broker |
| Subscribe Fan State | rpi/fan/control | Broker → Pi |

#### C. Run the Publisher

Execute the main Python script responsible for reading the temperature and publishing the data:Bash# Example command, depending on which script is your main one

```bash
python3 test_component/fan.py
```

### 3. Mobile App Setup (Subscriber/Controller)

This part sets up the real-time dashboard and fan control interface.

#### A. Navigate to the App Directory

```Bash
cd monitorApp
```

#### B. Install Dependencies

Install the Ionic/Angular and Capacitor dependencies:

```Bash
npm install
```

#### C. Configure MQTT Service

Open `src/app/services/mqtt.service.ts` and update the following to match your environment:

- MQTT Broker details: Host, Port, and any necessary credentials.
- Subscription Topic: Ensure it is subscribed to rpi/cpu/temperature.
- Publication Topic: Ensure it publishes to rpi/fan/control.

#### D. Run the AppYou can run the app in a browser for testing or build for a native device.

Browser Testing:

```Bash
ionic serve
```

Build and Run on a Device (Requires Android Studio/Xcode):Bash# Add the platform (if not already done)

```Bash
npx capacitor add android
npx capacitor add ios

# Sync web assets to native project
npx capacitor sync

# Open the native IDE to build and run
npx capacitor open android # or ios
```

🖼️ Demonstration

A brief GIF showing the application in action:

![demo](demo.gif)
