from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, WebDriverException, TimeoutException)
import os
from datetime import datetime
import re
from flask import current_app
from time import sleep

# CONSTANTS for the Common Pleas site #
COMMON_PLEAS_URL = "https://ujsportal.pacourts.us/DocketSheets/CP.aspx"
SEARCH_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$cphDynamicContent$searchTypeListControl")


class DocketSearch:
    """Selectors for searching for a single Docket"""
    # Dropdown to indicate if docket is CP or MC
    COURT_TYPE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
        "$cphDynamicContent$docketNumberCriteriaControl" +
        "$docketNumberControl$mddlCourt")

    COUNTY_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
        "$cphDynamicContent$docketNumberCriteriaControl" +
        "$docketNumberControl$mtxtCounty")

    # Dropdown when searching for a spsecific Docket to identify
    # the type of docket (CR, MD, etc.)
    DOCKET_TYPE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$docketNumberCriteriaControl$docketNumberControl$mddlDocketType"
    )

    DOCKET_INDEX_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$docketNumberCriteriaControl$docketNumberControl$mtxtSequenceNumber"
    )

    YEAR_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$docketNumberCriteriaControl$docketNumberControl$mtxtYear"
    )

    SEARCH_BUTTON = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$docketNumberCriteriaControl$searchCommandControl"
    )

    # id
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cph" +
        "DynamicContent_docketNumberCriteriaControl_searchResultsGrid" +
        "Control_resultsPanel"
    )

    # id
    NO_SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cph" +
        "DynamicContent_docketNumberCriteriaControl_searchResultsGrid" +
        "Control_noResultsPanel"
    )

    # xpath
    NO_RESULTS_FOUND = (
        "//td[contains(text(), 'No Cases Found')]"
    )


class NameSearch:
    """Selectors for searching for a single Docket"""

    LAST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$lastNameControl"
    )

    FIRST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$firstNameControl"
    )

    DOB_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateOfBirthControl$DateTextBox"
    )

    # Docket type when searching by a person's name.
    DOCKET_TYPE_SELECT = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphDynamicContent" +
        "_participantCriteriaControl_docketTypeListControl"
    )

    SEARCH_BUTTON = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphDynamicContent" +
        "_participantCriteriaControl_searchCommandControl"
    )

    # id
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphDynamicContent" +
        "_participantCriteriaControl_searchResultsGridControl_resultsPanel"
    )

    # xpath
    NO_RESULTS_FOUND = (
        "//td[contains(text(), 'No Cases Found')]"
    )

    # name
    CASE_STATUS_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$caseStatusListControl"
    )

    # name
    # This one is only used in order to TAB into the Date Filed To input box.
    # The tabbing is necessary to trigger the javascript on that box.
    CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateFiledControl$beginDateChildControl" +
        "$ToggleImage"
    )

    # name
    DATE_FILED_FROM_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateFiledControl$" +
        "beginDateChildControl$DateTextBox"
    )

    # value that will be entered into the FROM date.
    DATE_FILED_FROM = "01/01/1950"

    # name
    DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphDynamicContent" +
        "$participantCriteriaControl$dateFiledControl$endDateChildControl" +
        "$DateTextBox")


class SEARCH_TYPES:
    docket_number = "Docket Number"
    participant_name = "Participant Name"




# Helper functions #


def parse_docket_number(docket_number):
    """ Parse a Common Pleas docket number into its components.

    A docket number has the form "CP-46-CR-1234567-2019"
    This method takes a docket number as a string and
    returns a dictionary with the different parts as keys
    """
    patt = re.compile(
        "(?P<court>[A-Z]{2})-(?P<county>[0-9]{2})-" +
        "(?P<docket_type>[A-Z]{2})-(?P<docket_index>[0-9]{7})-" +
        "(?P<year>[0-9]{4})")
    match = patt.match(docket_number)
    if match is None:
        return None
    else:
        return match.groupdict()


def ss(driver, image_name="cp.png"):
    """ helper for taking a screenshot

    Only for debugging

    TODO: remove before production

    """
    driver.save_screenshot(
        os.path.join(os.getcwd(), "screenshots", image_name))


