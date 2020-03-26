============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

Bug reports
===========

When `reporting a bug <https://github.com/humio/python-humio/issues>`_ please include:

    * Your operating system name and version.
    * Any details about your local setup that might be helpful in troubleshooting.
    * Detailed steps to reproduce the bug.

Feature requests and feedback
=============================

The best way to send feedback is to file an issue at https://github.com/humio/python-humio/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that code contributions are welcome :)

Development
===========

To set up `humiolib` for local development:

1. Fork `python-humio <https://github.com/humio/python-humio>`_
   (look for the "Fork" button).
2. Clone your fork locally::

    git clone git@github.com/humio/python-humio.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

   It migh make sense to install `humiolib` in edit mode as you develop.
   You can do this entering the command ::

    pip install -e . 


4. Commit your changes and push your branch to GitHub::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

5. Submit a pull request through the GitHub website.


Pull Request Guidelines
=======================

If you need some code review or feedback while you're developing the code just make a pull request.

For merging, you should:

1. Include passing tests.
2. Update documentation when there's new API, functionality etc.
3. Add a note to ``CHANGELOG.rst`` about the changes.
4. Add yourself to ``AUTHORS.rst``.


Build Documentation From Source
===============================
If you're contributing to the documentation, you may need to build the docs locally to inspect your changes.

First make sure you have the dependencies installed::

    pip install -r docs/requirements.txt

Then build the html pages using sphinx::

    sphinx-build -b html docs build/docs

You should now find the generated HTML in ``build/docs``