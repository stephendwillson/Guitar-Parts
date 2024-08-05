# Guitar Parts
Developed for personal use but might be useful to others with the same problem.

I play guitar and try to learn as many songs as I can but I often forget which songs I've learned or which parts of songs I've learned. This is meant to be a place where I can store the songs I've learned and leave a note on which parts I've learned, the song structure, the chord progressions, or anything that might help me remember the part. The goal is to be able to randomly pick a few tracks to practice to keep fingers and brain fresh.

The app uses the Last.fm API to fetch song details based on the title and artist. You can add custom songs, but most metadata fields will be empty.


## Requirements
### Python
Ensure Python (3.6 or higher) is installed. It can be downloaded from [python.org](https://www.python.org/downloads/).

#### Windows
1. Download and install Python from the official [Python website](https://www.python.org/downloads/windows/).
2. Make sure to check the box that says "Add Python to PATH" during installation.

#### macOS
1. Download and install Python from the official [Python website](https://www.python.org/downloads/macos/).
2. Alternatively, Homebrew can be used:
   ```sh
   brew install python
   ```

#### Linux
1. Most Linux distributions come with Python pre-installed. If Python is not installed, it can be installed using the package manager. For example, on Debian-based systems:
   ```sh
   sudo apt-get update
   sudo apt-get install python3
   ```

### Virtual Environment
It's recommended to use a virtual environment for dependency management. From project root directory:
```sh
# Create virtual environment
python3 -m venv venv

# Activate venv (Linux/macOS)
source venv/bin/activate

# Activate venv (Windows)
venv\Scripts\activate
```

### Python modules
```sh
pip install pytest pytest-qt PyQt6 titlecase requests python-dotenv
```

### Last.fm API Keys
To use the Last.fm API, you need to have your own API keys:

1. Sign up for a Last.fm API account and get your API key and secret from [Last.fm API](https://www.last.fm/api).
2. Create a file named `.env` in the root directory of your project.
3. Add the following lines to `.env` and replace the placeholders with actual API key and secret:
   ```
   API_KEY=your_key_here
   API_SECRET=your_secret_here
   ```

   Note if you run a different shell like Fish, change the env var syntax as needed:
      ```
      set -x API_KEY 'your_key_here'
      set -x API_SECRET 'your_secret_here'
      ```

## Run Application
```sh
python guitar_parts.py
```