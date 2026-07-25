---


# Service Monitoring and Automation Assignment


This project contains three independent tasks:


1.Service monitoring with Python, Flask, and Elasticsearch
2.Infrastructure automation with Ansible
3.CSV data processing with Python


The project was developed and tested in a Linux/WSL environment.


---


## Project Structure

```text		
rbcapp1/
│
├── README.md
├── requirements.txt
│
├── test1/
│   ├── monitor_services.py
│   ├── rest_service.py
│   └── service_status/
│
├── test2/
│   ├── inventory
│   ├── assignment.yml
│   ├── verify_install.yml
│   ├── check_disk.yml
│   └── check_status.yml
│
└── test3/
    ├── filter_sales.py
    ├── Assignment python.csv
    └── filtered_sales.csv


---

## Prerequisites


The following software is required:


-Python 3
-Python virtual environment
-Flask
-Elasticsearch
-Ansible
-Docker, As Elasticsearch is run as a container

---

## Initial Setup


From the project root:


```bash
cd ~/rbcapp1


### Create and activate the virtual environment:


python3 -m venv venv
source venv/bin/activate


### Install the Python dependencies:


pip install -r requirements.txt



---


## Test 1: Service Monitoring


### Overview


#### The service monitoring workflow is:


```text
monitor_services.py
        ↓
Check configured services
        ↓
Create JSON status files
        ↓
Send service status to Flask API
        ↓
Flask stores the status in Elasticsearch




#### The monitored services are:


-httpd
-rabbitmq-server
-postgresql



#### Start Elasticsearch


As Elasticsearch is running in Docker:

```bash
docker ps


Output:



CONTAINER ID   IMAGE                                                 COMMAND                  CREATED       STATUS       PORTS                                         NAMES
f324b188682e   docker.elastic.co/elasticsearch/elasticsearch:9.0.0   "/bin/tini -- /usr/l…"   6 hours ago   Up 6 hours   0.0.0.0:9200->9200/tcp, [::]:9200->9200/tcp   elasticsearch



#### Verifying Elasticsearch is available or not:


```bash
curl http://localhost:9200


Output:


(venv) srika@Srikanth:~/rbcapp1$ curl http://localhost:9200
{
  "name" : "f324b188682e",
  "cluster_name" : "docker-cluster",
  "cluster_uuid" : "tTYjJ4BAQ5i3T7W-0QPJsw",
  "version" : {
    "number" : "9.0.0",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "112859b85d50de2a7e63f73c8fc70b99eea24291",
    "build_date" : "2025-04-08T15:13:46.049795831Z",
    "build_snapshot" : false,
    "lucene_version" : "10.1.0",
    "minimum_wire_compatibility_version" : "8.18.0",
    "minimum_index_compatibility_version" : "8.0.0"
  },
  "tagline" : "You Know, for Search"
}



#### Start the Flask API



From the project root:


```bash
cd ~/rbcapp1
source venv/bin/activate
python test1/rest_service.py


#### Run the service monitor


In another terminal:


```bash
cd ~/rbcapp1
source venv/bin/activate
python test1/monitor_services.py

The script checks the configured services, creates JSON status files, and uploads the status to the Flask API.


Output:


httpd: UP
Status file created: service_status/httpd-status-20260725_000304.json
Uploaded successfully: {'message': 'Service status stored successfully', 'service': 'httpd'}
rabbitmq-server: UP
Status file created: service_status/rabbitmq-server-status-20260725_000305.json
Uploaded successfully: {'message': 'Service status stored successfully', 'service': 'rabbitmq-server'}
postgresql: UP
Status file created: service_status/postgresql-status-20260725_000306.json
Uploaded successfully: {'message': 'Service status stored successfully', 'service': 'postgresql'}



#### Verify the data in Elasticsearch


```bash
curl "http://localhost:9200/service-status/_search?pretty"



Output:



