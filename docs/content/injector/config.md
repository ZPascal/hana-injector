# Table of Contents

* [load\_config.config](#load_config.config)
  * [LoadConfig](#load_config.config.LoadConfig)
    * [load\_correct\_config\_dict](#load_config.config.LoadConfig.load_correct_config_dict)

<a id="load_config.config"></a>

# load\_config.config

<a id="load_config.config.LoadConfig"></a>

## LoadConfig Objects

```python
class LoadConfig()
```

The class includes all necessary methods to load the configuration from the config file

<a id="load_config.config.LoadConfig.load_correct_config_dict"></a>

#### load\_correct\_config\_dict

```python
@staticmethod
def load_correct_config_dict() -> Dict
```

The method includes a functionality to translate the configuration from a Yaml file and returns the configuration as a dictionary

**Raises**:

- `KeyError` - Missed specifying a necessary configuration environment variable
  

**Returns**:

- `data` _Dict_ - Returns the configuration as dictionary

