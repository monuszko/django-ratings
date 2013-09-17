=======
Ratings
=======

Polls is a simple Django app to conduct Web-based ratings. For each
question, visitors can choose between a fixed number of answers.

Detailed documentation is in the "docs" directory.

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

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/ratings/ to participate in the poll.
