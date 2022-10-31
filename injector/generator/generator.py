"""
Created on 18.02.2021

@author: Pascal Zimmermann
"""
import os
import re
import pathlib
import subprocess
from typing import Dict, List, Tuple
from jinja2 import FileSystemLoader, Environment

from load_config.load_config import LoadConfig
from custom_logger.custom_logger import HanaInjectorError


# ===============================================================================
# Class to generate sql, mqtt and converter code
# ===============================================================================
class Generator:
    _SEC_LIST_DICT: str = "sep:ListDict"
    _CHECK_ERROR: str = "Please, check the error"

    _SUPPORTED_TYPES: List = [
        "int",
        "double",
        "str",
        "List",
        "ListDict",
        _SEC_LIST_DICT,
        "Dict",
        "generateDate",
        "generateDatetime",
    ]

    _generator_list: List = LoadConfig.load_correct_config_dict()["generator"]
    _file_loader = FileSystemLoader(
        LoadConfig.load_correct_config_dict()["hana_injector"]["template"]
    )
    _env = Environment(loader=_file_loader, trim_blocks=True, lstrip_blocks=True, autoescape=False)
    _src_path = os.path.dirname(str(pathlib.Path(__file__).parent.absolute()))

    def __init__(self):
        self._generate_converter()

    @classmethod
    def _generate_converter(cls):
        if cls._generator_list is not None and len(cls._generator_list) == 0:
            raise HanaInjectorError(
                "Please, specify the generator rules"
            ) from Exception

        cls._generate_mqtt_code()
        cls._reset_converter_code()
        cls._generate_converter_code()
        cls._format_converter_code()
        cls._reset_sql_code()
        cls._generate_sql_code()

    @classmethod
    def _generate_mqtt_code(cls):
        try:
            template = cls._env.get_template("mqtt.template")
        except Exception as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e

        mqtt_transformation_process_code: List = list()

        for i in range(0, len(cls._generator_list)):
            mqtt_transformation_process_code.append(
                f"cls._client.message_callback_add(\"{cls._generator_list[i]['mqtt_topic']}\", "
                f"converter.{str(cls._generator_list[i]['method_name']).lower()})"
            )

        try:
            output = template.render(
                mqtt_transformation_process_code=mqtt_transformation_process_code
            )
        except (KeyError, ValueError) as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e

        try:
            f = open(f"{cls._src_path}{os.sep}broker_mqtt{os.sep}mqtt.py", "w")
            f.write(output)
            f.close()
        except Exception as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def _reset_converter_code(cls):
        try:
            fi = open(
                f"{cls._src_path}{os.sep}templates{os.sep}converter_empty.template", "r"
            )
            file_input: str = fi.read()
            fi.close()
        except FileNotFoundError as e:
            raise HanaInjectorError(f"File not found. {cls._CHECK_ERROR}") from e

        try:
            fo = open(f"{cls._src_path}{os.sep}converter{os.sep}converter.py", "w")
            fo.write(file_input)
            fo.close()
        except FileNotFoundError as e:
            raise HanaInjectorError(f"File not found. {cls._CHECK_ERROR}") from e

    @classmethod
    def _generate_converter_code(cls):
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
                    converter_method_name=str(
                        cls._generator_list[i]["method_name"]
                    ).lower(),
                    mqtt_payload_values=mqtt_payload_values,
                    method_list=method_list,
                    sep_method_values=sep_method_values,
                )
            except ValueError as e:
                raise HanaInjectorError(cls._CHECK_ERROR) from e

            try:
                f = open(f"{cls._src_path}{os.sep}converter{os.sep}converter.py", "a")
                f.write("\n")
                f.write(output)
                f.write("\n")
                f.close()
            except Exception as e:
                raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def _get_mqtt_payload_values(cls, method_name: str, mqtt_payload: List, generator_index: int):
        if mqtt_payload is None or len(mqtt_payload) == 0:
            raise HanaInjectorError("Please, check the mqtt values") from ValueError

        return cls.__extract_mqtt_payload_values(method_name, mqtt_payload, generator_index)

    @classmethod
    def _format_converter_code(cls):
        cmd: List = ["black", f"{cls._src_path}{os.sep}converter{os.sep}converter.py"]
        result = subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)

        if result.returncode != 0:
            raise HanaInjectorError(
                "Please, check if you installed black"
            ) from Exception

    @classmethod
    def _reset_sql_code(cls):
        try:
            fi = open(
                f"{cls._src_path}{os.sep}templates{os.sep}sql_empty.template", "r"
            )
            file_input: str = fi.read()
            fi.close()
        except FileNotFoundError as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e

        try:
            fo = open(f"{cls._src_path}{os.sep}database_sql{os.sep}sql.py", "w")
            fo.write(file_input)
            fo.close()
        except FileNotFoundError as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def _generate_sql_code(cls):
        for i in range(0, len(cls._generator_list)):
            mqtt_payload: List = cls._generator_list[i]["mqtt_payload"]

            if mqtt_payload is None or len(mqtt_payload) == 0:
                raise HanaInjectorError(
                    "Please, check the mqtt payload"
                ) from ValueError

            cls.__create_sql_sep_code(mqtt_payload, i)
            cls.__create_sql_base_code(mqtt_payload, i)

    @classmethod
    def _write_sql_code_to_file(
        cls, sql_method_name: str, sql_method_values: str, sql_method_payload: str
    ):
        template = cls._env.get_template("sql.template")

        if (
            sql_method_name != ""
            or sql_method_values != ""
            or sql_method_payload != ""
        ):
            output = template.render(
                sql_method_name=sql_method_name,
                sql_method_values=sql_method_values,
                sql_method_payload=sql_method_payload,
            )

            f = open(f"{cls._src_path}{os.sep}database_sql{os.sep}sql.py", "a")
            f.write("\n")
            f.write(output)
            f.write("\n")
            f.close()
        else:
            raise HanaInjectorError(
                "Please, check the generator code and open a issue"
            ) from Exception

    @classmethod
    def __create_sql_sep_code(cls, mqtt_payload: List, index: int):
        sep_method_count: int = 0
        sql_method_payload_list: List = cls._generator_list[index].get("hana_sql_query_sep")

        for j in mqtt_payload:
            if re.compile(f".*{cls._SEC_LIST_DICT}*").match(str(j)):
                sql_method_name: str = str(
                    f"{cls._generator_list[index]['method_name']}_sep{sep_method_count + 1}"
                ).lower()

                values_sec: str = str(j).split("|")[0]
                values_pri: str = str(j).split("|")[1].lower().replace("'}", "")

                values_sec = values_sec.split("(")[1]
                values_sec = values_sec.split(")")[0]
                values_sec_list: List = values_sec.replace(" ", "").split(",")

                sql_method_values = (
                    values_pri + ", " + ", ".join(values_sec_list).lower()
                )

                try:
                    cls._write_sql_code_to_file(
                        sql_method_name, sql_method_values, str(sql_method_payload_list[sep_method_count])
                    )
                except Exception as e:
                    raise HanaInjectorError(cls._CHECK_ERROR) from e

                sep_method_count = sep_method_count + 1

    @classmethod
    def __create_sql_base_code(cls, mqtt_payload: List, index: int):
        for hana_sql_query_index in range(0, len(cls._generator_list[index]["hana_sql_query"])):
            sql_method_name = str(f"{cls._generator_list[index]['method_name']}_{hana_sql_query_index + 1}").lower()
            sql_method_payload = str(cls._generator_list[index]["hana_sql_query"][hana_sql_query_index])

            mqtt_payload_cleaned: List = mqtt_payload.copy()

            for m in mqtt_payload:
                if re.compile(f".*{cls._SEC_LIST_DICT}*").match(str(m)):
                    mqtt_payload_cleaned.remove(m)

            mqtt_payload_dict = list()
            for n in mqtt_payload_cleaned:
                mqtt_payload_dict.append(list(n)[0])

            sql_method_values = ", ".join(mqtt_payload_dict).lower()

            try:
                cls._write_sql_code_to_file(
                    sql_method_name, sql_method_values, sql_method_payload
                )
            except Exception as e:
                raise HanaInjectorError(cls._CHECK_ERROR) from e

    @classmethod
    def __extract_mqtt_payload_values(cls, method_name: str, mqtt_payload: List, generator_index: int) -> Tuple:
        mqtt_payload_values: List = list()
        method_value: str = ""
        sep_method_values: List = list()
        sep_method_count: int = 0

        for index in range(0, len(mqtt_payload)):
            # The List object includes dicts
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
                    mqtt_payload, index, key, sep_method_count, method_name, mqtt_payload_values, sep_method_values,
                    method_value)

        if cls._generator_list[generator_index].get("hana_sql_query_sep") is not None and sep_method_count != len(cls._generator_list[generator_index].get("hana_sql_query_sep", list())):
            raise HanaInjectorError("Please, specify the hana_sql_query_sep inside the config and check the used "
                                    "queries")

        method_list: List = list()

        for i in range(0, len(cls._generator_list[generator_index]["hana_sql_query"])):
            method_list.append(f"SQL.{method_name}_{i + 1}({method_value})")

        return mqtt_payload_values, method_list, sep_method_values

    @classmethod
    def __generate_mqtt_payload(cls, mqtt_payload: List, index: int, key: str, sep_method_count: int,
                                method_name: str, mqtt_payload_values: List, sep_method_values: List,
                                method_value: str) -> Tuple:
        if "sep:" in mqtt_payload[index][key]:
            sep_method_count = sep_method_count + 1

        generated_code, sep_method = cls.__generate_mqtt_payload_values(mqtt_payload, index, key,
                                                                        sep_method_count, method_name)
        mqtt_payload_values.append(generated_code)

        if sep_method != dict():
            sep_method_values.append(sep_method)

        if index < (len(mqtt_payload) - 1):
            method_value += str(key).lower() + ", "
        elif cls._SEC_LIST_DICT not in mqtt_payload[index][key]:
            method_value += str(key).lower()
        else:
            method_value = method_value[:-2]

        return mqtt_payload_values, sep_method_values, method_value, sep_method_count

    @classmethod
    def __generate_mqtt_payload_values(cls, mqtt_payload: List, index: int, key: str, hana_key_index: int,
                                       method_name: str) -> Tuple:
        sep_method: Dict = dict()

        if mqtt_payload[index][key] == "generateDate":
            generated_code = f"{str(key).lower()}: datetime = datetime.datetime.strptime(payload['{key}'], '%Y-%m-%d').date()"
        elif mqtt_payload[index][key] == "generateDatetime":
            generated_code = f"{str(key).lower()}: datetime = datetime.datetime.strptime(payload['{key}'], '%Y-%m-%dT%H:%M:%SZ').date()"
        elif cls._SEC_LIST_DICT in mqtt_payload[index][key]:
            generated_code = f"{str(key).lower()}: List = payload['{key}']"

            sep_method = cls.__extract_sep_methods(mqtt_payload, index, key, hana_key_index, method_name)
        else:
            generated_code = f"{str(key).lower()}: {mqtt_payload[index][key]} = payload['{key}']"

        return generated_code, sep_method

    @classmethod
    def __extract_sep_methods(cls, mqtt_payload: List, index: int, key: str, hana_key_index: int,
                              method_name: str) -> Dict:
        sep_method: Dict = dict()

        try:
            sep_method_value: str = ""
            values_sec: str = str(mqtt_payload[index][key]).split("|")[0]
            values_prio: str = str(mqtt_payload[index][key]).split("|")[1]

            values_sec = values_sec.split("(")[1]
            values_sec = values_sec.split(")")[0]
            values_sec_list: List = values_sec.split(",")

            for j in range(0, len(values_sec_list)):
                if j < (len(values_sec_list) - 1):
                    sep_method_value += (
                        f"attributes['{str(values_sec_list[j]).strip()}'], "
                    )
                else:
                    sep_method_value += (
                        f"attributes['{str(values_sec_list[j]).strip()}']"
                    )

            sep_method[
                "for"
            ] = f"for i in range(0, len({str(key).lower()})):"
            sep_method[
                "value"
            ] = f"attributes = eval(str({str(key).lower()}[i]))"
            sep_method["method"] = f"SQL.{method_name}_sep{hana_key_index}({values_prio.lower()}, {sep_method_value})"

            return sep_method
        except Exception as e:
            raise HanaInjectorError(cls._CHECK_ERROR) from e
