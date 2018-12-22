import os
import logging
import re
import yaml
import series_handler
import shutil
from yaml_helper import yaml_get

logging.basicConfig(level=logging.INFO)

localPathRoot = "/Users/Andrew/Movies/TV Shows/"
remotePathRoot = "/Volumes/videos/"
validExtension = "mp4"
destFile = 'dest.yaml'
 
SERIES = series_handler.series_handler()

def parseFile(fileName, y):
    '''
    Parse the file given a specific yaml config
    :param fileName: filename without path
    :param y: yaml file
    :return: tuple of (series,episode) and the filename to rename to
    '''

    # regex must pos0 = seriesID, pos1=episodeID, pos2=episodeName
    # if not found, return empty group

    s= []
    s.append("(?:.*)s([0-9]+)e([0-9]+)\.(.*)\.")
    s.append("Series ([0-9]+) - ([0-9]+)\.?(.*)(?:\(\()")
    s.append("Series ([0-9]+) - Episode ([0-9]+)()")
    s.append("Series ([0-9]+)\s+Episode ([0-9]+)()")
    s.append("- Episode ()([0-9]+) - (.+)(\.mp4)")
    s.append("- Episode ()([0-9]+)()")
    s.append("- ()([0-9]+)\.?(.+)\(\(")
    s.append("- ()()(.+)\.?(.+)\(\(")
    s.append("()()(.+)\s*-\s*\(\(")

    ret = []

    # fileName = fileName.replace(' ((hvfhd))','')

    # Format of regex groups:  0=seriesID  1=episodeID  3=episode name

    for q in s:
        r = re.compile(q,re.IGNORECASE)
        res = r.search(fileName)

        if res != None:
            if res.lastindex == 1:
                ret = ["1", res.group(1)]
            else:
                ret = [res.group(1),res.group(2)]

            logging.info('  - matched template: ' + q)

            ret[0] = "1" if ret[0] is None else ret[0]

            ep_name = res.group(3)                  # get the actual name
            series_id = ret[0]
            episode_id = ret[1]

            if y != None:
                if 'series' in y:
                    series_id = str(int(y['series']))
                    logging.info('  - series updated from yaml s:{}'.format(series_id))

                if 'episode_offset' in y:
                    episode_id = str(int(ret[1]) + int(y['episode_offset']))
                    logging.info('  - episode updated by offset from yaml e:{}'.format(episode_id))


            if 'id' in y:
                id = int(y['id'])
            else:
                id = 0

            s_id, e_id = SERIES.lookup_episode(y['name'], ep_name, id=id)

            # If we want to skip any lookup and just use the regex
            if yaml_get(y,'skip_match') == 1:
                logging.info("  - Skipping lookup match, using regex match")
                s_id = None
                e_id = None

            if s_id == "error":
                # If we force a match to the API handler then just return as we can't complete
                if yaml_get(y, 'force_match') == 1:
                    logging.info(" - Skipping file as no API match")
                    return (None,None)
                s_id = None
                e_id = None

            series_id = s_id if s_id is not None else series_id
            episode_id = e_id if e_id is not None else episode_id

            f = "s{0}e{1} {2}".format(series_id.zfill(2), episode_id.zfill(2), fileName)

            return (ret, f)


def moveFile(localPath,remotePath,fileName, fileNameSource):

    # create the local, remote and completed filenames
    lf = os.path.join(localPath, fileNameSource)
    rf = os.path.join(remotePath, fileName)
    cf = os.path.join(localPathRoot, "_completed", fileName)

    # if file not there then copy, else rename local copy
    if os.path.isfile(rf):
        if not os.path.isfile(cf):
            logging.info('File already exists, just moving file: ' + fileNameSource)
            os.rename(lf, cf)
        else:
            logging.info('File already exists in remote and completed ({}), deleting'.format(fileNameSource))
            os.remove(lf)

    else:
        logging.info('  - Copying file: ' + fileName)
        shutil.copy2(lf, rf)
        os.rename(lf, cf)


def run_move():
    # recurse paths
    for root, dirName, files in os.walk(localPathRoot):
        if destFile in files:
            logging.info('Found {0} in: {1}'.format(destFile, root))

            filesToCopy = []
            for f in files:
                if f.endswith(validExtension) and f != destFile:
                    filesToCopy.append(f)

            logging.info(str(len(filesToCopy)) + ' file(s) found to copy')

            # parse dest file
            fo = open(os.path.join(root, destFile), 'r')
            y = yaml.load(fo)
            fo.close()

            # iterate through the files
            for f in filesToCopy:
                logging.info("Parsing: {}".format(f))

                p = parseFile(f, y)             # parse the file
                if p[0] is None:                # if error skip the file
                    continue
                fn = p[1]                       # filename is element 2

                # build remote path
                r = remotePathRoot
                if 'dest' in y:
                    r = os.path.join(r, y['dest'])

                    if not os.path.isdir(r):
                        logging.info("  - Remote path: {} does not exist, skipping file".format(r))
                    else:
                        moveFile(root, r, fn, f)   # finally move the file

                logging.info(" ")

if __name__ == '__main__':
    run_move()
