Limette
=======

|PyPI| |Python versions| |Travis builds| |Documentation Status|
|Updates| |codecov|

A client to the LimeSurvey Remote Control API 2, written in modern
Python.

Features
--------

Low-level JSON-RPC API
~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   from limette.rpc import Session

   with Session('http://my-ls-server.com', 'iamadmin', 'secret') as session:
       response = session.rpc('list_surveys', 'iamadmin')
       surveys = response.result

Testing
-------

This project uses `tox <https://tox.readthedocs.io/en/latest/>`__
for runinng tests on different Python versions:

.. code:: bash

   tox

Credits
-------

This package was created with
`Cookiecutter <https://github.com/audreyr/cookiecutter>`__ and the
`audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`__
project template.

.. |PyPI| image:: https://img.shields.io/pypi/v/limette.svg
   :target: https://pypi.python.org/pypi/limette
.. |Python versions| image:: https://img.shields.io/pypi/pyversions/limette.svg?longCache=True
   :target: https://pypi.python.org/pypi/limette
.. |Travis builds| image:: https://api.travis-ci.com/mrfunnyshoes/limette.svg?branch=master
   :target: https://travis-ci.com/mrfunnyshoes/limette
.. |Documentation Status| image:: https://readthedocs.org/projects/limette/badge/?version=latest
   :target: https://limette.readthedocs.io/en/latest/?badge=latest
.. |Updates| image:: https://pyup.io/repos/github/mrfunnyshoes/limette/shield.svg
   :target: https://pyup.io/repos/github/mrfunnyshoes/limette/
.. |codecov| image:: https://codecov.io/gh/mrfunnyshoes/limette/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/mrfunnyshoes/limette
