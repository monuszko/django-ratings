=======
Ratings
=======

Ratings is a flexible Django app allowing users to rate arbitrary data models.
Each data model gets its own set of criteria.

Requirements: Python 2.7, Django 1.4.5

Documentation is being added to the ``docs`` directory.

Quick start
-----------

1. Add ``ratings`` to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
       ...
       'ratings',
    )

2. Include the ratings URLconf in your project urls.py like this::

    url(r'^ratings/', include('ratings.urls', namespace='ratings')),

3. Run ``python manage.py syncdb`` to create the ratings models.

4. Display scores in your *list* views, like this::

    {% load ratings_extras %}

    {% get_list_rating_for entry as lr %}
    <p>Average: {{ lr.avg_score|floatformat:1 }},
    voters: {{ lr.num_voters }},
    standard deviation: {{ lr.std_dev|floatformat:1 }}</p>

5. Display scores in your *detail* views. Start by loading the tags and getting
   a rating object::

    {% load ratings_extras %}
    
    {% get_detail_rating_for entry as dr %}

   Display detailed stats::

    {% get_detail_rating_for entry as dr %}
    <hr>
    <ul>
        TOTAL: {{ dr.avg_score|floatformat:1 }}, Number of voters: {{ dr.num_voters }}
        {% for dic in dr.scores_by_crit %}
        <li>{{ dic.name }}: 
        <b>{{ dic.avg|floatformat:1 }}</b>,
        deviation: {{ dic.std_dev|floatformat:1 }},
        votes: {{ dic.scores }}</li>
        {% endfor %}
    </ul>
    <hr>

   Display ratings by individual users, for example::

    <p>Individual opinions:</p>
    <ol>
    {% for person in dr.scores_by_users %}
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

   Finally, put a rating form in there::

    {% if user.is_authenticated %} 
    <form action="{{ dr.form_action }}" method="POST">{% csrf_token %}
            {% for f in dr.get_forms %}
                {{ f.name }}
                {{ f.as_p }}
            {% endfor %}
        <input type="submit" value="Submit" />
    {% endif %}

   They won't display properly at first. Read on.

6. Use the admin interface to create ``Criteria`` and ``Choice`` objects.
   
   ``Criteria`` are assigned to specific content types, for example Entry
   or Page. Rating forms are generated based on these criterias.

   ``Choice`` objects determine allowed choices for scores. They are shared
   among all criterias.


Contact: marek.onuszko@gmail.com
