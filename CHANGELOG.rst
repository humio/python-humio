
Changelog
=========

0.2.0 (2020-03-30)
******************
Initial real release to PyPI

Added:

    * Tests, mocking out API calls with vcr.py 
    * Custom error handling to completly wrap url library used
    * QueryJob class

Changed:

    * Whole API interface has been updated
    * Updated Sphinx documentation

Removed:

    * A few configuration files left over from earlier versions


0.2.2 (2020-05-19)
******************
Bugfixing to ensure that static queryjobs can be polled for all their results

Added:

    * Static queryjobs can now be queried for more than one segment
    

Changed:

    * Upon polling from a QueryJob it will now stall until it can poll data from Humio, ensuring that an empty result is not returned prematurely.

Removed:

    * The poll_until_done method has been removed from live query jobs, as this does not make conceptual sense to do, in the same manner as a static query job.

0.2.3 (2021-08-13)
******************
Smaller bugfixes
Changed:

    * Fix urls in docstrings in HumioClient.py
    * Propagate kwargs to poll functions in QueryJob.py