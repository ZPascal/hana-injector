# Table of Contents

* [custom\_logger.logger](#custom_logger.logger)
  * [CustomLogger](#custom_logger.logger.CustomLogger)
    * [get\_logger](#custom_logger.logger.CustomLogger.get_logger)
    * [write\_to\_console](#custom_logger.logger.CustomLogger.write_to_console)

<a id="custom_logger.logger"></a>

# custom\_logger.logger

<a id="custom_logger.logger.CustomLogger"></a>

## CustomLogger Objects

```python
class CustomLogger()
```

The class includes all necessary methods to specify a custom logger

<a id="custom_logger.logger.CustomLogger.get_logger"></a>

#### get\_logger

```python
@classmethod
def get_logger(cls, name)
```

The method includes a functionality to get the corresponding logger specified by the name

**Arguments**:

- `name` _any_ - Specify the corresponding logger name
  

**Raises**:

- `HanaInjectorError` - Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
  

**Returns**:

- `logger` _Logger_ - Returns the logger

<a id="custom_logger.logger.CustomLogger.write_to_console"></a>

#### write\_to\_console

```python
@classmethod
def write_to_console(cls, status, message)
```

The method includes a functionality to write the log messages to the console

**Arguments**:

- `status` _any_ - Specify the corresponding status
- `message` _any_ - Specify the corresponding message
  

**Raises**:

- `HanaInjectorError` - Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
- `ValueError` - Missed specifying a necessary value
  

**Returns**:

  None

