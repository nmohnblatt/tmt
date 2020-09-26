import os
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import tennisrules as tennis
from datetime import date


# This function finds the total number of sets played for a match on Scoreboard.com
def find_number_of_sets(page_soup):
    return sum([int(each_player.get_text()) for each_player in page_soup.find('div', {'id': 'event_detail_current_result'}).find_all('span', {'class': 'scoreboard'})])

def parse_players(page_title):
    player_data = [player.split() for player in page_title.split('|')[1].split('-')]
    players = [tennis.Player(player_data[i][0], player_data[i][1]) for i in [0,1]]

    return (players[0], players[1])

def parse_game(game_soup):
    # Find BP and SP comments
    comments = game_soup('span')

    # Use decompose() to remove the comments
    if comments != []:
        for comment in comments:
            comment.decompose()

    init = [tennis.Point(['0', '0'])]

    return tennis.Game(init + [tennis.Point(string.strip().split(':')) for string in game_soup.get_text().split(',')])

def parse_tiebreak(set_soup):
    scores = [line.text for line in set_soup.find_all('td', {'class': 'match-history-score'})]
    init = [tennis.Point(['0', '0'])]
    # To reach a tiebreak, 12 games must have been played. 
    # Scoreboard.com also adds an extra line that shows the final set score.
    # We can remove these by checking the 14th element of the extracted data (12 games, 1 tb summary)
    tb_points = init + [tennis.Point(score.replace(' ','').split('-')) for score in scores[13:]]

    return tennis.Game(tb_points, True)


def parse_set(page_soup, set_number):
    # Create a new Set object
    this_set = tennis.Set(set_number, [])

    # Compute the expected id for this set
    set_id = 'tab-mhistory-' + str(set_number) + '-history'

    # Find it in the page
    set_soup = page_soup.find('div', {'id': set_id})

    # Extract the scores:
    # (scoreboard.com arranges scores into odd and even rows)
    # (We work around this quirk and merge the rows)
    odd_rows = set_soup.find_all('tr', {'class': 'odd fifteen'})
    even_rows = set_soup.find_all('tr', {'class': 'even fifteen'})
    combined_rows = mergerows(odd_rows, even_rows)

    # For each game, create a Game object and parse the game data
    for game_raw in combined_rows:
        this_set.AddGame(parse_game(game_raw))

    # Parse tiebreak data if there is one
    if len(this_set.Score) == 12:
        this_set.AddGame(parse_tiebreak(set_soup))

    this_set.FindWinner()

    return this_set

def scrape_match(URL, rules=tennis.STANDARD_ATP_WTA):
    if 'https://www.scoreboard.com' not in URL:
        raise Exception('Please use a URL from scoreboard.com \n(the application is not affiliated to the site)')

    # remove trailing slash
    if URL[-1] == '/':
        URL = URL[:-1]

    if URL.split('/')[-1][0] == '#':
        URL = '/'.join(URL.split('/')[:-1])
        

    # Obtain page title and source code using a browser
    page_title, page_source = scrape_page(URL)

    # Retrieve player info
    player1, player2 = parse_players(page_title)

    # Format the page source code
    page_soup = BeautifulSoup(page_source, 'html.parser')

    # Retrieve match info (date, tournament, round)
    info = scrape_and_parse_info(page_soup)

    # Choose rules based on info
    rules = auto_rule_select(info)

    # ompute number of sets
    total_sets_played = find_number_of_sets(page_soup)

    # Create a new Match object
    match = tennis.Match(player1, player2, rules=rules, info=info)

    # For each set, add a Set object to the match
    for set_counter in range(1,total_sets_played+1):
        match.AddSet([parse_set(page_soup, set_counter)])


    return match

def scrape_page(URL):
    # Launch browser and access the desired page
    PATH = os.getcwd() + '/chromedriver'
    driver = webdriver.Chrome(PATH)
    set_url = URL + '#point-by-point;' + str(1)
    driver.get(set_url) 

    # Wait for the scores to have loaded
    test_set_id = 'tab-mhistory-1-history'
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, test_set_id))
        )
    except selenium.common.exceptions.TimeoutException:
        raise Exception('Time out: could not load Set 1 scores')

    page_source = driver.page_source
    page_title = driver.title

    driver.quit()
    return (page_title, page_source)

# This function merges odd and even rows from a Scoreboard.com game report
def mergerows(oddrows, evenrows):
    out = []
    if  len(oddrows) > len(evenrows)+1 or len(oddrows) < len(evenrows):
        raise Exception("Issue with the sizes of odd and even rows")
    
    [out.extend([orow, erow]) for (orow, erow) in zip(oddrows, evenrows)]

    if len(oddrows) == len(evenrows)+1:
        out.append(oddrows[-1])

    return out

def scrape_and_parse_info(page_soup):
    info = {}
    match_descriptor_soup = page_soup.find('div', {'class': 'description__match'})
    date_soup = page_soup.find('div', {'id': 'utime'})
    
    months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    year = int(date_soup.text.split(',')[2].strip())
    month = months[date_soup.text.split(',')[1].strip().split()[0]]
    day = int(date_soup.text.split(',')[1].split(' ')[-1])
    
    info['DATE'] = date(year, month, day)

    t0 = match_descriptor_soup.text.split(':')
    info['CIRCUIT'] = t0[0].split('-')[0].strip()
    info['MATCH_TYPE'] = t0[0].split('-')[1].strip()
    t1 = t0[1].split(',')
    info['TOURNAMENT'] = t1[0].strip()
    info['COURT_TYPE'] = t1[1].split('-', 1)[0].strip()
    info['ROUND'] = t1[1].split('-', 1)[1].strip()

    return info


def auto_rule_select(info):
    rules = tennis.STANDARD_ATP_WTA # default value

    if info['CIRCUIT'] == 'ATP':
        if info['TOURNAMENT'] == 'US Open (USA)':
            rules = tennis.ATP_GRAND_SLAM_TB
        elif info['TOURNAMENT'] == 'Wimbledon (United Kingdom)':
            # ADD SUPPORT FOR THESE RULES (regular tiebreak at 12-12 games)
            # example game https://www.scoreboard.com/game/fyXBxdlb
            pass
        elif info['TOURNAMENT'] == 'French Open (France)':
            rules = tennis.ATP_GRAND_SLAM_NOTB
        elif info['TOURNAMENT'] == 'Australian Open (Australia)':
            rules = tennis.ATP_GRAND_SLAM_AUS
    elif info['CIRCUIT'] == 'WTA':
        if info['TOURNAMENT'] == 'Australian Open (Australia)':
            rules = tennis.WTA_GRAND_SLAM_AUS
        elif info['TOURNAMENT'] == 'Wimbledon (United Kingdom)':
            # ADD SUPPORT FOR THESE RULES (regular tiebreak at 12-12 games)
            # https://www.scoreboard.com/game/rLaE3Awe/
            pass


    return rules


# Run the tennis scraper (tscraper.py) as a standalone script
# It will print the match info for the match provided in the argument
# Works for scores from scoreboard.com only (!)
if __name__ == "__main__":
    import sys
    match = scrape_match(str(sys.argv[1]))
    match.PrintScore()