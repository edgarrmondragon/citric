Citric
======

A client to the LimeSurvey Remote Control API 2, written in modern
Python.

.. toctree::
   :maxdepth: 1

   license

.. toctree::
   :maxdepth: 4

   API <_api/index>

Installation
------------

Using ``pip``:

.. code-block:: console

   $ pip install citric

Usage
-----

.. code-block:: python

   from citric import Client

   LS_URL = 'http://my-ls-server.com/index.php/admin/remotecontrol'

   with Client(LS_URL, 'iamadmin', 'secret') as client:
       # Get all surveys from user 'iamadmin'
       surveys = client.list_surveys('iamadmin')

       for s in surveys:
           print(s["surveyls_title"])

           # Get all questions, regardless of group
           questions = client.list_questions(s["sid"])
           for q in questions:
               print(q["title"], q["question"])

Or more interestingly, export responses to a ``pandas`` dataframe:


.. code-block:: python

       import io
       import pandas as pd

       survey_id = 123456

       df = pd.read_csv(
           io.BytesIO(client.export_responses(survey_id, file_format="csv")),
           delimiter=";",
           parse_dates=["datestamp", "startdate", "submitdate"],
           index_col="id",
       )
