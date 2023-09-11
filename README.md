# BlogVoyage_project# BlogVoyage
## _Social network for bloggers and even more_

[![N|Solid](https://static.djangoproject.com/img/logos/django-logo-negative.svg)](https://www.djangoproject.com/)

BlogVoyage is a project for learning, testing and improving skills on python, django, sql etc.

## Features*
- You can post blogs, commentaries and follow other users
- You can put images to your posts
- Admin interface to control the site with superuser permissions
- Could start a DEV server


## Tech

BlogVoyage uses a number of open source projects to work properly:

- [Python] - Python 3.9
- [Django] - Web framework to rule them all!


And of course BlogVoyage itself is open source with a [public repository][Rexant-b2k]
 on GitHub.

## Installation

BlogVoyage requires [Django] v2.2.19 to run.

Install the dependencies and devDependencies and start the server (Linux/MacOS example).

```sh
cd BlogVoyage
python -m pip install --upgrade pip
python -m venv venv
source venv/bin/activate
```

For production environments (automatic)...

```sh
pip install -r requirements.txt
```
or manual:
```sh
pip install Django==2.2.19
```

## Running server
```sh
venv..$ .../BlogVoyage/BlogVoyage: python manage.py runserver
```

Then: **Open 127.0.0.1:8000 in your browser**

## Plugins

BlogVoyage is currently extended with the following plugins.
Instructions on how to use them in your own application are linked below.

| Plugin | README |
| ------ | ------ |
| Dillinger | [https://dillinger.io/][Dill] |



## License

BSD-3 Clause License

**Free Software, Hello everybody**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [Rexant-b2k]: <https://github.com/Rexant-b2k>
   [git-repo-url]: <https://github.com/Rexant-b2k/BlogVoyage_project.git>
   [Django]: <https://www.djangoproject.com>
   [Python]: <https://www.python.org/>


   [Dill]: <https://dillinger.io/>

