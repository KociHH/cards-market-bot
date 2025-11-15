import logging


logger = logging.getLogger(__name__)


def parsing_callback_data(callback: str, check_params: int) -> list | None:
    """
    parse: name_data-page-type_func
    
    return: без названия даты, начиная со страницы
    """
    
    if check_params < 3:
        logger.error("Аргумент check_params слишком мал")
        return None
    
    data = callback.split("-")
    if len(data) < check_params:
        logger.error(f"callback содержит меньше элементов чем ожидается: {len(data)} < {check_params}")
        return None
    
    result_params = []
    
    for i in range(1, check_params):
        if i < len(data):
            result_params.append(data[i])
        else:
            logger.error(f"Недостаточно элементов в callback: ожидалось {check_params}, получено {len(data)}")
            return None
    
    return result_params
