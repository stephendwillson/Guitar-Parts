# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/stephendwillson/Guitar-Parts/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                            |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------- | -------: | -------: | ------: | --------: |
| controllers/song\_controller.py |       42 |       11 |     74% |58, 76, 86, 95, 129, 135-138, 170-171 |
| models/song.py                  |       11 |        1 |     91% |        48 |
| services/db.py                  |       42 |        8 |     81% |     51-70 |
| services/lastfm\_api.py         |       54 |        4 |     93% | 19, 53-55 |
| tests/test\_db.py               |       47 |        0 |    100% |           |
| tests/test\_lastfm\_api.py      |       55 |        0 |    100% |           |
| tests/test\_main\_window.py     |      112 |        0 |    100% |           |
| utils/utils.py                  |       27 |        5 |     81% |     74-79 |
| views/main\_window.py           |      268 |       58 |     78% |194-218, 259, 286-288, 300-316, 374-380, 387-403, 406-410, 477-480 |
|                       **TOTAL** |  **658** |   **87** | **87%** |           |


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