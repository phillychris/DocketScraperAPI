"""
Class and constants for looking up docket information from
the Pennsylvania Majesterial District Courts
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException, WebDriverException, TimeoutException)
from selenium.webdriver.support import expected_conditions as EC
import csv
from flask import current_app
from datetime import datetime
import re


# Constants for MDJ Searches #
MDJ_URL = "https://ujsportal.pacourts.us/DocketSheets/MDJ.aspx"

# name ctl00$ctl00$ctl00$cphMain$cphDynamicContent$ddlSearchType
SEARCH_TYPE_SELECT = (
    "ctl00$ctl00$ctl00$cphMain$cphDynamicContent" +
    "$ddlSearchType")


class SearchTypes:
    """Different types of searches on the MDJ site"""
    # visible text of select
    DOCKET_NUMBER = "Docket Number"

    # visible text of select
    PARTICIPANT_NAME = "Participant Name"

    # visible text of select
    DATE_FILED = "Date Filed"

    # Currently unused:
    """
	Citation Number
	Organization
	OTN
	Parcel
	Police Incident/Complaint Number
	SID
    """



class DocketSearch:
    """Constants for searching for a single  docket."""
    # name
    COUNTY_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDocketNumber$ddlCounty"
    )

    # name
    COURT_OFFICE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDocketNumber$ddlCourtOffice"
    )

    # name
    DOCKET_TYPE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsDocketNumber$ddlDocketType"
    )

    # name
    DOCKET_INDEX_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsDocketNumber$txtSequenceNumber"
    )

    # name
    YEAR_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsDocketNumber$txtYear"
    )

    # name
    SEARCH_BUTTON = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch"
    )

    # id
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket"
    )

    # xpath
    NO_RESULTS_FOUND = "//td[contains(text(), 'No Records Found')]"


class NameSearch:
    """ Constants for searching MDJ dockets by name """

    # name
    LAST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$txtLastName"
    )

    # name
    FIRST_NAME_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$txtFirstName"
    )

    # name
    DOB_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsParticipantName$dpDOB$DateTextBox"
    )

    # name
    DATE_FILED_FROM_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$DateFiledDateRangePicker$beginDateChildControl" +
        "$DateTextBox"
    )

    # name
    DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$DateFiledDateRangePicker$endDateChildControl" +
        "$DateTextBox"
    )

    # name
    CASE_STATUS_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$ddlCaseStatus"
    )

    # name
    CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls" +
        "$udsParticipantName$DateFiledDateRangePicker$beginDateChild" +
        "Control$ToggleImage"
    )

    # name
    SEARCH_BUTTON = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch"
    )

    # id
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket"
    )

    # xpath
    NO_RESULTS_FOUND = "//td[contains(text(), 'No Records Found')]"

    # value
    DATE_FILED_FROM = "01/01/1950"


class DateSearch:
    """ Constants for searching MDJ dockets by name """

    # county ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$ddlCounty
    COUNTY_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDateFiled$ddlCounty"
    )

    # court office ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$ddlCourtOffice
    COURT_OFFICE_SELECT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDateFiled$ddlCourtOffice"
    )

    # date from ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$drpFiled$beginDateChildControl$DateTextBox
    DATE_FILED_FROM_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDateFiled$drpFiled$beginDateChildControl$DateTextBox"
    )

    # date to ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$drpFiled$endDateChildControl$DateTextBox
    DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDateFiled$drpFiled$endDateChildControl$DateTextBox"
    )

    # calendar to ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$udsDateFiled$drpFiled$beginDateChildControl$ToggleImage
    CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$cphSearchControls$" +
        "udsDateFiled$drpFiled$beginDateChildControl$ToggleImage"
    )

    # name ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch
    SEARCH_BUTTON = (
        "ctl00$ctl00$ctl00$cphMain$cphDynamicContent$btnSearch"
    )

    # id ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket
    SEARCH_RESULTS_TABLE = (
        "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphResults_gvDocket"
    )

    # xpath
    NO_RESULTS_FOUND = "//td[contains(text(), 'No Records Found')]"


# Helper functions #


def parse_docket_number(docket_str):
    """ Parse a string representation of a MDJ docket number into
    component parts.

    Args:
        docket_str (str): MDJ Docket number as a string

    Returns:
        Dict of parts of an MDJ Docket number
    """
    patt = re.compile(
        "(?P<court>[A-Z]{2})-(?P<county_code>[0-9]{2})" +
        "(?P<office_code>[0-9]{3})-" +
        "(?P<docket_type>[A-Z]{2})-(?P<docket_index>[0-9]{7})-" +
        "(?P<year>[0-9]{4})")
    match = patt.match(docket_str)
    if match is None:
        return None
    else:
        return match.groupdict()


def next_button_enabled(driver):
    """ Return true if there is an enabled "Next" link on the page.

    The "Next" link, if enabled, indicates there are more pages of results
    to parse for a searche

    """
    try:
        el = driver.find_element_by_xpath(
            "//a[contains(@href, 'cstPager') and contains(text(), 'Next')]")
        return True if el.is_enabled() else False
    except NoSuchElementException:
        return False


def get_next_button(driver):
    return driver.find_element_by_xpath(
        "//a[contains(@href, 'cstPager') and contains(text(), 'Next')]")


def get_current_active_page(driver):
    """When a page's search results have multiple pages, return the number of
       the currently loaded page."""
    return int(driver.find_element_by_xpath(
        "//span[@id='ctl00_ctl00_ctl00_cphMain_cphDynamicContent" +
        "_cstPager']/div/a[@style='text-decoration:none;']"
    ).text)


def lookup_county(county_code, office_code):
    """ Maps county numbers from a docket number (41, 20, etc.) to county
    names.


    The MDJ Docket search requires a user to select the name of the county
    to search. We can get the name of the county from a Docket Number, but it
    is not straightforward.

    MDJ Docket numbers start with "MDJ-012345". The five digits are a
    county code and an office code. Some counties share the same code, so the
    name of a county depends on all five of these digits.

    This method uses a reference table to match the county and office codes
    to the correct county's name.

    Args:
        county_code (str): Two-digit code that (usually) identifies a county.
        office_code (str): Three more digits that are sometimes necessary to
        identify a county, when two counties share the same county code.

    Returns:
        The name of a county, or None, if no match was found. Raise an
        AssertionError if multiple matches were found, because then something
        is wrong with the reference table.

    """
    full_five_digits = "{}{}".format(county_code, office_code)
    with open("references/county_lookup.csv", "r") as f:
        reader = csv.DictReader(f)
        matches = []
        for row in reader:
            if re.match(row["regex"], full_five_digits):
                matches.append(row["County"])
    assert len(matches) <= 1, "Error: Found multiple matches for {}".format(
        full_five_digits)
    if len(matches) == 0:
        return None
    return matches[0]


def parse_docket_search_results(search_results):
    """ Given a table of docket search results, return a list of dicts of key
    information
    """
    docket_numbers = search_results.find_elements_by_xpath(
        ".//td[2]")
    xcourt_offices = search_results.find_elements_by_xpath(
        ".//td[3]")
    captions = search_results.find_elements_by_xpath(
        ".//td[4]")
    xfiling_dates = search_results.find_elements_by_xpath(
        ".//td[5]")
    xcounties = search_results.find_elements_by_xpath(
        ".//td[6]")
    case_statuses = search_results.find_elements_by_xpath(
        ".//td[7]")
    xparticipants = search_results.find_elements_by_xpath(
        ".//td[8]")
    otns = search_results.find_elements_by_xpath(
        ".//td[9]")
    xlotns = search_results.find_elements_by_xpath(
        ".//td[10]")
    xincident_numbers = search_results.find_elements_by_xpath(
        ".//td[11]")
    dobs = search_results.find_elements_by_xpath(
        ".//td[12]"
    )

    docket_sheet_urls = []
    for docket in docket_numbers:
        try:
            docket_sheet_url = search_results.find_element_by_xpath(
                (".//tr[td[contains(text(), '{}')]]//" +
                 "a[contains(text(), 'Docket Sheet')]").format(docket.text)
            ).get_attribute("href")
        except NoSuchElementException:
            try:
                docket_sheet_url = search_results.find_element_by_xpath(
                    (".//tr[td[contains(text(), '{}')]]//" +
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
                (".//tr[td[contains(text(), '{}')]]//" +
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
        captions, case_statuses)))) == 1

    dockets = [
        {
            "docket_number": dn.text,
            "docket_sheet_url": ds,
            "summary_url": su,
            "court_office": co.text,
            "caption": cp.text,
            "filing_date": fd.text,
            "county": c.text,
            "case_status": cs.text,
            "participant": p.text,
            "otn": otn.text,
            "lotn": l.text,
            "incident_number": i.text,
            "dob": dob.text
        }
        for dn, ds, su, co, cp, fd, c, cs, p, otn, l, i, dob in zip(
            docket_numbers,
            docket_sheet_urls,
            summary_urls,
            xcourt_offices,
            captions,
            xfiling_dates,
            xcounties,
            case_statuses,
            xparticipants,
            otns,
            xlotns,
            xincident_numbers,
            dobs,
        )
    ]
    return dockets


class MDJ:
    """ Class for searching for dockets in Majesterial District courts
    """

    @staticmethod
    def searchName(
            first_name, last_name, driver, dob=None, date_format="%m/%d/%Y"):
        """
        Search the MDJ site for criminal records of a person

        Args:
            first_name (str): A person's first name
            last_name (str): A person's last name
            dob (str): Optional. A person's data of birth, in YYYY-MM-DD
            date_format (str): Optional. Format for parsing `dob`. Default
                is "%Y-%m-%d"
        """
        current_app.logger.info("Searching by name for MDJ dockets")
        if dob:
            try:
                dob = datetime.strptime(dob, date_format)
            except ValueError:
                current_app.logger.error("Unable to parse date")
                return {"status": "Error: check your date format"}
        driver.get(MDJ_URL)

        # Select the Name search
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SearchTypes.PARTICIPANT_NAME)

        # Enter a name to search and execute the search
        try:
            last_name_input = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.NAME, NameSearch.LAST_NAME_INPUT)
                )
            )
        except AssertionError:
            current_app.logger.error("Name Seaerch Fields not found.")
            return {"status": "Error: Name search fields not found"}

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

        driver.find_element_by_name(
            NameSearch.CASE_STATUS_SELECT).send_keys(Keys.TAB)

        date_filed_from_input = driver.find_element_by_name(
            NameSearch.DATE_FILED_FROM_INPUT)
        driver.execute_script("""
            arguments[0].focus()
            arguments[0].value = arguments[1]
            arguments[0].blur()
        """, date_filed_from_input, NameSearch.DATE_FILED_FROM)

        driver.find_element_by_name(
            NameSearch.CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT).send_keys(
                Keys.TAB)

        date_filed_to_input = driver.find_element_by_name(
            NameSearch.DATE_FILED_TO_INPUT)
        date_filed_to_input.send_keys(datetime.today().strftime("%m%d%Y"))

        # Execute search
        search_button = driver.find_element_by_name(NameSearch.SEARCH_BUTTON)
        search_button.click()

        # Process results.
        try:
            search_xpath = ("//*[@id='{}'] | {}".format(
                NameSearch.SEARCH_RESULTS_TABLE,
                NameSearch.NO_RESULTS_FOUND
            ))
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, search_xpath))
            )
        except AssertionError:
            return {"status": "Error: Could not find search results."}

        if "No Records Found" in search_results.text:
            return {"status": "No Dockets Found"}

        final_results = parse_docket_search_results(search_results)

        while next_button_enabled(driver) and dob:
            current_active_page = get_current_active_page(driver)
            next_active_page_xpath = (
                "//span[@id='ctl00_ctl00_ctl00_cphMain_cphDynamicContent" +
                "_cstPager']/div/a[@style='text-decoration:none;' and" +
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

        current_app.logger.info("Completed searching by name for MDJ Dockets")
        current_app.logger.info("found {} dockets".format(len(final_results)))
        return {"status": "success",
                "dockets": final_results}


    @staticmethod
    def searchByDate(
            county, court_office, start_date, end_date, driver, date_format="%m/%d/%Y"):
        """
        Search the MDJ site for criminal records by county, office, and dates

        Args:
            county (str): County in PA
            court_office (str): An office in the provided county
            start_date (str): Start date for search, in YYYY-MM-DD
            end_date (str): Start date for search, in YYYY-MM-DD
            date_format (str): Optional. Format for parsing `start_date` and
                `end_date`. Default is "%Y-%m-%d"
        """
        #current_app.logger.info("Searching by county, office, and date for MDJ dockets")
        #current_app.logger.error("Starting searchByDate")

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            current_app.logger.error("Unable to parse start_date")
            return {"status": "Error: check your start_date format"}

        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            current_app.logger.error("Unable to parse end_date")
            return {"status": "Error: check your end_date format"}

        driver.get(MDJ_URL)

        # Select the Date Filed search
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SearchTypes.DATE_FILED)


        # Enter a county to search and execute the search
        try:
            county_select = Select(WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.NAME, DateSearch.COUNTY_SELECT)
                )
            ))
        except AssertionError:
            current_app.logger.error("County Select not found.")
            return {"status": "Error: County Select not found"}

        #print(county_select)
        #current_app.logger.error(dir(county_select))
        #print(dir(county_select))

        county_select.select_by_visible_text(county)

        #current_app.logger.error('type(court_office): '+ str(type(court_office)))

        # Enter a court_office to search and execute the search
        try:
            office_select = Select(WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.NAME, DateSearch.COURT_OFFICE_SELECT)
                )
            ))
        except AssertionError:
            current_app.logger.error("Court Office not found.")
            return {"status": "Error: Court Office not found"}

        #current_app.logger.error(dir(office_select))

        office_select.select_by_value(court_office)

        """ This isn't working, leaving value as '__/__/____'
        date_filed_from_input = driver.find_element_by_name(
            DateSearch.DATE_FILED_FROM_INPUT)
        date_filed_from_input.send_keys(start_date.strftime("%m%d%Y"))
        date_filed_from_input.send_keys(Keys.TAB)
        """

        date_filed_from_input = driver.find_element_by_name(
            DateSearch.DATE_FILED_FROM_INPUT)
        driver.execute_script("""
            arguments[0].focus()
            arguments[0].value = arguments[1]
            arguments[0].blur()
        """, date_filed_from_input, start_date.strftime("%m/%d/%Y"))


        current_app.logger.error('start_date_set: '+ start_date.strftime("%m%d%Y"))

        driver.find_element_by_name(
            DateSearch.CALENDAR_TOGGLE_BEFORE_DATE_FILED_TO_INPUT).send_keys(
                Keys.TAB)

        date_filed_to_input = driver.find_element_by_name(
            DateSearch.DATE_FILED_TO_INPUT)
        date_filed_to_input.send_keys(end_date.strftime("%m%d%Y"))
        date_filed_to_input.send_keys(Keys.TAB)

        current_app.logger.error('end date set: '+ end_date.strftime("%m%d%Y"))

        # Execute search
        search_button = driver.find_element_by_name(DateSearch.SEARCH_BUTTON)
        search_button.click()

        current_app.logger.error('search button clicked.')

        # Process results.
        try:
            current_app.logger.error("starting at: "+ str(datetime.now()))
            search_xpath = ("//*[@id='{}'] | {}".format(
                DateSearch.SEARCH_RESULTS_TABLE,
                DateSearch.NO_RESULTS_FOUND
            ))
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, search_xpath))
            )
            current_app.logger.error("ending at: "+ str(datetime.now()))
        except Exception as e:
            current_app.logger.error("Exception in search results")
            current_app.logger.error(e)

            error_message = driver.find_element_by_id(
                "ctl00_ctl00_ctl00_cphMain_cphDynamicContent_cphSearchControls_udsDateFiled_DateRangePickerValidator1")

            current_app.logger.error("date error: "+ error_message.text)

            date_from = driver.find_element_by_name(DateSearch.DATE_FILED_FROM_INPUT)
            current_app.logger.error("date_from: "+ date_from.get_attribute('value'))

            date_to = driver.find_element_by_name(DateSearch.DATE_FILED_TO_INPUT)
            current_app.logger.error("date_to: "+ date_to.get_attribute('value'))

            current_app.logger.error("search_xpath: "+ search_xpath)

            return {"status": "Unknown Error."}
        except AssertionError:
            return {"status": "Error: Could not find search results."}

        #current_app.logger.error('search_results: '+ search_results.text)

        if "No Records Found" in search_results.text:
            return {"status": "No Dockets Found"}

        final_results = parse_docket_search_results(search_results)

        #current_app.logger.error('final_results: '+ final_results)

        while next_button_enabled(driver):
            current_active_page = get_current_active_page(driver)
            current_app.logger.error('current_active_page: '+ str(current_active_page))
            #current_app.logger.error(final_results)
            next_active_page_xpath = (
                "//span[@id='ctl00_ctl00_ctl00_cphMain_cphDynamicContent" +
                "_cstPager']/div/a[@style='text-decoration:none;' and" +
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
                    (By.ID, DateSearch.SEARCH_RESULTS_TABLE))
            )

            final_results.extend(parse_docket_search_results(search_results))

        current_app.logger.info("Completed searching by name for MDJ Dockets")
        current_app.logger.info("found {} dockets".format(len(final_results)))
        return {"status": "success",
                "dockets": final_results}


    @staticmethod
    def getCourtOffices(
            county, driver, date_format="%m/%d/%Y"):
        """
        Search the MDJ site for criminal records by county, office, and dates

        Args:
            county (str): County in PA
            date_format (str): Optional. Format for parsing `dob`. Default
                is "%Y-%m-%d"
        """

        driver.get(MDJ_URL)

        # Select the Date Filed search
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SearchTypes.DATE_FILED)


        # Enter a county to search and execute the search
        try:
            county_select = Select(WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.NAME, DateSearch.COUNTY_SELECT)
                )
            ))
        except AssertionError:
            current_app.logger.error("County Select not found.")
            return {"status": "Error: County Select not found"}

        #print(county_select)
        #current_app.logger.error(dir(county_select))
        #print(dir(county_select))

        county_select.select_by_visible_text(county)

        #current_app.logger.error('type(court_office): '+ str(type(court_office)))

        # Enter a court_office to search and execute the search
        try:
            office_select = Select(WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (By.NAME, DateSearch.COURT_OFFICE_SELECT)
                )
            ))
        except AssertionError:
            current_app.logger.error("Court Office not found.")
            return {"status": "Error: Court Office not found"}

        #date_to = driver.find_element_by_name(DateSearch.DATE_FILED_TO_INPUT)
        #current_app.logger.error("office_select: "+ office_select.options)
        offices = {}
        for o in office_select.options:
            #current_app.logger.error(dir(o))
            #break
            if o.get_attribute('value') != '':
                #current_app.logger.error(o.get_attribute('value')+': '+o.text)
                offices[o.get_attribute('value')] = o.text

        #current_app.logger.error(dir(office_select))

        current_app.logger.info("Got Court Offices for {} County".format(county))
        current_app.logger.info("found {} offices".format(len(offices)))
        return {"status": "success", "offices": offices}



    @staticmethod
    def lookupDocket(docket_number, driver):
        """
        Lookup information about a single docket in the MDJ courts

        If the search somehow returns more than one docket given the
        docket_number, the search will return just the first docket.

        Args:
            docket_number (str): Docket number like CP-45-CR-1234567-2019
        """
        docket_dict = parse_docket_number(docket_number)
        if docket_dict is None:
            current_app.logger.info("Caught malformed docket number.")
            return {"status": "Error. Malformed docket number."}
        current_app.logger.info("searching by docket number for mdj dockets.")
        driver.get(MDJ_URL)
        search_type_select = Select(
            driver.find_element_by_name(SEARCH_TYPE_SELECT))
        search_type_select.select_by_visible_text(SearchTypes.DOCKET_NUMBER)

        county_name = lookup_county(
            docket_dict["county_code"], docket_dict["office_code"])

        county_select = Select(
            driver.find_element_by_name(DocketSearch.COUNTY_SELECT)
        )
        county_select.select_by_visible_text(county_name)

        office_select = Select(
            driver.find_element_by_name(DocketSearch.COURT_OFFICE_SELECT)
        )
        office_select.select_by_value("{}{}".format(
            docket_dict["county_code"], docket_dict["office_code"]
        ))

        docket_type_select = Select(
            driver.find_element_by_name(DocketSearch.DOCKET_TYPE_SELECT)
        )
        docket_type_select.select_by_visible_text(docket_dict["docket_type"])

        docket_index = driver.find_element_by_name(
            DocketSearch.DOCKET_INDEX_INPUT)
        docket_index.send_keys(docket_dict["docket_index"])

        docket_year = driver.find_element_by_name(DocketSearch.YEAR_INPUT)

        driver.execute_script("""
            arguments[0].focus();
            arguments[0].value = arguments[1];
            arguments[0].blur();
        """, docket_year, docket_dict["year"])

        search_button = driver.find_element_by_name(DocketSearch.SEARCH_BUTTON)
        search_button.click()

        # Process results.
        try:
            search_xpath = "//*[@id='{}'] | {}".format(
                DocketSearch.SEARCH_RESULTS_TABLE,
                DocketSearch.NO_RESULTS_FOUND
            )
            search_results = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, search_xpath))
            )

        except AssertionError:
            return {"status": "Error: Could not find search results."}

        if "No Records Found" in search_results.text:
            return {"status": "No Dockets Found"}

        try:
            final_results = parse_docket_search_results(search_results)
            assert len(final_results) == 1
        except AssertionError:
            return {"status": "Error: could not parse search results."}

        current_app.logger.info(
            "Completed searching by docket number for mdj dockets.")
        return {"status": "success", "docket": final_results[0]}

    @staticmethod
    def lookupMultipleDockets(docket_nums, driver):
        """ Lookup multiple dockets

        Args:
            docket_nums (str[]): list of docket numbers as strings """

        if len(docket_nums) == 0:
            return []
        results = []
        for docket_num in docket_nums:
            docket_lookup = MDJ.lookupDocket(docket_num, driver=driver)
            if docket_lookup["status"] == "success":
                results.append(docket_lookup["docket"])
        return results
