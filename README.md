# erp-e2e-cypress-tests

Pre reqs:

- ``Clone this repository``

- ``Install Cypress by running following command from Cypress folder.``

    - ``npm install``

# erp-e2e-tests

Pre reqs:
 Install Firefox and Firefox driver

# Steps to get started:
- ``Clone this repository``
- ``For Docker user only``:
    - ``docker build -t <image_name> .`` - Will take a while building 
    - ``docker run <image_name>`` - Will run tests and display results 
    - ``docker exec -it <image_name OR image ID> /bin/bash`` - To work inside Docker container  
- Set environment variables for each test (login required) # Ask for staging user/password 
- To run all the tests: nosetests -v (first make sure to set env variables)
# OR
- Right click on each test and use 'Run...' option 
