import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.FileHandler("logging/logging.log", "w", "utf-8")
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def log_arrival(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Demand arrival: ID - {0}. Class ID - {1}. Current Time: {2}".format(
                str(demand.id), str(demand.class_id), str(current_time)
            )
        )


def log_full_queue(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Demand arrival (FULL QUEUE): ID - {0}. Class ID - {1}. Current Time: {2}".format(
                str(demand.id), str(demand.class_id), str(current_time)
            )
        )


def log_service_start(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Demand start service: ID - {0}. Class ID - {1}. Current Time: {2}".format(
                str(demand.id), str(demand.class_id), str(current_time)
            )
        )


def log_leaving(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Demand leaving: ID - {0}. Class ID - {1}. Current Time: {2}".format(
                str(demand.id), str(demand.class_id), str(current_time)
            )
        )


def log_network_state(times, servers):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Server's state: {0}".format(str(servers.get_demands_ids_on_servers()))
        )
        logger.debug(
            "Server's state with min time: {0}".format(
                str(servers.get_fragments_service_durations())
            )
        )
        logger.debug(
            "Event times: = {0}".format(
                str([times.arrival, times.service_start, times.leaving])
            )
        )
