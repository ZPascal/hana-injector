# Hana Injector

MQTT stream to SAP Hana database converter and forwarder API.

The following application was created by a project with the purpose to connect MQTT parts with the SAP HANA DB. The goal was to implement an application that is capable of transforming incoming MQTT topics to a SQL format that is compliant with the Hana DB, as the original data was streamed with MQTT, whereas the HANA database was only able to receive data sent in Hana SQL format.

## Basic information about the application and key features
The Hana Injector is based on a Python Flask microservice architecture. Therefore, one of the key features of the application is the low consumption of resources, as the framework allows for the efficient distribution and usage of resources in general.

Furthermore, the architecture includes multiple packages, such as the Python [MQTT Paho client](https://pypi.org/project/paho-mqtt/#description) and the [PyHDB](https://pypi.org/project/pyhdb/#description) library.

The features of this application are the conversion process in SQL, the element identification and the insertion into the HANA DB.

## Architecture and functional principles of the Hana Injector
### Architecture
The service based on a microservice architecture and the Python Flask framework. The application include a Prometheus metric endpoint and a code generator to produce the corresponding functions and transformation code to forward/ modify the incoming MQTT stream. 
After the transformation process, the core functionality of the tool is the injection of the modified and transformed MQTT stream and in the meantime already a Hana database query to the attached and configured SAP Hana database.

### Process flow
The transformation process identify the elements and puts these variables in the SQL statement. For this process, the statements were defined before the application starts.  As soon as the transforming is done, the string is transformed to the HANA DB SQL format and can then be directly inserted to the HANA database.

## Installation and configuration
### Installation
1. Please clone the injector code inside your local environment and install all required dependencies via `pip3 install -r requirements.txt` for the application.
2. Modify the execution rights of the `app.py` file e.g. on Linux `chmod +x app.py`

### Configuration
Before starting the application, you must ensure that both the MQTT server and the corresponding HANA DB server are running.

In case these preconditions are not set, the application will throw multiple errors and will eventually crash.

You set up all related configuration parameters like the Hana and MQTT credentials and channels inside the configuration YAML file. You can check out the predefined example configuration inside the next paragraph. To specify the used configuration file it's necessary to set up the env variable `HANA_INJECTOR_CONFIG_FILE_PATH` and to store the path of the configuration file inside the variable e.g. `HANA_INJECTOR_CONFIG_FILE_PATH=config/config.yml`.
For the startup of the application it's required to call the `app.py` script e.g. `python3 app.py`.

#### Configuration Yaml

```yaml
hana_injector:
  secret_key: "test"
  log_mode: "debug"
  template: "injector/templates"
  host: "localhost"
  port: 8080
  threads: 4

mqtt:
  hostname: "localhost"
  port: 3555
  username: "3555"
  password: "3555"
  subscribed_topics:
    - name: "Test1"
      qos: 0
    - name: "Test2"
      qos: 0

hana_database:
  hostname: "Test"
  port: 123
  username: "test"
  password: "Test"

generator:
  - method_name: "Service1"
    mqtt_topic: "Service11"
    mqtt_payload:
      - OrderID: "str"
      - OrderDate: "generateDatetime"
      - Color: "sep:ListDict(Name, Amount)|OrderID, OrderDate"
      - Color2: "sep:ListDict(Name, Amount)|OrderID, OrderDate"
      - CustomerName: "str"
    hana_sql_query:
      - "Test1"
    hana_sql_query_sep:
      - "Test1_sep"
      - "Test2_sep"

  - method_name: "Service2"
    mqtt_topic: "Service21"
    mqtt_payload:
      - OrderID: "str"
      - OrderDate: "generateDate"
      - CustomerName: "str"
      - Color: "List"
    hana_sql_query:
      - "Test2"
      - "Test22"

  - method_name: "Service3"
    mqtt_topic: "Service31"
    mqtt_payload:
      - OrderID: "str"
      - DeviceID: "str"
      - OrderDate: "str"
      - StatusCode: "str"
    hana_sql_query:
      - "Test3"
```

#### Supported mapping types and function
- **int** | Mapping value for a classical integer like `1`
- **double**  | Mapping value for a classical double like `1.1`
- **str**  | Mapping value for a classical string like `test`
- **List**  | Mapping value for a classical list of values like `["test", "test1"]`
- **ListDict** | Mapping value for a list of dictionaries like `[{"test": "test1"}, {"test1": "test2"}]`
- **sep:ListDict** | Mapping value the functionality to separate values from MQTT stream and accumulate existing values from configuration/ stream and forward both together to the HANA database via a separate methode and query `sep:ListDict(Name, Amount)|OrderID, OrderDate`. For this datatype it's also necessary to specify the `hana_sql_query_sep` configuration option and forward the queries in the right order to the generator functionality.
- **Dict** | Mapping value for a dictionary like `{"test": "test1"}`
- **generateDate** | Mapping value for the functionality to generate a date inside the following format `%Y-%m-%d`
- **generateDatetime** | Mapping value for the functionality to generate a date time inside the following format `%Y-%m-%dT%H:%M:%SZ`

### Api Endpoints
#### Health

The corresponding app includes a health endpoint to check the status of the application. You can call the `/health` page to get the corresponding status of the app.

#### Metrics

The corresponding app includes a Prometheus metric endpoint to get the metrics of the application. You can call the `/metrics` page to get the corresponding metrics of the app.

#### Swagger

The corresponding app includes a documentation endpoint to check the documentation pages of the API. You can call the `/api/docs` page to get the corresponding documentation pages.

## Contribution

If you would like to contribute, have an improvement request, or want to make a change inside the code, please open a pull request and write unit tests.

## Support

If you need support, or you encounter a bug, please don't hesitate to open an issue.

## Donations

If you would like to support my work, I ask you to take an unusual action inside the open source community. Donate the money to a non-profit organization like Doctors Without Borders or the Children's Cancer Aid. I will continue to build tools because I like it and it is my passion to develop and share applications.

## License

This product is available under the Apache 2.0 [license](LICENSE).