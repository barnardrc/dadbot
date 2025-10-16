# Dark and Darker Automated Trading Bot

![Animated demo of the trading bot in action](assets/demo.gif)

An automated trading bot for the game Dark and Darker that uses computer vision (pytesseract) and screen automation to identify and execute profitable trades in the in-game market.

***

## ⚠️ EXTREME WARNING: USE AT YOUR OWN RISK ⚠️

**This project is for educational purposes only. Using this bot is a direct violation of the Dark and Darker Terms of Service and will likely result in a permanent ban of your game account.** The author of this software is not responsible for any disciplinary action taken against you. You assume all risks by downloading, running, or using this code.

***

## How It Works

The bot operates in a simple loop:
1.  **Screen Capture:** Takes a screenshot of the in-game trade window.
2.  **OCR Data Reading:** Uses `pytesseract` to perform Optical Character Recognition (OCR) on the image, extracting item names, prices, and stats.
3.  **Profit Calculation:** Processes the extracted data to determine if an item is listed below its calculated market value, indicating a profitable trade.
4.  **Automated Interaction:** If a profitable trade is found, the bot uses `pyautogui` to simulate mouse clicks to purchase the item.
5.  **Refresh and Repeat:** The bot refreshes the trade window and repeats the cycle.

## Features

* Automated screen reading of the trade market.
* Calculates potential profit based on user-defined criteria.
* Automatically purchases items identified as profitable.
* Configurable settings for refresh rates and profit margins.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```
2.  **Install dependencies:** Ensure you have Python 3.x installed.
    ```bash
    pip install -r requirements.txt
    ```
3.  **Install Tesseract OCR:** You must install Google's Tesseract engine. Follow the instructions for your operating system:
    * [Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)
    * For macOS/Linux, use your package manager (e.g., `sudo apt-get install tesseract-ocr` or `brew install tesseract`).
    * **Important:** You may need to add the Tesseract installation path to your system's PATH variable.

4.  **Configure the Bot:** Open `config.ini` (or your configuration file) and adjust the settings to match your screen resolution and desired trading parameters.

## Usage

1.  Launch Dark and Darker and navigate to the trade market.
2.  Ensure the game is running in windowed or borderless windowed mode.
3.  Run the main Python script from your terminal:
    ```bash
    python main.py
    ```
4.  To stop the bot, press the designated hotkey (e.g., F12) or close the terminal window.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