{
  "took" : 42,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 3,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "service-status",
        "_id" : "httpd",
        "_score" : 1.0,
        "_source" : {
          "service_name" : "httpd",
          "service_status" : "UP",
          "host_name" : "Srikanth",
          "checked_at" : "2026-07-25T05:03:04.219105+00:00"
        }
      },
      {
        "_index" : "service-status",
        "_id" : "rabbitmq-server",
        "_score" : 1.0,
        "_source" : {
          "service_name" : "rabbitmq-server",
          "service_status" : "UP",
          "host_name" : "Srikanth",
          "checked_at" : "2026-07-25T05:03:05.055839+00:00"
        }
      },
      {
        "_index" : "service-status",
        "_id" : "postgresql",
        "_score" : 1.0,
        "_source" : {
          "service_name" : "postgresql",
          "service_status" : "UP",
          "host_name" : "Srikanth",
          "checked_at" : "2026-07-25T05:03:06.066579+00:00"
        }
      }
    ]
  }
}




#### Flask health endpoint


The application health endpoint can be checked with:


```bash
curl http://localhost:5000/healthcheck



Output:


{"application":"rbcapp1","status":"UP"}


---


## Test 2: Ansible Automation



#### Inventory


The inventory file is located at:


```bash
test2/inventory



#### The current setup uses local connections for testing:


```bash
[httpd_servers]
host1 ansible_connection=local

[rabbitmq_servers]
host2 ansible_connection=local

[postgresql_servers]
host3 ansible_connection=local


The host names represent separate service groups in the assignment inventory.




##### Verify Ansible connectivity



```bash
cd ~/rbcapp1/test2
ansible all -i inventory -m ping



Output:


[WARNING]: Host 'host2' is using the discovered Python interpreter at '/home/srika/rbcapp1/venv/bin/python3.14', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.20/reference_appendices/interpreter_discovery.html for more information.
host2 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/home/srika/rbcapp1/venv/bin/python3.14"
    },
    "changed": false,
    "ping": "pong"
}
[WARNING]: Host 'host3' is using the discovered Python interpreter at '/home/srika/rbcapp1/venv/bin/python3.14', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.20/reference_appendices/interpreter_discovery.html for more information.
host3 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/home/srika/rbcapp1/venv/bin/python3.14"
    },
    "changed": false,
    "ping": "pong"
}
[WARNING]: Host 'host1' is using the discovered Python interpreter at '/home/srika/rbcapp1/venv/bin/python3.14', but future installation of another Python interpreter could cause a different interpreter to be discovered. See https://docs.ansible.com/ansible-core/2.20/reference_appendices/interpreter_discovery.html for more information.
host1 | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/home/srika/rbcapp1/venv/bin/python3.14"
    },
    "changed": false,
    "ping": "pong"
}
(venv) srika@Srikanth:~/rbcapp1/test2$ nano inventory
(venv) srika@Srikanth:~/rbcapp1/test2$ rm inventory
(venv) srika@Srikanth:~/rbcapp1/test2$ nano inventory
(venv) srika@Srikanth:~/rbcapp1/test2$ ansible all -i inventory -m ping
host1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
host3 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
host2 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}




#### Verify service status



```bash
ansible-playbook \
  -i inventory \
  assignment.yml \
  -e operation=verify_install



This checks the status of:


httpd
RabbitMQ
PostgreSQL



Output:


PLAY [Run selected operation] ******************************************************************************************

TASK [Gathering Facts] *************************************************************************************************
ok: [host1]
ok: [host3]
ok: [host2]

TASK [Verify and install required services] ****************************************************************************
included: /home/srika/rbcapp1/test2/verify_install.yml for host1, host2, host3

TASK [Check whether httpd is installed] ********************************************************************************
skipping: [host2]
skipping: [host3]
ok: [host1]

TASK [Display httpd status] ********************************************************************************************
skipping: [host2]
skipping: [host3]
ok: [host1] => {
    "msg": "httpd status: active"
}

TASK [Check whether RabbitMQ is installed] *****************************************************************************
skipping: [host1]
skipping: [host3]
ok: [host2]

TASK [Display RabbitMQ status] *****************************************************************************************
skipping: [host1]
ok: [host2] => {
    "msg": "RabbitMQ status: active"
}
skipping: [host3]

TASK [Check whether PostgreSQL is installed] ***************************************************************************
skipping: [host1]
skipping: [host2]
ok: [host3]

TASK [Display PostgreSQL status] ***************************************************************************************
skipping: [host1]
skipping: [host2]
ok: [host3] => {
    "msg": "PostgreSQL status: active"
}

TASK [Check disk usage] ************************************************************************************************
skipping: [host1]
skipping: [host2]
skipping: [host3]

TASK [Check application status] ****************************************************************************************
skipping: [host1]
skipping: [host2]
skipping: [host3]

PLAY RECAP *************************************************************************************************************
host1                      : ok=4    changed=0    unreachable=0    failed=0    skipped=6    rescued=0    ignored=0
host2                      : ok=4    changed=0    unreachable=0    failed=0    skipped=6    rescued=0    ignored=0
host3                      : ok=4    changed=0    unreachable=0    failed=0    skipped=6    rescued=0    ignored=0




#### Check disk usage



```bash
ansible-playbook \
  -i inventory \
  assignment.yml \
  -e operation=check-disk



