============
Contributing
============
Contributions are welcome, and they are greatly appreciated! 
Every little bit helps, and credit will always be given.

Ways To Contribute
==================
There are many different ways, in which you may contribute to this project, including:

   * Opening issues by using the `issue tracker <https://github.com/humio/python-humio/issues>`_, using the correct issue template for your submission.
   * Commenting and expanding on open issues.
   * Propose fixes to open issues via a pull request.

We suggest that you create an issue on GitHub before starting to work on a pull request, as this gives us a better overview, and allows us to start a conversation about the issue.
We also encourage you to separate unrelated contributions into different pull requests. This makes it easier for us to understand your individual contributions and faster at reviewing them.

Setting Up `humiolib` For Local Development
===========================================

1. Fork `python-humio <https://github.com/humio/python-humio>`_
   (look for the "Fork" button).
2. Clone your fork locally::

    git clone git@github.com/humio/python-humio.git

3. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

4. Install `humiolib` from your local repository::

    pip install -e . 
   
   Now you can import `humiolib` into your Python code, and you can make changes to the project locally.

5. As your work progresses, regularly commit to and push your branch to your own fork on GitHub::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature


Running Tests locally
=====================
Testing is accomplished using the  `pytest <https://github.com/pytest-dev/pytest>`_ library. This should automatically be installed on your machine, when you install the `humiolib` package.
To run tests simply execute the following command in the `tests` folder:

.. code-block:: 

   pytest

Humio API calls made during tests have been recorded using `vcr.py <https://github.com/kevin1024/vcrpy>`_ and can be found in the `tests/cassettes` folder.
These will be *played back* when tests are run, so you do not need to set up a Humio instance to perform the tests.
Please do not re-record cassettes unless you're really familiar with vcr.py.


Building Documentation From Source
===================================
If you're contributing to the documentation, you need to build the docs locally to inspect your changes.

To do this, first make sure you have the documentation dependencies installed::

    pip install -r docs/requirements.txt

Once dependencies have been installed build the HTML pages using sphinx::

    sphinx-build -b html docs build/docs

You should now find the generated HTML in ``build/docs``.


Making A Pull Request
=====================
When you have made your changes locally, or you want feedback on a work in progress, you're almost ready to make a pull request.

If you have changed part of the codebase in your pull request, please go through this checklist:

    1. Write new test cases if the old ones do not cover your new code.
    2. Update documentation if necessary.
    3. Add yourself to ``AUTHORS.rst``.

If you have only changed the documentation you only need to add yourself to ``AUTHORS.rst``.

When you've been through the applicable checklist, push your final changes to your development branch on GitHub.
Afterwards, use the GitHub interface to create a pull request to the official repository.

Terms of Service For Contributors
=================================
For all contributions to this repository (software, bug fixes, configuration changes, documentation, or any other materials), we emphasize that this happens under GitHubs general Terms of Service and the license of this repository.

Contributing as an individual
*****************************
If you are contributing as an individual you must make sure to adhere to:

The `GitHub Terms of Service <https://help.github.com/en/github/site-policy/github-terms-of-service>`_ **Section D. User-Generated Content,** `Subsection: 6. Contributions Under Repository License <https://help.github.com/en/github/site-policy/github-terms-of-service#6-contributions-under-repository-license>`_ :

*Whenever you make a contribution to a repository containing notice of a license, you license your contribution under the same terms, and you agree that you have the right to license your contribution under those terms. If you have a separate agreement to license your contributions under different terms, such as a contributor license agreement, that agreement will supersede.
Isn't this just how it works already? Yep. This is widely accepted as the norm in the open-source community; it's commonly referred to by the shorthand "inbound=outbound". We're just making it explicit."*

Contributing on behalf of a Corporation
***************************************
If you are contributing on behalf of a Corporation you must make sure to adhere to:

The `GitHub Corporate Terms of Service <https://help.github.com/en/github/site-policy/github-corporate-terms-of-service>`_ **Section D. Content Responsibility; Ownership; License Rights,** `subsection 5. Contributions Under Repository License <https://help.github.com/en/github/site-policy/github-corporate-terms-of-service#5-contributions-under-repository-license>`_:

*Whenever Customer makes a contribution to a repository containing notice of a license, it licenses such contributions under the same terms and agrees that it has the right to license such contributions under those terms. If Customer has a separate agreement to license its contributions under different terms, such as a contributor license agreement, that agreement will supersede*