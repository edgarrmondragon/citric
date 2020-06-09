Citric
======

.. toctree::
   :hidden:
   :maxdepth: 1

   license
   reference

Installation
------------

Using ``pip``:

.. code-block:: console

   $ pip install git+https://github.com/edgarrmondragon/citric

Usage
-----

.. code-block:: python

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