Output:



PLAY [Run selected operation] ******************************************************************************************

TASK [Gathering Facts] *************************************************************************************************
ok: [host1]
ok: [host3]
ok: [host2]

TASK [Verify and install required services] ****************************************************************************
skipping: [host1]
skipping: [host2]
skipping: [host3]

TASK [Check disk usage] ************************************************************************************************
included: /home/srika/rbcapp1/test2/check_disk.yml for host2, host1, host3

TASK [Check root filesystem usage] *************************************************************************************
ok: [host1]
ok: [host2]
ok: [host3]

TASK [Display disk usage] **********************************************************************************************
ok: [host1] => {
    "msg": "host1 is using 1% of disk space"
}
ok: [host2] => {
    "msg": "host2 is using 1% of disk space"
}
ok: [host3] => {
    "msg": "host3 is using 1% of disk space"
}

TASK [Display disk usage warning] **************************************************************************************
skipping: [host2]
skipping: [host1]
skipping: [host3]

TASK [Send disk usage alert email] *************************************************************************************
skipping: [host1]
skipping: [host2]
skipping: [host3]

TASK [Check application status] ****************************************************************************************
skipping: [host1]
skipping: [host2]
skipping: [host3]

PLAY RECAP *************************************************************************************************************
host1                      : ok=4    changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0
host2                      : ok=4    changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0
host3                      : ok=4    changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0

The playbook reports root filesystem usage.
If usage exceeds the configured threshold, the playbook displays a warning and can send an email alert through the configured SMTP server.






### SMTP parameters can be passed at runtime:



```bash
ansible-playbook \
  -i inventory \
  assignment.yml \
  -e operation=check-disk \
  -e smtp_host=smtp.gmail.com \
  -e smtp_port=587 \
  -e smtp_username=xyz.gmail.com \
  -e smtp_password=PASSWORD \
  -e alert_email=Recipient_email_address




Credentials should not be committed to the repository.




#### Check application health



```bash
ansible-playbook \
  -i inventory \
  assignment.yml \
  -e operation=check-status



This queries the application health endpoint and displays the returned status.



Output:


PLAY [Run selected operation] ******************************************************************************************

TASK [Gathering Facts] *************************************************************************************************
ok: [host1]
ok: [host3]
ok: [host2]

TASK [Verify and install required services] ****************************************************************************
skipping: [host1]
skipping: [host2]
skipping: [host3]

TASK [Check disk usage] ************************************************************************************************
skipping: [host1]
skipping: [host2]
skipping: [host3]

TASK [Check application status] ****************************************************************************************
included: /home/srika/rbcapp1/test2/check_status.yml for host1, host2, host3

TASK [Query application health endpoint] *******************************************************************************
ok: [host3]
ok: [host1]
ok: [host2]

TASK [Display application health] **************************************************************************************
ok: [host1] => {
    "application_health.json": {
        "application": "rbcapp1",
        "status": "UP"
    }
}
ok: [host2] => {
    "application_health.json": {
        "application": "rbcapp1",
        "status": "UP"
    }
}
ok: [host3] => {
    "application_health.json": {
        "application": "rbcapp1",
        "status": "UP"
    }
}