def get_current_active_page(driver):
    """When a page's search results have multiple pages, return the number of
       the currently loaded page."""
    return int(driver.find_element_by_xpath(
        "//span[@id='ctl00_ctl00_ctl00_cphMain_cphDynamicContent_" +
        "cphDynamicContent_participantCriteriaControl_" +
        "searchResultsGridControl_casePager']/" +
        "div/a[@style='text-decoration:none;']"
    ).text)


def parse_docket_search_results(search_results):
    """ Given a table of docket search results, return a list of dicts of key
    information
    """

    """
    docket_numbers = search_results.find_elements_by_xpath(
        "//span[contains(@id, 'docketNumberLabel')]")
    # docket_sheet_urls = search_results.find_elements_by_xpath(
    #     "//td/a[contains(text(), 'Docket Sheet')]")
    # summary_urls = search_results.find_elements_by_xpath(
    #     "//td/a[contains(text(), 'Court Summary')]")
    captions = search_results.find_elements_by_xpath(
        "//span[contains(@id, 'shortCaptionLabel')]")
    case_statuses = search_results.find_elements_by_xpath(
        "//span[contains(@id, 'caseStatusNameLabel')]")
    otns = search_results.find_elements_by_xpath(
            "//span[contains(@id, 'otnLabel')]")
    dobs = search_results.find_elements_by_xpath(
        "//span[contains(@id, 'DobLabel')]")
    """

    docket_numbers = search_results.find_elements_by_xpath(
        ".//td[2]")
    captions = search_results.find_elements_by_xpath(
        ".//td[3]")
    xfiling_dates = search_results.find_elements_by_xpath(
        ".//td[4]")
    xcounties = search_results.find_elements_by_xpath(
        ".//td[5]")
    xparties = search_results.find_elements_by_xpath(
        ".//td[6]")
    case_statuses = search_results.find_elements_by_xpath(
        ".//td[7]")
    otns = search_results.find_elements_by_xpath(
        ".//td[8]")
    xlotns = search_results.find_elements_by_xpath(
        ".//td[9]")
    xincident_numbers = search_results.find_elements_by_xpath(
        ".//td[10]")
    dobs = search_results.find_elements_by_xpath(
        ".//td[11]"
    )

    docket_sheet_urls = []
    for docket in docket_numbers:
        try:
            docket_sheet_url = search_results.find_element_by_xpath(
                (".//tr[td/span[contains(text(), '{}')]]//" +
                 "a[contains(text(), 'Docket Sheet')]").format(docket.text)
            ).get_attribute("href")
        except NoSuchElementException:
            try:
                docket_sheet_url = search_results.find_element_by_xpath(
                    (".//tr[td/span[contains(text(), '{}')]]//" +
                     "a[contains(@href, 'docketNumber')]").format(docket)
                ).get_attribute("href")
            except NoSuchElementException:
                docket_sheet_url = "Docket Sheet url not found"
        finally:
            docket_sheet_urls.append(docket_sheet_url)

    summary_urls = []
    for docket in docket_numbers:
        try:
            summary_url = search_results.find_element_by_xpath(
                (".//tr[td/span[contains(text(), '{}')]]//" +
                 "a[contains(text(), 'Court Summary')]").format(docket.text)
            ).get_attribute("href")
        except NoSuchElementException:
            summary_url = "Summary URL not found"
        finally:
            summary_urls.append(summary_url)

    # check that the length of all these lists is the same, so that
    # they get zipped up properly.
    assert len(set(map(len, (
        docket_numbers, docket_sheet_urls, summary_urls,
        captions, case_statuses, dobs)))) == 1

    """
    dockets = [
        {
            "docket_number": dn.text,
            "docket_sheet_url": ds,
            "summary_url": su,
            "caption": cp.text,
            "case_status": cs.text,
            "otn": otn.text,
            "dob": dob.text,
        }
        for dn, ds, su, cp, cs, otn, dob in zip(
            docket_numbers,
            docket_sheet_urls,
            summary_urls,
            captions,
            case_statuses,
            otns,
            dobs
        )
    ]
    """
    dockets = [
        {
            "docket_number": dn.text,
            "docket_sheet_url": ds,
            "summary_url": su,
            "caption": cp.text,
            "filing_date": fd.text,
            "county": c.text,
            "case_status": cs.text,
            "party": p.text,
            "otn": otn.text,
            "lotn": l.text,
            "incident_number": i.text,
            "dob": dob.text
        }
        for dn, ds, su, cp, fd, c, cs, p, otn, l, i, dob in zip(
            docket_numbers,
            docket_sheet_urls,
            summary_urls,
            captions,
            xfiling_dates,
            xcounties,
            case_statuses,
            xparties,
            otns,
            xlotns,
            xincident_numbers,
            dobs,
        )
    ]
    return dockets


