# Guitar Parts

![Coverage Badge](https://raw.githubusercontent.com/stephendwillson/Guitar-Parts/python-coverage-comment-action-data/badge.svg)

Developed for personal use but might be useful to others with the same problem.

I play guitar and try to learn as many songs as I can but I often forget which songs I've learned or which parts of songs I've learned. This is meant to be a place where I can store the songs I've learned and leave a note on which parts I've learned, the song structure, the chord progressions, or anything that might help me remember the part. The goal is to be able to randomly pick a few tracks to practice to keep fingers and brain fresh. There's also some useful statistics to help contextualize the practice.

The app uses the Last.fm API to fetch song details based on the title and artist. You can add custom songs, but most metadata fields will be empty.

## Quick Start
Download the release for your platform from the [Releases](https://github.com/stephendwillson/Guitar-Parts/releases) page.

## Development

### Requirements

**Note**: This application has been tested on Fedora Linux. It should work on other Linux distros and platforms but these platforms have not been explicitly tested.

#### (Optional) Virtual Environment
It's recommended to use a virtual environment for dependency management. From project root directory:
```sh
# Create virtual environment
python3 -m venv venv

# Activate venv (Linux/macOS)
source venv/bin/activate
```

#### Python
Ensure [Python](https://www.python.org/downloads/) (3.6 or higher) is installed.

See [Last.fm API Key](#lastfm-api-keys) for details on obtaining a Last.FM API key.

#### Python modules
```sh
pip install -r requirements.txt
```

### Running Application
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
To enable song metadata fetching, you can configure Last.fm API credentials. Sign up for an account and get your API key and secret from [Last.fm API](https://www.last.fm/api).

You can configure the API credentials through any of the following:
* File > Settings in the application
* Manual environment variable setup:
   ```sh
   API_KEY=your_key_here
   API_SECRET=your_secret_here
   ```
* Create a `.env` file in the root directory of your project and export them there.

## Known Issues

- Last.fm will sometimes prioritize compilations or live albums over the original studio album. For example, a query for Led Zeppelin's "Rain Song" returns the album as "Tour Over Europe 1980". Looking through Last.fm API support forums, this is a known issue and is unlikely to be solved anytime soon.

   See the following forum topics for more information:

   - [Last.fm API - How to get the original album instead of these compilations?](https://support.last.fm/t/how-to-get-the-original-album-instead-of-these-compilations/60771/7)
   - [Last.fm API - Future of the API?](https://support.last.fm/t/future-of-the-api/89942/5)