PLAY RECAP *************************************************************************************************************
host1                      : ok=4    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
host2                      : ok=4    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0
host3                      : ok=4    changed=0    unreachable=0    failed=0    skipped=2    rescued=0    ignored=0


---


## Test 3: CSV Processing



### Overview



The Python script processes the provided real estate sales CSV file.


#### Input file:



test3/Assignment python.csv



The script calculates:


-Price per square foot = price / square footage
-It then calculates the average price per square foot across valid records.
-Only properties with a price per square foot below the average are written to the output file.


Run the script



```bash
cd ~/rbcapp1/test3
python filter_sales.py



The script creates:


filtered_sales.csv



Output:


Average price per square foot: $145.67
Properties in input file: 985
Properties written to output: 470
Output file created: filtered_sales.csv


Check the filtered_sales.csv file to validate the records:

head -10 filtered_sales.csv


street,city,zip,state,beds,baths,sq__ft,type,sale_date,price,latitude,longitude
3526 HIGH ST,SACRAMENTO,95838,CA,2,1,836,Residential,Wed May 21 00:00:00 EDT 2008,59222,38.631913,-121.434879
51 OMAHA CT,SACRAMENTO,95823,CA,3,1,1167,Residential,Wed May 21 00:00:00 EDT 2008,68212,38.478902,-121.431028
2796 BRANCH ST,SACRAMENTO,95815,CA,2,1,796,Residential,Wed May 21 00:00:00 EDT 2008,68880,38.618305,-121.443839
2805 JANETTE WAY,SACRAMENTO,95815,CA,2,1,852,Residential,Wed May 21 00:00:00 EDT 2008,69307,38.616835,-121.439146
6001 MCMAHON DR,SACRAMENTO,95824,CA,2,1,797,Residential,Wed May 21 00:00:00 EDT 2008,81900,38.51947,-121.435768
5828 PEPPERMILL CT,SACRAMENTO,95841,CA,3,1,1122,Condo,Wed May 21 00:00:00 EDT 2008,89921,38.662595,-121.327813
6048 OGDEN NASH WAY,SACRAMENTO,95842,CA,3,2,1104,Residential,Wed May 21 00:00:00 EDT 2008,90895,38.681659,-121.351705
2561 19TH AVE,SACRAMENTO,95820,CA,3,1,1177,Residential,Wed May 21 00:00:00 EDT 2008,91002,38.535092,-121.481367
11150 TRINITY RIVER DR Unit 114,RANCHO CORDOVA,95670,CA,2,2,941,Condo,Wed May 21 00:00:00 EDT 2008,94905,38.621188,-121.270555



The output CSV keeps the original columns and contains only the filtered property records.


---

## Testing Summary



The three tasks can be tested independently.



#### Test 1


```bash
python test1/monitor_services.py


Verify:


curl "http://localhost:9200/service-status/_search?pretty"



#### Test 2


```bash
cd test2



ansible-playbook -i inventory assignment.yml -e operation=verify_install



ansible-playbook -i inventory assignment.yml -e operation=check-disk



ansible-playbook -i inventory assignment.yml -e operation=check-status




#### Test 3



```bash
cd test3


python filter_sales.py


---

## Design Notes



The solution is intentionally divided into separate components:



-Python handles service monitoring and CSV processing.
-Flask provides the REST API layer.
-Elasticsearch provides persistent storage for service status data.
-Ansible handles service verification, disk monitoring, alerting, and application health checks.
-The service monitor and Ansible automation are independent. 
-The Python monitor continuously checks and records service health, while Ansible provides operational checks and automation commands.


---

## Security Notes



Sensitive credentials should not be stored directly in the repository.


In particular:


-Do not commit SMTP passwords.
-Do not commit application secrets.
-Use environment variables, Ansible Vault, or another secure secrets mechanism for production credentials.
-The SMTP values used for testing should be supplied at runtime or stored securely outside the source code.


---

## Result


The completed assignment demonstrates:


-REST API development with Flask
-Elasticsearch integration
-Service monitoring
-JSON status generation
-Ansible inventory and playbooks
-Service health verification
-Disk usage monitoring
-Email alert configuration
-Python CSV processing
-Data filtering and output generation

