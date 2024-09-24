# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/stephendwillson/Guitar-Parts/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                            |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------- | -------: | -------: | ------: | --------: |
| controllers/song\_controller.py |      120 |       39 |     68% |129-132, 148-151, 167-171, 189, 199, 211, 217-220, 239, 252-253, 266, 272, 284-285, 306-325 |
| models/song.py                  |       11 |        1 |     91% |        48 |
| services/db.py                  |       61 |       19 |     69% |59-60, 193-208, 215-225 |
| services/lastfm\_api.py         |       56 |        7 |     88% |19, 55-57, 118-120 |
| tests/test\_db.py               |       47 |        0 |    100% |           |
| tests/test\_lastfm\_api.py      |       55 |        0 |    100% |           |
| tests/test\_main\_window.py     |      220 |        0 |    100% |           |
| tests/test\_song\_controller.py |       91 |        0 |    100% |           |
| utils/utils.py                  |       27 |        5 |     81% |     74-79 |
| views/main\_window.py           |      426 |       81 |     81% |187-204, 249-252, 277-279, 311, 330, 334-338, 403-410, 416-420, 455-458, 463-464, 505-507, 528-532, 579-582, 606-612, 683-689, 697, 700, 702, 716-734, 751-756, 760-763 |
|                       **TOTAL** | **1114** |  **152** | **86%** |           |


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