Citric
======

.. toctree::
   :maxdepth: 4

   license

.. toctree::
   :maxdepth: 1
   :caption: References

   API <_api/index>

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
      r = session.list_surveys('iamadmin')

      if r.error is None:
         surveys = r.result
         for s in surveys:
            print(s["surveyls_title"])

            # Get all questions, regardless of group
            r = session.list_questions(s["sid"])
            questions = r.result
            for q in questions:
               print(q["title"], q["question"])
