# AccessEngineeringLibrary Downloader

A Python application that can automatically download all chapters from [Access Engineering Library](https://www.accessengineeringlibrary.com) and merge them into a fully readable PDF file.

**Requires:** Access to Access Engineering Library

_Currently supported_: RMIT University([.vn](rmit.edu.vn)|[.au](rmit.edu.au)) Login

## Installation

### Run from compiled executables

- Go to [releases](https://github.com/Khang5687/simple-ebook-scraper/releases) tab to download compatible executable

### Run from source

- Download and Install [Python](https://www.python.org/)
- Clone the repo

```bash
git clone https://github.com/Khang5687/simple-ebook-scraper.git
cd simple-ebook-scraper
```

- Install required dependencies

```bash
pip install -r requirements.txt
```

- Run the app

```bash
python main.py
```

## Known Issue

- Google Chrome may not properly exits after a login session, which uses up most of the system's CPU and Ram, causing system instability and stutters. This typically only happens when you login to your RMIT account, which uses Chrome to get your cookies session. *Will get addressed in the **next version***

  **Temporary fix**: NOTE THAT THIS WOULD CLOSE ALL PROCESSES OF **CHROME**, make sure to save your work before you run these commands!

    - **Windows**: `taskkill /im chrome.exe /f`
    - **MacOS**: `killall -9 "Google Chrome"`
    - **GNU/Linux**: `pkill -9 chrome`

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[GNU Affero General Public License v3.0](https://github.com/Khang5687/simple-ebook-scraper/blob/main/LICENSE)
