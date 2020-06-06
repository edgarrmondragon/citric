Citric
=======

|Documentation Status|
|Updates| |Python 3| |codecov| |Tests|

A client to the LimeSurvey Remote Control API 2, written in modern
Python.

Features
--------

Low-level JSON-RPC API
~~~~~~~~~~~~~~~~~~~~~~

For the full reference, see https://api.limesurvey.org/classes/remotecontrol_handle.html.

.. code:: python

   from citric.rpc import Session

   LS_URL = 'http://my-ls-server.com/index.php/admin/remotecontrol'

   with Session(LS_URL, 'iamadmin', 'secret') as session:
       # Get all surveys from user 'iamadmin'
       r = session.rpc('list_surveys', 'iamadmin')

       if r.error is None:
           surveys = r.result
           for s in surveys:
               print(s["surveyls_title"])

               # Get all questions, regardless of group
               r = session.rpc("list_questions", s["sid"])
               questions = r.result
               for q in questions:
                   print(q["title"], q["question"])


Development
-----------

Use pyenv to setup default Python versions for this repo:

.. code:: bash

   pyenv local 3.8.3 3.7.7 3.6.10


Install project dependencies

.. code:: bash

   poetry install


Docker
~~~~~~

You can setup a local instance of LimeSurvey with `Docker Compose <https://docs.docker.com/compose/>`_:

.. code:: bash

   docker-compose up -d

Now you can access LimeSurvey at http://localhost:8001/index.php/admin.

Import an existing survey file and start testing with it:

.. code:: python

   import base64

   from citric.rpc import Session

   LS_URL = "http://localhost:8001/index.php/admin/remotecontrol"
   SURVEY_FILE = "examples/limesurvey_survey_432535.lss"

   with Session(LS_URL, "iamadmin", "secret") as session, open(SURVEY_FILE, "rb") as file:
       # Import survey from file
       contents = file.read()

       string = base64.b64encode(contents).decode()
       r = session.rpc("import_survey", string, "lss")

       if r.error is None:
           survey_id = r.result
           print("New survey:", survey_id)


Testing
~~~~~~~

This project uses nox_ for running tests and linting on different Python versions:

.. code:: bash

   pip install --user --upgrade nox
   nox -r


Run only a linting session

.. code:: bash

   nox -rs lint


pre-commit
~~~~~~~~~~

.. code:: bash

   pip install --user --upgrade pre-commit
   pre-commit install


Releasing an upgrade
~~~~~~~~~~~~~~~~~~~~

Bump the package version

.. code:: bash

   poetry version <version>
   poetry publish


Credits
-------



.. |Documentation Status| image:: https://readthedocs.org/projects/citric/badge/?version=latest
   :target: https://citric.readthedocs.io/en/latest/?badge=latest
.. |Updates| image:: https://pyup.io/repos/github/edgarrmondragon/citric/shield.svg
   :target: https://pyup.io/repos/github/edgarrmondragon/citric/
.. |Python 3| image:: https://pyup.io/repos/github/edgarrmondragon/citric/python-3-shield.svg
   :target: https://pyup.io/repos/github/edgarrmondragon/citric/
   :alt: Python 3
.. |codecov| image:: https://codecov.io/gh/edgarrmondragon/citric/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/edgarrmondragon/citric
.. |Tests| image:: https://github.com/edgarrmondragon/citric/workflows/Tests/badge.svg
   :target: https://github.com/edgarrmondragon/citric/actions?workflow=Tests
.. _nox: https://nox.thea.codes/en/stable/
