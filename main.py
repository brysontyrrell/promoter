from config import config
import jsslib
import logging
import promoter
import sys

__author__ = 'brysontyrrell'

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

logging.basicConfig(level=logging.DEBUG)


def main():
    # Configuration values are set in config.py
    src_cfg = config['source_jss']
    logging.info("Source JSS: {}".format(src_cfg['url']))
    trg_cfg = config['target_jss']
    logging.info("Target JSS: {}".format(trg_cfg['url']))

    source_jss = jsslib.JSS(src_cfg['url'], src_cfg['username'], src_cfg['password'], read_only=True)
    target_jss = jsslib.JSS(trg_cfg['url'], trg_cfg['username'], trg_cfg['password'])

    logging.info("prepping target jss")
    promoter.clean_jss(target_jss)
    promoter.promote_jss(source_jss, target_jss)

if __name__ == '__main__':
    main()