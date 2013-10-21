=======
Ratings
=======

Ratings is a Django app allowing users to rate arbitrary data models.
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

4. Modify your ``models.py`` and make your models inherit from RatedModel::

    from ratings.models import RatedModel


  class Entry(RatedModel):


5. Insert rating forms in your templates, like this::

    {% load url from future %}
    {% load ratings_extras %}


    {% if user.is_authenticated %}
        <form action="{{ entry.get_rate_url }}" method="POST">{% csrf_token %}
        {% for f in entry|get_forms:user %}
        {{ f.name }} ({{ f.min }}-{{ f.max }}):
          {{ f.as_p }}
        {% endfor %}
        <input type="submit" value="Submit" />
    {% endif %}

5. Display scores in your templates. In list view::

    <p>Average: {{ entry.avg_score|floatformat:1 }}, voters: {{ entry.get_voters }}</p>

   In detail view::

    <ul>
    TOTAL: {{ entry.avg_score }}, Number of voters: {{ custompage.get_voters }}
    {% for dic in entry.scores_by_crit %}
    <li>{{ dic.name }}: <b>{{ dic.avg|floatformat:1 }}</b>, deviation: {{ dic.std_dev|floatformat:1 }}, votes: {{ dic.scores }}</li>
    {% endfor %}
    </ul>

   In detail view, as a list of user comments::
 
    <ol>
    {% for person in entry.scores_by_users %}
    <li><dl>
        <dt>username</dt>
        <dd>{{ person.username }}</dd>
        <dt>Date</dt>
        <dd>{{ person.pub_date }}
        <dt>Total</dt>
        <dd>{{ person.avg }}
        <dt>Subscores</dt>
        <dd>
        <ul>
            {% for crit in person.by_crit %}
                <li><p>{{ crit.name }} - {{ crit.value }}</p>
                    <p>Comment - {{ crit.comment }}</p>
                </li>
            {% endfor %}
        </ul>
        </dd>
    </dl></li>
    {% endfor %}
    </ol>

