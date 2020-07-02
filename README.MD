# What is Wagtail Gatsby

Wagatil Gatsby is an **experimental** library for intergrating Gatsby and Wagtail CMS (in conjunction with Wagtail Grapple). It provides the three features:
- Detect when pages are published and send a POST request to a desired HTTP endpoint (Netlify, Travis CI, etc).
- Creates a ModelAdmin that allows you to manually deploy to your frontend host.
- Gatsby Image processing (Now Deprecated, Please see [gatsby-source-wagatil's](https://github.com/NathHorrigan/gatsby-source-wagtail) repo on local image processing).

## Install

- Install package via PIP:

```
https://pypi.org/project/wagtailgatsby/
```


- Add to `INSTALLED_APPS`:

```
INSTALLED_APPS = [
  ...
  "wagtail_gatsby",
  ...
]
```

- Run Django Migrations:

```
python ./manage.py migrate
```

### Publishing Triggers

To have your frontend triggered when a pageis published inside of Wagtail add the following to your `base.py`

```
GATSBY_AUTO_DEPLOY = env.get("GATSBY_AUTO_DEPLOY", True)
GATSBY_TRIGGER_URL = env.get("GATSBY_TRIGGER_URL", "SOME-NETLIFY-URL"
```
