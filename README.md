# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/stephendwillson/Guitar-Parts/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                              |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------- | -------: | -------: | ------: | --------: |
| controllers/song\_controller.py   |      150 |       27 |     82% |131-134, 150-153, 169-173, 191, 201, 213, 219-222, 241, 268, 274, 286-287, 318, 357, 368-369 |
| models/song.py                    |       15 |        2 |     87% |    46, 56 |
| services/db.py                    |       94 |       23 |     76% |90-93, 99, 101, 273-288, 295-305 |
| services/lastfm\_api.py           |       63 |        9 |     86% |21, 42-43, 66-68, 129-131 |
| tests/conftest.py                 |       10 |        3 |     70% |     14-16 |
| tests/test\_db.py                 |       51 |        0 |    100% |           |
| tests/test\_lastfm\_api.py        |       55 |        0 |    100% |           |
| tests/test\_main\_window.py       |      275 |        0 |    100% |           |
| tests/test\_song\_controller.py   |       91 |        0 |    100% |           |
| tests/test\_statistics\_dialog.py |       78 |        0 |    100% |           |
| utils/utils.py                    |       40 |       10 |     75% |31, 87-92, 103-106 |
| views/main\_window.py             |      548 |      125 |     77% |69-70, 245-262, 316-317, 344-346, 378, 397, 401-405, 470-477, 483-487, 522-525, 530-531, 578-580, 602-605, 661-664, 688-694, 746, 785-791, 799, 802, 804, 845-885, 892-919, 934-939, 949-954, 958-961 |
| views/statistics\_dialog.py       |      126 |       17 |     87% |124-126, 132, 156-168 |
|                         **TOTAL** | **1596** |  **216** | **86%** |           |


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