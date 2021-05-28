import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.FileHandler('logging/logging.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

def log_arrival(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Demand arrival: ID - " + str(demand.id) + ". Class ID - " + str(demand.class_id) +
                      ". Current Time: " + str(current_time))


def log_full_queue(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "Demand arrival (FULL QUEUE): ID - " + str(demand.id) + ". Class ID - " + str(demand.class_id) +
            ". Current Time: " + str(current_time))


def log_service_start(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Demand start service: ID - " + str(demand.id) + ". Class ID - " +
                      str(demand.class_id) + ". Current Time: " + str(current_time))


def log_leaving(demand, current_time):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Demand leaving: ID - " + str(demand.id) + ". Class ID - " + str(demand.class_id) +
                      ". Current Time: " + str(current_time))


def log_network_state(times, servers):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Server's state: " + str(servers.get_demands_ids_on_servers()))
        logger.debug("Server's state with min time: " +
                      str(servers.get_fragments_service_durations()))
        logger.debug("Event times: = " +
                      str([times.arrival, times.service_start, times.leaving]))
