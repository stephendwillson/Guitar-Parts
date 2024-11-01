# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/stephendwillson/Guitar-Parts/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                            |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------- | -------: | -------: | ------: | --------: |
| controllers/song\_controller.py |      120 |       39 |     68% |129-132, 148-151, 167-171, 189, 199, 211, 217-220, 239, 252-253, 266, 272, 284-285, 306-325 |
| models/song.py                  |       11 |        1 |     91% |        48 |
| services/db.py                  |       61 |       19 |     69% |59-60, 193-208, 215-225 |
| services/lastfm\_api.py         |       59 |        8 |     86% |37-38, 60-62, 123-125 |
| tests/test\_db.py               |       47 |        0 |    100% |           |
| tests/test\_lastfm\_api.py      |       55 |        0 |    100% |           |
| tests/test\_main\_window.py     |      220 |        0 |    100% |           |
| tests/test\_song\_controller.py |       91 |        0 |    100% |           |
| utils/utils.py                  |       27 |        5 |     81% |     74-79 |
| views/main\_window.py           |      459 |      107 |     77% |197-214, 259-262, 287-289, 321, 340, 344-348, 413-420, 426-430, 465-468, 473-474, 515-517, 538-542, 589-592, 616-622, 693-699, 707, 710, 712, 726-744, 750-788, 804-809, 813-816 |
|                       **TOTAL** | **1150** |  **179** | **84%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/stephendwillson/Guitar-Parts/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/stephendwillson/Guitar-Parts/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/stephendwillson/Guitar-Parts/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/stephendwillson/Guitar-Parts/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fstephendwillson%2FGuitar-Parts%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/stephendwillson/Guitar-Parts/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.