import os
import selenium
import requests
import lxml.html as LH
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class Player:
    def __init__(self, firstname, lastname):
        self.First = firstname
        self.Last = lastname

    def full_name(self):
        return (self.First + ' ' + self.Last)

class Game:
    def __init__(self, score):
        self.Score = score

    def Point(self, number):
        if number < 1 or number > len(self.Score):
            raise Exception('Index out of bound')
        return self.Score[number-1]


class Set:
    def __init__(self, score):
        self.Score = score

    def Game(self, number):
        if number < 1 or number > len(self.Score):
            raise Exception('Index out of bound')
        return self.Score[number-1]
    
    def AddGame(self, game_score):
        self.Score = self.Score + [game_score]

    def PrintScore(self):
        for game in self.Score:
            print(game.Score)



class Match:
    def __init__(self, Player1, Player2, rules):
        self.Score = []
        self.Player1 = Player1
        self.Player2 = Player2
        self.Rules = rules # support for different match lengths (slam, 5th set TB, 5th set 'super TB', etc...)

    def title(self):
        return (self.Player1.full_name() + ' - ' + self.Player2.full_name())

    def Set(self, number):
        if number < 1 or number > len(self.Score):
            raise Exception('Index out of bound')
        return self.Score[number-1]

    def AddSet(self, set_score):
        self.Score = self.Score + set_score

    def PrintScore(self):
        for set_ in self.Score:
            set_.PrintScore()


# This function merges odd and even rows from a Scoreboard.com game report
def mergerows(oddrows, evenrows):
    out = []
    if  len(oddrows) > len(evenrows)+1 or len(oddrows) < len(evenrows):
        raise Exception("Issue with the sizes of odd and even rows")
    
    [out.extend([orow, erow]) for (orow, erow) in zip(oddrows, evenrows)]

    if len(oddrows) == len(evenrows)+1:
        out.append(oddrows[-1])

    return out

def extract_points_tiebreak(set_soup):
    tb_points = []
    horizontal_dividers = set_soup.find_all('td', {'class': 'h-part'})
    if len(horizontal_dividers) == 1:
        return tb_points
    else:
        for divider in horizontal_dividers[1:]:
            if divider.get_text().split()[0] == 'Tiebreak':
                tiebreak_start = divider

    print(tiebreak_start)

    return tb_points



def extract_points_single_set(driver, URL, set_number):
    this_set = Set([])
    # set_url = URL + '#point-by-point;' + str(set_number)
    # driver.get(set_url) 
    # print(driver.title)

    # # Click on the 'Point-by-Point' tab
    # point_by_point_element = driver.find_element_by_id('a-match-history')
    # ActionChains(driver).move_to_element(point_by_point_element).click(point_by_point_element).perform()

    set_id = 'tab-mhistory-' + str(set_number) + '-history'

    try:
        set_raw = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, set_id))
        )
    except selenium.common.exceptions.TimeoutException:
        print(set_id + ': Time out')

    soup = BeautifulSoup(set_raw.get_attribute('innerHTML'), 'html.parser')

    odd_rows = soup.find_all('tr', {'class': 'odd fifteen'})
    even_rows = soup.find_all('tr', {'class': 'even fifteen'})

    combined_rows = mergerows(odd_rows, even_rows)

    for game in combined_rows:
        # Find BP and SP comments
        comments = game('span')

        # Use decompose() to remove the comments
        if comments != []:
            for comment in comments:
                comment.decompose()

        # point_results = [string.strip().split(':') for string in game.get_text().split(',')]
        # out = out + [point_results]
        this_set.AddGame(Game([string.strip().split(':') for string in game.get_text().split(',')]))


    this_set.AddGame(Game(extract_points_tiebreak(soup)))

    return this_set



# This function finds the total number of sets played for a match on Scoreboard.com
def find_number_of_sets(page_soup):
    return sum([int(each_player.get_text()) for each_player in page_soup.find('div', {'id': 'event_detail_current_result'}).find_all('span', {'class': 'scoreboard'})])

def extract_player_names(page_title):
    return [player_data.split() for player_data in page_title.split('|')[1].split('-')]
    

# This function gets the point-by-point score of a finished game
def post_match_scrape(URL):
    # Launch browser and access the desired page
    PATH = os.getcwd() + '/chromedriver'
    driver = webdriver.Chrome(PATH)

    set_url = URL + '#point-by-point;' + str(1)
    driver.get(set_url) 

    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')

    page_title = driver.title
    player1 = Player(extract_player_names(page_title)[0][0], extract_player_names(page_title)[0][1])
    player2 = Player(extract_player_names(page_title)[1][0], extract_player_names(page_title)[1][1])

    # Find the total number of sets
    # total_sets = sum([int(single_set.get_text()) for single_set in soup.find('div', {'id': 'event_detail_current_result'}).find_all('span', {'class': 'scoreboard'})])
    total_sets = find_number_of_sets(soup)

    match = Match(player1, player2, [])

    print(total_sets)


    for set_counter in range(1,total_sets+1):
        match.AddSet([extract_points_single_set(driver, URL, set_counter)])
    
    print(match.title())
    match.PrintScore()
    

    driver.quit()

# ---------------------------------------------------------------------------------------------------------------------

# def post_match_scrape(URL):
#     set_counter = 1
#     set_url= URL + '#point-by-point;' + str(set_counter)
#     page = requests.get(set_url)
#     soup = BeautifulSoup(page.content, 'html.parser')

#     print(soup.prettify)


def main():
    post_match_scrape('https://www.scoreboard.com/en/match/O8bBVnn7') # Use US Open 2020 men's finals as test

main()