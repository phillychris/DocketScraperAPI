from flask import Flask, jsonify, request
from .SearchBot import SearchBot
from .MDJ import MDJ_URL
from .CommonPleas import COMMON_PLEAS_URL
import os
import logging


app = Flask(__name__)
if os.getenv("GUNICORN_LOGGER"):
    gunicorn_logger = logging.getLogger('gunicorn.info')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)


@app.route("/")
def index():
    app.logger.info("logging a call to /")
    return jsonify({"status": "all good"})


@app.route("/searchName", methods=["POST"], defaults={'court': None})
@app.route("/searchName/<court>", methods=["POST"])
def searchName(court):
    try:
        first_name = request.json["first_name"]
        last_name = request.json["last_name"]
    except KeyError:
        app.logger.error("Request to searchName missing parameter")
        return jsonify(
            {"status": "Error: Missing required parameter."}
        )
    dob = request.json.get("dob")
    searchbot = SearchBot()
    if court == "CP":
        return jsonify(
            searchbot.search_name(first_name, last_name, dob, court="CP"))
    elif court == "MDJ":
        return jsonify(
            searchbot.search_name(first_name, last_name, dob, court="MDJ"))
    elif court is not None:
        return jsonify(
            {"status": "Error: {} court not recognized".format(court)})
    else:
        return jsonify(
            searchbot.search_name(first_name, last_name, dob, court="both"))


@app.route("/lookupDocket/<court>", methods=["POST"])
def lookupDocket(court):
    try:
        docket_number = request.json["docket_number"]
    except KeyError:
        return jsonify(
            {"status": "Error: Missing required parameter."}
        )
    searchbot = SearchBot()
    if court in ["CP", "MDJ"]:
        return jsonify(searchbot.lookup_docket(docket_number, court))
    else:
        return jsonify(
            {"status": "Error: {} court not recognized".format(court)})


@app.route("/lookupMultipleDockets", methods=["POST"])
def lookupMany():
    """ Route for looking up many docket numbers."""
    try:
        docket_numbers = request.json["docket_numbers"]
    except KeyError:
        return jsonify(
            {"status": "Error. Missing docket_numbers parameter."}
        )
    searchbot = SearchBot()
    results = searchbot.lookup_multiple_dockets(docket_numbers)
    return jsonify({"status": "success", "dockets": results})


@app.route("/lookupMultipleCPDocketsEfficiently", methods=["POST"])
def lookupManyCP():
    """ Route for looking up many docket numbers."""
    try:
        docket_numbers = request.json["docket_numbers"]
    except KeyError:
        return jsonify(
            {"status": "Error. Missing docket_numbers parameter."}
        )
    searchbot = SearchBot()
    results = searchbot.lookup_multiple_cp_dockets_efficiently(docket_numbers)
    return jsonify({"status": "success", "dockets": results})

@app.route("/lookupMultipleMDJDocketsEfficiently", methods=["POST"])
def lookupManyMDJ():
    """ Route for looking up many docket numbers."""
    try:
        docket_numbers = request.json["docket_numbers"]
    except KeyError:
        return jsonify(
            {"status": "Error. Missing docket_numbers parameter."}
        )
    #searchbot = SearchBot()
    #results = searchbot.lookup_multiple_cp_dockets_efficiently(docket_numbers)
    #return jsonify({"status": "success", "dockets": results})
    return jsonify({"status": "not-yet-implemented", "dockets": []})


# MDJ Only for now
@app.route("/lookupByDate/<court>", methods=["POST"])
def lookupByDate(court):

    try:
        county = request.json["county"]
        court_office = request.json["court_office"]
        start_date = request.json["start_date"]
        end_date = request.json["end_date"]
    except KeyError:
        app.logger.error("Request to lookupByDate missing parameter")
        return jsonify(
            {"status": "Error: Missing required parameter."}
        )
    except Exception as e:
        app.logger.error("Error:", e)

    searchbot = SearchBot()
    return jsonify(
        searchbot.lookup_by_date(county, court_office, start_date, end_date, court))


# MDJ Only for now
@app.route("/getCourtOffices/<court>", methods=["POST"])
def getCourtOffices(court):

    #app.logger.error("In getCourtOffices")

    try:
        app.logger.error("county: "+request.json["county"])
        county = request.json["county"]
    except KeyError:
        app.logger.error("Request to lookupByDate missing parameter")
        return jsonify(
            {"status": "Error: Missing required parameter."}
        )
    except Exception as e:
        app.logger.error("Error:", e)
        return jsonify(
            {"status": "Error: {}".format(e)}
        )

    # ToDo: Make sure county is invalid

    #app.logger.error("Still in getCourtOffices")

    searchbot = SearchBot()
    return jsonify(
        searchbot.get_court_offices_by_county(county, court))


@app.route("/htmlPassthrough/<court>", methods=["GET"])
def htmlPassthrough(court):
    if court == "CP":
        url = COMMON_PLEAS_URL
    elif court == "MDJ":
        url = MDJ_URL
    elif court is not None:
        return "<h3>Error: {} is not a valid court</h3>".format(court)

    #return "<h3>URL: {}</h3>".format(url)

    searchbot = SearchBot()

    driver = searchbot.get_driver()

    driver.get(url)

    #app.logger.error(driver)

    return driver.page_source



@app.route("/<path:path>", methods=["GET", "POST"])
def catchall_route(path):
    app.logger.info("call to an invalid path")
    return jsonify({"status": "not a valid endpoint"})
