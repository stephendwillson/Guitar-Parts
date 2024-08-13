# Guitar Parts
Developed for personal use but might be useful to others with the same problem.

I play guitar and try to learn as many songs as I can but I often forget which songs I've learned or which parts of songs I've learned. This is meant to be a place where I can store the songs I've learned and leave a note on which parts I've learned, the song structure, the chord progressions, or anything that might help me remember the part. The goal is to be able to randomly pick a few tracks to practice to keep fingers and brain fresh.

The app uses the Last.fm API to fetch song details based on the title and artist. You can add custom songs, but most metadata fields will be empty.

## Getting Started

### Requirements

**Note**: This application has been tested on Fedora Linux. It should work on other Linux distros and platforms but these platforms have not been explicitly tested.

#### Python
Ensure Python (3.6 or higher) is installed. It can be downloaded from [python.org](https://www.python.org/downloads/).

##### Windows
1. Download and install Python from the official [Python website](https://www.python.org/downloads/windows/).
2. Make sure to check the box that says "Add Python to PATH" during installation.

##### macOS
1. Download and install Python from the official [Python website](https://www.python.org/downloads/macos/).
2. Alternatively, Homebrew can be used:
   ```sh
   brew install python
   ```

##### Linux
Most Linux distributions come with Python pre-installed. If Python is not installed, it can be installed using the package manager. For example, on Debian-based systems:
```sh
sudo apt-get update
sudo apt-get install python3
```

### Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/stephendwillson/Guitar-Parts.git
   cd guitar-parts
   ```

2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

3. Set the required environment variables:
   ```sh
   cp .env.example .env
   # Edit .env to include your Last.fm API key
   # Change syntax as needed per platform

   source .env
   ```
See [Last.fm API Key](#lastfm-api-keys) for details on obtaining a Last.FM API key.

### Running Application
```sh
python guitar_parts.py
```

## Development

### Setting up Development Environment

#### Virtual Environment
It's recommended to use a virtual environment for dependency management. From project root directory:
```sh
# Create virtual environment
python3 -m venv venv

# Activate venv (Linux/macOS)
source venv/bin/activate

# Activate venv (Windows)
venv\Scripts\activate
```

#### Python modules
```sh
pip install -r requirements.txt
```

#### Run Application
```sh
python guitar_parts.py
```

### Running Tests

Tests can be run with a coverage report generated via `task`:
1. Install `task` per install instructions for your platform: [Task Install](https://taskfile.dev/installation/)
2. Run tasks:
```sh
task run_tests_and_generate_coverage
```
The coverage report can be viewed at `project_root/htmlcov/index.html`.

Alternatively, you can run tests and generate a basic coverage report via `pytest` directly:
```sh
pytest --cov=.
```

## Last.fm API Keys
To use the Last.fm API, you need to obtain your own API keys. Sign up for an account and get your API key and secret from [Last.fm API](https://www.last.fm/api).

Set the following environment variables with your API key and secret:
```
API_KEY=your_key_here
API_SECRET=your_secret_here
```

You can set these variables manually or by creating a `.env` file in the root directory of your project and exporting them there. Before running or developing, load the environment variables:
```sh
source .env
```
