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

   from citric import Client, Session

   LS_URL = 'http://my-ls-server.com/index.php/admin/remotecontrol'

   with Session(LS_URL, 'iamadmin', 'secret') as session:
       # Create a client from an RPC session
       client = Client(session)

       # Get all surveys from user 'iamadmin'
       surveys = client.list_surveys('iamadmin')

       for s in surveys:
           print(s["surveyls_title"])

           # Get all questions, regardless of group
           questions = client.list_questions(s["sid"])
           for q in questions:
               print(q["title"], q["question"])
