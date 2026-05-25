import os
import pathlib
import re

from custom_logger.logger import HanaInjectorError
from jinja2 import Environment, FileSystemLoader
from load_config.config import LoadConfig


class Generator:
    """The class includes all necessary methods to generate SQL, MQTT and converter code"""

    _SEC_LIST_DICT: str = "sep:listDict"
    _CHECK_ERROR: str = "Please, check the error"
    _SUPPORTED_TYPES: list = [
        "int",
        "double",
        "str",
        "list",
        "listDict",
        _SEC_LIST_DICT,
        "Dict",
        "generateDate",
        "generateDatetime",
    ]
    _generator_list: list = LoadConfig.load_correct_config_dict()["generator"]
    _file_loader = FileSystemLoader(LoadConfig.load_correct_config_dict()["hana_injector"]["template"])
    _env = Environment(loader=_file_loader, trim_blocks=True, lstrip_blocks=True, autoescape=False)
    _src_path = os.path.dirname(str(pathlib.Path(__file__).parent.absolute()))

    def __init__(self):
        self._generate_converter()

    @classmethod
    def _generate_converter(cls):
        """The method includes a functionality to start the code generator
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        """
        if cls._generator_list is not None and len(cls._generator_list) == 0:
            raise HanaInjectorError("Please, specify the generator rules") from Exception
        cls._generate_mqtt_code()
        cls._reset_converter_code()
        cls._generate_converter_code()
        cls._format_converter_code()
        cls._reset_sql_code()
        cls._generate_sql_code()

    @classmethod
    def _generate_mqtt_code(cls):
        """The method includes a functionality to generate the MQTT code
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        """
        try:
            template = cls._env.get_template("mqtt.template")
        except Exception as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e
        mqtt_transformation_process_code: list = []
        for i in range(0, len(cls._generator_list)):
            mqtt_transformation_process_code.append(
                f'cls._client.message_callback_add("{cls._generator_list[i]["mqtt_topic"]}", '
                f"converter.{str(cls._generator_list[i]['method_name']).lower()})"
            )
        try:
            output = template.render(mqtt_transformation_process_code=mqtt_transformation_process_code)
        except (KeyError, ValueError) as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e
        try:
            with open(f"{cls._src_path}{os.sep}broker_mqtt{os.sep}mqtt.py", "w") as f:
                f.write(output)
        except Exception as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def _reset_converter_code(cls):
        """The method includes a functionality to reset the converter code
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        """
        try:
            with open(f"{cls._src_path}{os.sep}templates{os.sep}converter_empty.template") as fi:
                file_input: str = fi.read()
        except FileNotFoundError as e:
            raise HanaInjectorError(f"File not found. {cls._CHECK_ERROR}") from e
        try:
            with open(f"{cls._src_path}{os.sep}converter{os.sep}converter.py", "w") as fo:
                fo.write(file_input)
        except FileNotFoundError as e:
            raise HanaInjectorError(f"File not found. {cls._CHECK_ERROR}") from e

    @classmethod
    def _generate_converter_code(cls):
        """The method includes a functionality to generate the converter code
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        """
        try:
            template = cls._env.get_template("converter.template")
        except Exception as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e
        for i in range(0, len(cls._generator_list)):
            (mqtt_payload_values, method_list, sep_method_values) = cls._get_mqtt_payload_values(
                str(cls._generator_list[i]["method_name"]).lower(),
                cls._generator_list[i]["mqtt_payload"],
                i,
            )
            try:
                output = template.render(
                    converter_method_name=str(cls._generator_list[i]["method_name"]).lower(),
                    mqtt_payload_values=mqtt_payload_values,
                    method_list=method_list,
                    sep_method_values=sep_method_values,
                )
            except ValueError as e:
                raise HanaInjectorError(cls._CHECK_ERROR) from e
            try:
                with open(f"{cls._src_path}{os.sep}converter{os.sep}converter.py", "a") as f:
                    f.write("\n")
                    f.write(output)
                    f.write("\n")
            except Exception as e:
                raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def _get_mqtt_payload_values(cls, method_name: str, mqtt_payload: list, generator_index: int) -> tuple:
        """The method includes a functionality to get the MQTT payload values
        Args:
            method_name (str): Specify the MQTT method name
            mqtt_payload (list): Specify the MQTT payload as list
            generator_index (int): Specify the generator index
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        Returns:
            mqtt_payload_values, method_list, sep_method_values (tuple): Returns the MQTT payload values
        """
        if mqtt_payload is None or len(mqtt_payload) == 0:
            raise HanaInjectorError("Please, check the mqtt values") from ValueError
        return cls.__extract_mqtt_payload_values(method_name, mqtt_payload, generator_index)

    @classmethod
    def _format_converter_code(cls):
        """The method includes a functionality to format the converter code using black
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        """
        try:
            import black as _black

            converter_path = f"{cls._src_path}{os.sep}converter{os.sep}converter.py"
            with open(converter_path, encoding="utf-8") as f:
                source = f.read()
            formatted = _black.format_str(source, mode=_black.Mode())
            with open(converter_path, "w", encoding="utf-8") as f:
                f.write(formatted)
        except Exception as e:
            raise HanaInjectorError(f"Failed to format converter with black: {e}") from e

    @classmethod
    def _reset_sql_code(cls):
        """The method includes a functionality to reset the SQL code
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        """
        try:
            with open(f"{cls._src_path}{os.sep}templates{os.sep}sql_empty.template") as fi:
                file_input: str = fi.read()
        except FileNotFoundError as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e
        try:
            with open(f"{cls._src_path}{os.sep}database_sql{os.sep}sql.py", "w") as fo:
                fo.write(file_input)
        except FileNotFoundError as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def _generate_sql_code(cls):
        """The method includes a functionality to generate the SQL code
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        """
        for i in range(0, len(cls._generator_list)):
            mqtt_payload: list = cls._generator_list[i]["mqtt_payload"]
            if mqtt_payload is None or len(mqtt_payload) == 0:
                raise HanaInjectorError("Please, check the mqtt payload") from ValueError
            cls.__create_sql_sep_code(mqtt_payload, i)
            cls.__create_sql_base_code(mqtt_payload, i)

    @classmethod
    def _write_sql_code_to_file(cls, sql_method_name: str, sql_method_values: str, sql_method_payload: str):
        """The method includes a functionality to write the SQL code to a file
        Args:
            sql_method_name (str): Specify the SQL method name
            sql_method_values (str): Specify the SQL method values
            sql_method_payload (str): Specify the SQL method payload
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        Returns:
            None
        """
        template = cls._env.get_template("sql.template")
        if sql_method_name != "" or sql_method_values != "" or sql_method_payload != "":
            output = template.render(
                sql_method_name=sql_method_name,
                sql_method_values=sql_method_values,
                sql_method_payload=sql_method_payload,
            )
            with open(f"{cls._src_path}{os.sep}database_sql{os.sep}sql.py", "a") as f:
                f.write("\n")
                f.write(output)
                f.write("\n")
        else:
            raise HanaInjectorError("Please, check the generator code and open a issue") from Exception

    @classmethod
    def __create_sql_sep_code(cls, mqtt_payload: list, index: int):
        """The method includes a functionality to create the separated SQL code
        Args:
            mqtt_payload (list): Specify the MQTT payload list
            index (int): Specify the index
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        Returns:
            None
        """
        sep_method_count: int = 0
        sql_method_payload_list: list = cls._generator_list[index].get("hana_sql_query_sep")
        for j in mqtt_payload:
            if re.compile(f".*{cls._SEC_LIST_DICT}*").match(str(j)):
                sql_method_name: str = str(
                    f"{cls._generator_list[index]['method_name']}_sep{sep_method_count + 1}"
                ).lower()
                values_sec: str = str(j).split("|")[0]
                values_pri: str = str(j).split("|")[1].lower().replace("'}", "")
                values_sec = values_sec.split("(")[1]
                values_sec = values_sec.split(")")[0]
                values_sec_list: list = values_sec.replace(" ", "").split(",")
                sql_method_values = values_pri + ", " + ", ".join(values_sec_list).lower()
                try:
                    cls._write_sql_code_to_file(
                        sql_method_name, sql_method_values, str(sql_method_payload_list[sep_method_count])
                    )
                except Exception as e:
                    raise HanaInjectorError(cls._CHECK_ERROR) from e
                sep_method_count = sep_method_count + 1

    @classmethod
    def __create_sql_base_code(cls, mqtt_payload: list, index: int):
        """The method includes a functionality to create the SQL base code
        Args:
            mqtt_payload (list): Specify the MQTT payload list
            index (int): Specify the index
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        Returns:
            None
        """
        for hana_sql_query_index in range(0, len(cls._generator_list[index]["hana_sql_query"])):
            sql_method_name = str(f"{cls._generator_list[index]['method_name']}_{hana_sql_query_index + 1}").lower()
            sql_method_payload = str(cls._generator_list[index]["hana_sql_query"][hana_sql_query_index])
            mqtt_payload_cleaned: list = mqtt_payload.copy()
            for m in mqtt_payload:
                if re.compile(f".*{cls._SEC_LIST_DICT}*").match(str(m)):
                    mqtt_payload_cleaned.remove(m)
            mqtt_payload_dict = []
            for n in mqtt_payload_cleaned:
                mqtt_payload_dict.append(list(n)[0])
            sql_method_values = ", ".join(mqtt_payload_dict).lower()
            try:
                cls._write_sql_code_to_file(sql_method_name, sql_method_values, sql_method_payload)
            except Exception as e:
                raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def __extract_mqtt_payload_values(cls, method_name: str, mqtt_payload: list, generator_index: int) -> tuple:
        """The method includes a functionality to extract the MQTT payload values
        Args:
            method_name (str): Specify the method name
            mqtt_payload (list): Specify the MQTT payload list
            generator_index (int): Specify the generator index
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        Returns:
            mqtt_payload_values, method_list, sep_method_values (tuple): Returns the MQTT payload values
        """
        mqtt_payload_values: list = []
        method_value: str = ""
        sep_method_values: list = []
        sep_method_count: int = 0
        for index in range(0, len(mqtt_payload)):
            # The list object includes dicts
            for key in mqtt_payload[index]:
                if (
                    mqtt_payload[index][key] not in cls._SUPPORTED_TYPES
                    and cls._SEC_LIST_DICT not in mqtt_payload[index][key]
                ):
                    raise HanaInjectorError(
                        f"Only supported types are available. "
                        f"Please, change your selected type: {mqtt_payload[index][key]}"
                    ) from ValueError
                mqtt_payload_values, sep_method_values, method_value, sep_method_count = cls.__generate_mqtt_payload(
                    mqtt_payload,
                    index,
                    key,
                    sep_method_count,
                    method_name,
                    mqtt_payload_values,
                    sep_method_values,
                    method_value,
                )
        if cls._generator_list[generator_index].get("hana_sql_query_sep") is not None and sep_method_count != len(
            cls._generator_list[generator_index].get("hana_sql_query_sep", [])
        ):
            raise HanaInjectorError(
                "Please, specify the hana_sql_query_sep inside the config and check the used queries"
            )
        method_list: list = []
        for i in range(0, len(cls._generator_list[generator_index]["hana_sql_query"])):
            method_list.append(f"SQL.{method_name}_{i + 1}({method_value})")
        return mqtt_payload_values, method_list, sep_method_values

    @classmethod
    def __generate_mqtt_payload(
        cls,
        mqtt_payload: list,
        index: int,
        key: str,
        sep_method_count: int,
        method_name: str,
        mqtt_payload_values: list,
        sep_method_values: list,
        method_value: str,
    ) -> tuple:
        """The method includes a functionality to generate the MQTT payload
        Args:
            mqtt_payload (list): Specify the MQTT payload as list
            index (int): Specify the extracted index as integer
            key (str): Specify the extracted key as string
            sep_method_count (int): Specify the separated method count
            method_name (str): Specify the method name
            mqtt_payload_values (list): Specify the MQTT payload values
            sep_method_values (list): Specify the separated method values
            method_value (str): Specify the method value
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        Returns:
            mqtt_payload_values, sep_method_values, method_value, sep_method_count (tuple): Returns the generated code as tuple
        """
        if "sep:" in mqtt_payload[index][key]:
            sep_method_count = sep_method_count + 1
        generated_code, sep_method = cls.__generate_mqtt_payload_values(
            mqtt_payload, index, key, sep_method_count, method_name
        )
        mqtt_payload_values.append(generated_code)
        if sep_method != {}:
            sep_method_values.append(sep_method)
        if index < (len(mqtt_payload) - 1):
            method_value += str(key).lower() + ", "
        elif cls._SEC_LIST_DICT not in mqtt_payload[index][key]:
            method_value += str(key).lower()
        else:
            method_value = method_value[:-2]
        return mqtt_payload_values, sep_method_values, method_value, sep_method_count

    @classmethod
    def __generate_mqtt_payload_values(
        cls, mqtt_payload: list, index: int, key: str, hana_key_index: int, method_name: str
    ) -> tuple:
        """The method includes a functionality to generate the MQTT payload values
        Args:
            mqtt_payload (list): Specify the MQTT payload as list
            index (int): Specify the extracted index as integer
            key (str): Specify the extracted key as string
            hana_key_index (int): Specify the Hana key index
            method_name (str): Specify the method name
        Returns:
            generated_code, sep_method (tuple): Returns the generated code as tuple
        """
        sep_method: dict = {}
        if mqtt_payload[index][key] == "generateDate":
            generated_code = (
                f"{str(key).lower()}: datetime = datetime.datetime.strptime(payload['{key}'], '%Y-%m-%d').date()"
            )
        elif mqtt_payload[index][key] == "generateDatetime":
            generated_code = f"{str(key).lower()}: datetime = datetime.datetime.strptime(payload['{key}'], '%Y-%m-%dT%H:%M:%SZ').date()"
        elif cls._SEC_LIST_DICT in mqtt_payload[index][key]:
            generated_code = f"{str(key).lower()}: list = payload['{key}']"
            sep_method = cls.__extract_sep_methods(mqtt_payload, index, key, hana_key_index, method_name)
        else:
            generated_code = f"{str(key).lower()}: {mqtt_payload[index][key]} = payload['{key}']"
        return generated_code, sep_method

    @classmethod
    def __extract_sep_methods(
        cls, mqtt_payload: list, index: int, key: str, hana_key_index: int, method_name: str
    ) -> dict:
        """The method includes a functionality to extract the separated values and return them as dictionary
        Args:
            mqtt_payload (list): Specify the MQTT payload as list
            index (int): Specify the extracted index as integer
            key (str): Specify the extracted key as string
            hana_key_index (int): Specify the Hana key index
            method_name (str): Specify the method name
        Raises:
            HanaInjectorError: Wrapper exception to reformat the forwarded potential exception and include inside the trowed stacktrace
        Returns:
            sep_method (dict): Returns the separated value as dict
        """
        sep_method: dict = {}
        try:
            sep_method_value: str = ""
            values_sec: str = str(mqtt_payload[index][key]).split("|")[0]
            values_prio: str = str(mqtt_payload[index][key]).split("|")[1]
            values_sec = values_sec.split("(")[1]
            values_sec = values_sec.split(")")[0]
            values_sec_list: list = values_sec.split(",")
            for j in range(0, len(values_sec_list)):
                if j < (len(values_sec_list) - 1):
                    sep_method_value += f"attributes['{str(values_sec_list[j]).strip()}'], "
                else:
                    sep_method_value += f"attributes['{str(values_sec_list[j]).strip()}']"
            sep_method["for"] = f"for i in range(0, len({str(key).lower()})):"
            sep_method["value"] = f"attributes = eval(str({str(key).lower()}[i]))"
            sep_method["method"] = f"SQL.{method_name}_sep{hana_key_index}({values_prio.lower()}, {sep_method_value})"
            return sep_method
        except Exception as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e
