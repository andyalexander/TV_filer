import tvdbsimple as tvdb
import Levenshtein
import logging
import configparser

MATCH_TOLERANCE = 2     # number of characters to allow
CONFIG_NAME = 'default.config'

class series_handler():
    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_NAME)


        tvdb.KEYS.API_KEY = cfg['thetvdb']['Key']
        self.last_series_name = None
        self.last_series_obj = None

    def lookup_episode(self, seriesName, episodeName, id = 0):
        """
        Lookup a TV episode from thetvdb, matches based on levenstein distance comparisson
        :param seriesName: series name
        :param episodeName: episide name
        :return: series_id and episode_id as strings
        """

        if seriesName is None or episodeName is None:
            return (None,None)

        if seriesName != self.last_series_name:
            logging.info(" - Searching thetvdb for:{}".format(seriesName))
            search = tvdb.Search()
            response = search.series(seriesName)
            s = search.series

            if id > 0:
                for s in response:
                    if s['id'] == id:
                        show = tvdb.Series(id)
                        break
            elif id == 0:
                show = tvdb.Series(s[0]['id'])
            else:
                logging.info(' - Unable to find series id:{} - terminating'.format(id))
                return (None,None)

            self.last_series_name = seriesName
            self.last_series_obj = show

        show = self.last_series_obj

        episodes = show.Episodes.all()
        logging.info("  - Found {} episodes".format(len(episodes)))
        if episodes == []:
            return (None, None)

        for i, e in enumerate(episodes[::-1]):
            ep_name = e['episodeName']

            if ep_name is not None:
                n = Levenshtein.distance(episodeName, ep_name)

                if n <= MATCH_TOLERANCE:
                    e_id = e['airedEpisodeNumber']
                    s_id = e['airedSeason']
                    logging.info("  - Matched [{0}] to episode name: [{1}]".format(episodeName, ep_name))
                    return (str(s_id), str(e_id))

        logging.info(" - UNABLE TO MATCH: {}".format(episodeName))
        return ("error", "expected series not found")




