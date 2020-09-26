# from tscraper import scrape_match
import tscraper
import tennisrules
import ttracker
import sys
import plotting


def main(URL):
    match = tscraper.scrape_match(URL)
    
    p1_tracked, p2_tracked, EoS = ttracker.trackmatch(match)

    plotting.momentum_animation(match, p1_tracked, p2_tracked, EoS, save_video=True)

    return 0

main(str(sys.argv[1]))