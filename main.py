import time
from pathlib import Path
import random

import vk_api
from loguru import logger


def file_txt(path: Path | str, mode: str, data: str = None) -> str | None:
    """
    Read, write, re-writing to file:
    r - read
    readlines - readlines
    w - write
    a - re-writing
    return: `str` | `None`
    """
    try:
        if mode == "readlines":
            with open(path, "r", encoding="UTF-8") as file:
                data = file.readlines()
                return data
        else:
            with open(path, mode) as file:
                if mode == "r":
                    data = file.read()
                    return data
                elif mode == "w":
                    file.write(data)
                elif mode == "a":
                    file.write(data + "\n")
    except Exception as ex:
        logger.warning(ex)


def get_audience(serch_criteria: str) -> int:

    audience = vk.ads.getTargetingStats(
        criteria=serch_criteria,
        account_id=advertising_cabinet_id,
        link_url='vk.com/team'
        )
    return audience['audience_count']


def build_serch_criteria(key_phrase: str,
                         sex: str | int = 2,
                         period: str | int = 12,
                         age_from: str | int = 0,
                         age_to: str | int = 0
                         ) -> str:

    dictionari = {
        "sex": str(sex),
        "key_phrases": key_phrase,
        "key_phrases_days": str(period),
        "age_from": str(age_from),
        "age_to": str(age_to)
        }
    dict_str = str(dictionari).replace("'", '"')
    return dict_str


def get_audience_male(key_phrase: str,
                      period: int | str,
                      age_from: str | int,
                      age_to: str | int) -> int:

    criteria = build_serch_criteria(key_phrase, 2, period, age_from, age_to)
    result = get_audience(criteria)
    return result


def get_audience_female(key_phrase: str,
                        period: int | str,
                        age_from: str | int,
                        age_to: str | int) -> int:

    criteria = build_serch_criteria(key_phrase, 1, period, age_from, age_to)
    result = get_audience(criteria)
    return result


def get_delite_line(value: str,
                    file_name: Path | str = Path("keys.txt")) -> None:
    """
    File_name:`Path`|`str`
    Input:`str` the line whose index you need to find out
    """

    def get_index_line(file_name) -> int:
        '''
        return: index line
        '''
        def get_list(file_name) -> list:
            """
            Get list from file
            """
            try:
                with open(file_name, 'r') as f:
                    data = f.readlines()
                return data
            except Exception as ex:
                logger.warning(ex)

        try:
            lines = get_list(file_name)
            index_line = lines.index(value)
            return index_line
        except Exception as ex:
            logger.warning(ex)

    def delete_line(file_name: Path | str, index: int) -> None:
        '''
        Input: name/path to file, index line
        Delete line in txt file
        '''
        try:
            with open(file_name, "r") as f:
                lines = f.readlines()

            del lines[index]

            with open(file_name, "w") as f:
                f.writelines(lines)
        except Exception as ex:
            logger.warning(ex)

    index = get_index_line(file_name)
    delete_line(file_name, index)


def main(period: str | int, age_from: str | int, age_to: str | int) -> None:

    keys = file_txt(Path('keys.txt'), "readlines")
    counter = 0

    for key in keys:
        try:
            line_for_delete = key
            current_key = key.replace("\n", "").replace("'", '"')

            male_audience = get_audience_male(current_key,
                                              period, age_from,
                                              age_to)
            time.sleep(1)
            female_audience = get_audience_female(current_key,
                                                  period, age_from,
                                                  age_to)

            if male_audience == 0 and female_audience == 0:
                persent_male = 0
            else:
                persent_male = int(
                    male_audience / (male_audience + female_audience) * 100)

            value = (f"{current_key};"
                     f"{male_audience};"
                     f"{female_audience};"
                     f"{persent_male}"
                     )

            file_txt(Path("result.txt"), "a", value)
            get_delite_line(line_for_delete,
                            file_name="keys.txt"
                            )

            counter = counter + 1
            logger.info(f"{counter} из {len(keys)}")
            random_time = random.uniform(5, 8)
            time.sleep(random_time)  # пауза между запросами

        except Exception as ex:
            file_txt(Path("errors.txt"), "a", current_key)
            logger.warning(str(ex)+" "+current_key+" Добавлено в errors.txt")
            random_time = random.uniform(5, 8)
            time.sleep(random_time)  # пауза между запросами


if __name__ == "__main__":

    advertising_cabinet_id = file_txt(Path("advertising_cabinet_id.txt"), "r")
    token = file_txt(Path("token.txt"), "r")
    vk = vk_api.VkApi(token=token).get_api()

    period = input(
        "Выберите период в днях: "
        )
    age_from = input(
        "Выберите нижнюю границу возраста от 14 до 80; 0 - без ограничений: "
        )
    age_to = input(
        "Выберите верхнюю границу возраста от 14 до 80; 0 - без ограничений: "
        )
    main(period, age_from, age_to)
