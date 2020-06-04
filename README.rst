Limette
=======

|PyPI| |Python versions| |Travis builds| |Documentation Status|
|Updates| |Python 3| |codecov|

A client to the LimeSurvey Remote Control API 2, written in modern
Python.

Features
--------

Low-level JSON-RPC API
~~~~~~~~~~~~~~~~~~~~~~

For the full reference, see https://api.limesurvey.org/classes/remotecontrol_handle.html.

.. code:: python

   from limette.rpc import Session

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


Testing
-------

This project uses [`Nox`][nox]__
for runinng tests on different Python versions:

.. code:: bash

   pip install --user --upgrade nox
   nox -r

Credits
-------



.. |PyPI| image:: https://img.shields.io/pypi/v/limette.svg
   :target: https://pypi.python.org/pypi/limette
.. |Python versions| image:: https://img.shields.io/pypi/pyversions/limette.svg?longCache=True
   :target: https://pypi.python.org/pypi/limette
.. |Travis builds| image:: https://api.travis-ci.com/edgarrmondragon/limette.svg?branch=master
   :target: https://travis-ci.com/edgarrmondragon/limette
.. |Documentation Status| image:: https://readthedocs.org/projects/limette/badge/?version=latest
   :target: https://limette.readthedocs.io/en/latest/?badge=latest
.. |Updates| image:: https://pyup.io/repos/github/edgarrmondragon/limette/shield.svg
   :target: https://pyup.io/repos/github/edgarrmondragon/limette/
.. |Python 3| image:: https://pyup.io/repos/github/edgarrmondragon/limette/python-3-shield.svg
   :target: https://pyup.io/repos/github/edgarrmondragon/limette/
   :alt: Python 3
.. |codecov| image:: https://codecov.io/gh/edgarrmondragon/limette/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/edgarrmondragon/limette
.. |nox| target:: https://nox.thea.codes/en/stable/
