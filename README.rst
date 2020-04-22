======================
Humiolib
======================
 
.. start-badges
 
|docs| |version| |license|
 
 
.. |docs| image:: https://readthedocs.org/projects/python-humio/badge/?style=flat
   :target: https://readthedocs.org/projects/python-humio
   :alt: Documentation Status
 
.. |version| image:: https://img.shields.io/pypi/v/humiolib.svg
   :target: https://pypi.org/project/humiolib
   :alt: PyPI Package latest release
 
.. |license| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
   :alt: Apache 2.0 License
 
.. end-badges
 
The `humiolib` library is a wrapper for Humio's web API, supporting easy interaction with Humio directly from Python.
Full documentation for this repository can be found at https://python-humio.readthedocs.io/en/latest/readme.html.
 
Vision
======
The vision for `humiolib` is to create an opinionated wrapper around the Humio web API, supporting most if not all exposed endpoints.
The project does not simply expose web endpoints as Python methods, but attempts to improve upon the usability experience of the API.
In addition the project seeks to add non-intrusive quality of life features, so that users can focus on their primary goals during development.
 
Governance
==========
This project is maintained by employees at Humio ApS.
As a general rule, only employees at Humio can become maintainers and have commit privileges to this repository.
Therefore, if you want to contribute to the project, which we very much encourage, you must first fork the repository.
Maintainers will have the final say on accepting or rejecting pull requests.
As a rule of thumb, pull requests will be accepted if:
 
   * The contribution fits with the project's vision
   * All automated tests have passed
   * The contribution is of a quality comparable to the rest of the project
 
The maintainers will attempt to react to issues and pull requests quickly, but their ability to do so can vary.
If you haven't heard back from a maintainer within 7 days of creating an issue or making a pull request, please feel free to ping them on the relevant post.
 
The active maintainers involved with this project include:
  
   * `Alexander Brandborg <https://github.com/AlexanderBrandborg>`_
 
Installation
============
The `humiolib` library has been published on PyPI, so you can use `pip` to install it:
::
  
   pip install humiolib
 
 
Usage
========
The examples below seek to get you going with `humiolib`.
For further documentation have a look at the code itself.
 
HumioClient
***********
The HumioClient class is used for general interaction with Humio.
It is mainly used for performing queries, as well as managing different aspects of your Humio instance.
 
.. code-block:: python
 
  from humiolib.HumioClient import HumioClient
 
  # Creating the client
  client = HumioClient(
       base_url= "https://cloud.humio.com",
       repository= "sandbox",
       user_token="*****")
 
  # Using a streaming query 
  webStream = client.streaming_query("Login Attempt Failed", is_live=True)
  for event in webStream:
      print(event)
 
  # Using a queryjob 
  queryjob = client.create_queryjob("Login Attempt Failed", is_live=True)
  poll_result = queryjob.poll()
  for event in poll_result.events:
      print(event)

  # With a static queryjob you can poll it iterativly until it has been exhausted
  queryjob = client.create_queryjob("Login Attempt Failed", is_live=False)
  for poll_result in queryjob.poll_until_done():
      print(poll_result.metadata)
      for event in poll_result.events:
              print(event)
 
HumioIngestClient
*****************
The HumioIngestClient class is used for ingesting data into Humio.
While the HumioClient can also be used for ingesting data, this is mainly meant for debugging.
 
.. code-block:: python

  from humiolib.HumioClient import HumioIngestClient
 
 # Creating the client
 client = HumioIngestClient(
    base_url= "https://cloud.humio.com",
    ingest_token="*****")
 
 # Ingesting Unstructured Data
 messages = [
       "192.168.1.21 - user1 [02/Nov/2017:13:48:26 +0000] \"POST /humio/api/v1/ingest/elastic-bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.015 664 0.015",
       "192.168.1..21 - user2 [02/Nov/2017:13:49:09 +0000] \"POST /humio/api/v1/ingest/elastic-bulk HTTP/1.1\" 200 0 \"-\" \"useragent\" 0.013 565 0.013"
   ]
 
 client.ingest_messages(messages) 
 
 # Ingesting Structured Data
 structured_data = [
       {
           "tags": {"host": "server1" },
           "events": [
               {
                   "timestamp": "2020-03-23T00:00:00+00:00",
                   "attributes": {"key1": "value1", "key2": "value2"}      
               }
           ]
       }
   ]
 
 client.ingest_json_data(structured_data)
 