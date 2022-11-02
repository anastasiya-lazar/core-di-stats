from solution.sp.azure.stats_msg_handler import StatsMessageHandlerSP
import config as conf


def get_stats_message_handler():
    return StatsMessageHandlerSP(conf.STATS_QUEUE_CONNECTION_STRING)
