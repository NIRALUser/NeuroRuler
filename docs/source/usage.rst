Usage
=====

.. _installation:

Installation
------------

To use Head Circumference Tool, first clone it:

.. code-block:: console

   (.venv) $ git clone https://github.com/COMP523TeamD/HeadCircumferenceTool.git

Install dependencies
----------------

Install dependencies via pip:

   (.venv) $ pip install -r requirements.txt

.. To retrieve a list of random ingredients,
.. you can use the ``lumache.get_random_ingredients()`` function:

.. .. autofunction:: lumache.get_random_ingredients

.. The ``kind`` parameter should be either ``"meat"``, ``"fish"``,
.. or ``"veggies"``. Otherwise, :py:func:`lumache.get_random_ingredients`
.. will raise an exception.

.. .. autoexception:: lumache.InvalidKindError

.. For example:

.. >>> import lumache
.. >>> lumache.get_random_ingredients()
.. ['shells', 'gorgonzola', 'parsley']