def next_button_enabled(driver):
    try:
        el = driver.find_element_by_xpath(
            "//a[contains(@href, 'casePager') and contains(text(), 'Next')]")
        return True if el.is_enabled() else False
    except NoSuchElementException:
        return False


def get_next_button(driver):
    return driver.find_element_by_xpath(
        "//a[contains(@href, 'casePager') and contains(text(), 'Next')]")


class CommonPleas:

    @staticmethod
    def searchName(
            first_name, last_name, driver, dob=None, date_format="%m/%d/%Y"):
        """
        Search the Common Pleas site for criminal records of a person

        Args:
            first_name (str): A person's first name
            last_name (str): A person's last name
            dob (str): Optional. A person's data of birth, in YYYY-MM-DD
            date_format (str): Optional. Format for parsing `dob`. Default
                is "%Y-%m-%d"
        """
        if dob:
            try:
                dob = datetime.strptime(dob, date_format)
            except ValueError:
                current_app.logger.error("Unable to parse date.")
                return {"status": "Error: check your date format"}

        current_app.logger.info("Searching by Name for Common Pleas dockets")
        driver.get(COMMON_PLEAS_URL)

        # Choose to search by Name
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(
            SEARCH_TYPES.participant_name)

        # Wait for the name fields to appear
        try:
            last_name_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.NAME, NameSearch.LAST_NAME_INPUT))
            )
        except AssertionError:
            current_app.logger.error("Name Search Fields not found.")
            return {"status": "Error: Name search fields not found"}

        # Fill in name fields
        last_name_input.clear()
        last_name_input.send_keys(last_name)

        first_name_input = driver.find_element_by_name(
            NameSearch.FIRST_NAME_INPUT)
        first_name_input.clear()
        first_name_input.send_keys(first_name)

        first_name_input.send_keys(Keys.TAB)
        if dob:

            dob_input = driver.find_element_by_name(
                NameSearch.DOB_INPUT
            )
            dob_string = dob.strftime("%m%d%Y")
            dob_input.send_keys(dob_string)
            dob_input.send_keys(Keys.TAB)

        date_filed_from_input = driver.find_element_by_name(
            NameSearch.DATE_FILED_FROM_INPUT)
        driver.execute_script("""
            arguments[0].focus()
            arguments[0].value = arguments[1]
            arguments[0].blur()
        """, date_filed_from_input, NameSearch.DATE_FILED_FROM)

        calendar_box = driver.find_element_by_name(
            NameSearch.CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT)
        calendar_box.send_keys(
                Keys.TAB)

        date_filed_to_input = driver.find_element_by_name(
            NameSearch.DATE_FILED_TO_INPUT)
        date_filed_to_input.send_keys(datetime.today().strftime("%m%d%Y"))

        # Execute search
        search_button = driver.find_element_by_id(NameSearch.SEARCH_BUTTON)
        search_button.click()

        # Process results.
        try:
            results_xpath = "//*[@id='{}'] | {}".format(
                NameSearch.SEARCH_RESULTS_TABLE,
                NameSearch.NO_RESULTS_FOUND
            )
            search_results = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, results_xpath)
                    )
            )
        except TimeoutException:
            return {"status": "Error: Could not find search results."}

        if "No Cases Found" in search_results.text:
            return {"status": "No Dockets Found"}
        final_results = parse_docket_search_results(search_results)
        while next_button_enabled(driver) and dob:
            current_active_page = get_current_active_page(driver)
            next_active_page_xpath = (
                "//span[@id='ctl00_ctl00_ctl00_cphMain_cphDynamicContent" +
                "_cphDynamicContent_participantCriteriaControl_" +
                "searchResultsGridControl_casePager']" +
                "/div/a[@style='text-decoration:none;' and" +
                " contains(text(), '{}')]"
            ).format(current_active_page + 1)

            # click the next button to get the next page of results
            get_next_button(driver).click()

            # wait until the next page number is activated, so we know
            # that the next results have loaded.
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, next_active_page_xpath)
                )
            )

            # Get the results from this next page.

            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.ID, NameSearch.SEARCH_RESULTS_TABLE))
            )
            final_results.extend(parse_docket_search_results(search_results))

        current_app.logger.info(
            "Completed Name Search for Common Pleas Dockets.")
        current_app.logger.info("Found {} dockets.".format(len(final_results)))

        return {"status": "success",
                "dockets": final_results}

    @staticmethod
    def lookupDocket(docket_number, driver):
        """
        Lookup information about a single docket

        If the search somehow returns more than one docket given the
        docket_number, the search will return just the first docket.

        Args:
            docket_number (str): Docket number like CP-45-CR-1234567-2019
        """
        current_app.logger.info(
            "Searching by docket number for common pleas docket")
        docket_dict = parse_docket_number(docket_number)
        if docket_dict is None:
            current_app.logger.info("Caught malformed docket number.")
            return {"status": "Error. Malformed docket number."}
        driver.get(COMMON_PLEAS_URL)
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SEARCH_TYPES.docket_number)

        # Fill in docket information
        court_select = Select(
            driver.find_element_by_name(DocketSearch.COURT_TYPE_SELECT)
        )
        court_select.select_by_visible_text(docket_dict["court"])

        county_input = driver.find_element_by_name(DocketSearch.COUNTY_INPUT)
        county_input.send_keys(docket_dict["county"])

        docket_type_select = Select(
            driver.find_element_by_name(DocketSearch.DOCKET_TYPE_SELECT)
        )
        docket_type_select.select_by_visible_text(docket_dict["docket_type"])

        docket_index_input = driver.find_element_by_name(
            DocketSearch.DOCKET_INDEX_INPUT)
        docket_index_input.send_keys(docket_dict["docket_index"])

        year_input = driver.find_element_by_name(DocketSearch.YEAR_INPUT)
        year_input.clear()
        year_input.send_keys(docket_dict["year"])

        search_button = driver.find_element_by_name(DocketSearch.SEARCH_BUTTON)
        search_button.click()

        # Wait for results
        try:
            search_xpath = "//*[@id='{}'] | {}".format(
                DocketSearch.SEARCH_RESULTS_TABLE,
                DocketSearch.NO_RESULTS_FOUND
            )
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, search_xpath))
            )

            if "No Cases Found" in search_results.text:
                return {"status": "No Dockets Found"}

        # Collect results
            response = parse_docket_search_results(search_results)
            if len(response) != 1:
                current_app.logger.warning(
                    "While searching for {}, ".format(docket_number)
                )
                current_app.logger.warning(
                    "I found {} dockets, instead of 1.".format(len(response)))
            response = response[0]
        except TimeoutException:
            return {"status": "no dockets found"}

        current_app.logger.info("Completed search for common pleas docket.")
        return {"status": "success",
                "docket": response}

    @staticmethod
    def lookupMultipleDockets(docket_nums, driver):
        """ Lookup multiple dockets

        Args:
            docket_nums (str[]): list of docket numbers as strings """

        if len(docket_nums) == 0:
            return []
        results = []
        for docket_num in docket_nums:
            docket_lookup = CommonPleas.lookupDocket(docket_num, driver=driver)
            if docket_lookup["status"] == "success":
                results.append(docket_lookup["docket"])
        return results

    @staticmethod
    def lookupMultipleDocketsEfficiently(docket_nums, driver):
        """
        Lookup information about a single docket

        If the search somehow returns more than one docket given the
        docket_number, the search will return just the first docket.

        Args:
            docket_number (str): Docket number like CP-45-CR-1234567-2019
        """
        results = {}

        docket_number = docket_nums[1]

        driver.get(COMMON_PLEAS_URL)

        # Don't need to wait for anything to load, docket number is the default
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SEARCH_TYPES.docket_number)

        current_app.logger.info(
            "Searching by docket number for common pleas docket")

        remove_results_js = """
var element = document.querySelector("#{}");
if (element)
    element.parentNode.removeChild(element);
""".format(DocketSearch.SEARCH_RESULTS_TABLE)

        remove_no_results_js = """
var element = document.querySelector("#{}");
if (element)
    element.parentNode.removeChild(element);
""".format(DocketSearch.NO_SEARCH_RESULTS_TABLE)

        #current_app.logger.error(remove_results_js)

        #current_app.logger.error(remove_no_results_js)

        for docket_number in docket_nums:

            current_app.logger.info("Checking docket: {}".format(docket_number))

            # Delete results if exists
            driver.execute_script(remove_results_js)

            # Delete no-results if exists
            driver.execute_script(remove_no_results_js)

            docket_dict = parse_docket_number(docket_number)

            #current_app.logger.error(str(docket_dict))

            if docket_dict is None:
                current_app.logger.error("Caught malformed docket number: {}".format(docket_number))
                results[docket_number] = {"error": "Error. Malformed docket number: {}".format(docket_number)}
                continue

            # Fill in docket information
            try:
                court_select = Select(
                    driver.find_element_by_name(DocketSearch.COURT_TYPE_SELECT)
                )
                court_select.select_by_visible_text(docket_dict["court"])
            except Exception as e:
                results[docket_number] = {"error": "Error. Invalid court type in docket number: {}".format(docket_number)}
                continue

            county_input = driver.find_element_by_name(DocketSearch.COUNTY_INPUT)
            county_input.clear()
            county_input.send_keys(docket_dict["county"])

            try:
                docket_type_select = Select(
                    driver.find_element_by_name(DocketSearch.DOCKET_TYPE_SELECT)
                )
                docket_type_select.select_by_visible_text(docket_dict["docket_type"])
            except Exception as e:
                results[docket_number] = {"error": "Error. Invalid docket type in docket number: {}".format(docket_number)}
                continue

            docket_index_input = driver.find_element_by_name(
                DocketSearch.DOCKET_INDEX_INPUT)
            docket_index_input.clear()
            docket_index_input.send_keys(docket_dict["docket_index"])

            year_input = driver.find_element_by_name(DocketSearch.YEAR_INPUT)
            year_input.clear()
            year_input.send_keys(docket_dict["year"])

            search_button = driver.find_element_by_name(DocketSearch.SEARCH_BUTTON)
            search_button.click()

            # Delete

            # Wait for results
            try:
                search_xpath = "//*[@id='{}'] | {}".format(
                    DocketSearch.SEARCH_RESULTS_TABLE,
                    DocketSearch.NO_RESULTS_FOUND
                )
                search_results = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.XPATH, search_xpath))
                )

                if "No Cases Found" in search_results.text:
                    results[docket_number] = {"error": "No Dockets Found for: {}".format(docket_number)}
                    continue

                # Collect results
                response = parse_docket_search_results(search_results)
                if len(response) != 1:
                    current_app.logger.warning(
                        "While searching for {}, ".format(docket_number)
                    )
                    current_app.logger.warning(
                        "I found {} dockets, instead of 1.".format(len(response)))
                response_dict = response[0]
            except TimeoutException:
                results[docket_number] = {"error": "Timeout when searching for: {}".format(docket_number)}
                continue

            results[docket_number] = response_dict

            sleep(0.2)

        current_app.logger.info("Completed search for common pleas docket.")
        return results
