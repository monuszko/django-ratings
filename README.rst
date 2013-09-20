=======
Ratings
=======

Polls is a simple Django app allowing users to rate arbitrary data models.
Each data model gets its own set of criteria.

Documentation is being added to the "docs" directory.

Quick start
-----------

1. Add "ratings" to your INSTALLED_APPS setting like this::

      INSTALLED_APPS = (
          ...
          'ratings',
      )

2. Include the ratings URLconf in your project urls.py like this::

      url(r'^ratings/', include('ratings.urls')),

3. Run `python manage.py syncdb` to create the ratings models.

