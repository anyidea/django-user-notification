# Django user notification

[![Build Status](https://img.shields.io/github/workflow/status/anyidea/django-user-notification/CI/master)](https://github.com/anyidea/django-user-notification/actions?query=workflow%3ACI)
[![GitHub license](https://img.shields.io/github/license/anyidea/django-user-notification)](https://github.com/anyidea/django-user-notification/blob/master/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/django-user-notification/badge/?version=latest)](https://django-user-notification.readthedocs.io/en/latest/?badge=latest)
[![pypi-version](https://img.shields.io/pypi/v/django-user-notification.svg)](https://pypi.python.org/pypi/django-user-notification)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-user-notification)
[![PyPI - Django Version](https://img.shields.io/badge/django-%3E%3D3.1-44B78B)](https://www.djangoproject.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Overview
-----
Django user notification is intended to provide a way to send multiple types of notification messages to django users out of box.

Documentation
-----
on the way...

Requirements
-----

* Python 3.8, 3.9, 3.10
* Django 3.1, 3.2, 4.0, 4.1

Installation
-----

Install using `pip`...

    pip install django-user-notification

Add `'tinymce'` and `'notification'` to your `INSTALLED_APPS` setting.
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
    'tinymce',
    'notification',
]
```

Quick Start
-----

Let's take a look at a quick start of using Django user notification to send notification messages to users.

Run the `notification` migrations using:

    python manage.py migrate notification


Add the following to your `settings.py` module:

```python
INSTALLED_APPS = [
    ...  # Make sure to include the default installed apps here.
    'tinymce',
    'notification',
]

DJANGO_USER_NOTIFICATION = {
    "aliyunsms": {
        "access_key_id": "Your Access Key ID",
        "access_key_secret": "Your Access Key Secret",
        "sign_name": "Your Sign Name",
    },
    "dingtalkchatbot": {
        "webhook": "Your Webhook URL",
    },
    "dingtalkworkmessage": {
        "agent_id": "Your App Agent ID",
        "app_key": "Your App Key",
        "app_secret": "Your App Secret",
    },
    "dingtalktodotask": {
        "app_key": "Your App Key",
        "app_secret": "Your App Secret",
    },
}
```

Add `tinymce.urls` to `urls.py` for your project:
```python
urlpatterns = [
    ...
    path('tinymce/', include('tinymce.urls')),
    ...
]
```

Let's send a notification

``` {.python}
from django.contrib.auth import get_user_model
from notification.backends import notify_by_email, notify_by_dingtalk_workmessage

User = get_user_model()

recipient = User.objects.first()

# send a dingtalk work message notification
notify_by_dingtalk_workmessage([recipient], phone_field="phone", title="This is a title", message="A test message")


# send a email notiofication
notify_by_email([recipient], title="This is a title", message="A test message")
```


Send Message With Template
--------------

`django-user-notification` support send notifications with custom template, To
specify a custom message template you can provide the `template_code`
and `context` parameters.

1)  Create a template message with code named `TMP01` on django admin

2)  Provide the `template_code` and `context` to `send` method:
``` {.python}
...

notify_by_email([recipient], template_code="TMP01", context={"content": "Hello"})
```

Supported backends
-----------------------------

- `DummyNotificationBackend`: send dummy message
- `EmailNotificationBackend`: send email notification.
- `WebsocketNotificationBackend`: send webdocket notification, need install extension: `channels`.
- `AliyunSMSNotificationBackend`: send aliyun sms notification, need install extension: `aliyunsms`.
- `DingTalkChatbotNotificationBackend`: send dingtalk chatbot notification.
- `DingTalkToDoTaskNotificationBackend`: send dingtalk todo tasks notification
- `DingTalkWorkMessageNotificationBackend`: send dingtalk work message notification.
- `WechatNotificationBackend`: planning...

Running the tests
-----------------

To run the tests against the current environment:

``` {.bash}
$ pytest tests/
```

Changelog
---------

### 0.7.0

-   Initial release

Contributing
------------
As an open source project, we welcome contributions. The code lives on [GitHub](https://github.com/anyidea/django-user-notification/)

## Thanks

[![PyCharm](docs/pycharm.svg)](https://www.jetbrains.com/?from=django-user-notification)
