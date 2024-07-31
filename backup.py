import json
from datetime import datetime
import numpy as np
import pandas as pd
from google.oauth2 import service_account
from apiclient.discovery import build
from reports_setup import Reports
from constants import ColumnNames

# Constants
GA_API_KEYS = "config/api-keys.json"


"""### Define Procedures"""


def create_body(body, view_id, page_size=100000, page_token="0"):
    report_request = body["reportRequests"][0]
    report_request.update(
        {"viewId": view_id, "pageSize": page_size, "pageToken": page_token}
    )
    return body


def format_summary(response):
    try:
        # create row index
        try:
            row_index_names = response["reports"][0]["columnHeader"]["dimensions"]
            row_index_names = list(map(lambda x: x.split(":")[-1], row_index_names))
            row_index = [
                element["dimensions"]
                for element in response["reports"][0]["data"]["rows"]
            ]
            row_index_named = pd.MultiIndex.from_arrays(
                np.transpose(np.array(row_index)), names=np.array(row_index_names)
            )
        except:
            row_index_named = None

        # extract column names
        summary_column_names = [
            ColumnNames.get(item["name"], "")
            for item in response["reports"][0]["columnHeader"]["metricHeader"][
                "metricHeaderEntries"
            ]
        ]

        # extract table values
        summary_values = [
            element["metrics"][0]["values"]
            for element in response["reports"][0]["data"]["rows"]
        ]

        # combine. I used type 'float' because default is object, and as far as I know, all values are numeric
        df = pd.DataFrame(
            data=np.array(summary_values),
            index=row_index_named,
            columns=summary_column_names,
        ).astype("float")

    except:
        df = pd.DataFrame()

    return df


def format_pivot(response):
    try:
        # extract table values
        pivot_values = [
            item["metrics"][0]["pivotValueRegions"][0]["values"]
            for item in response["reports"][0]["data"]["rows"]
        ]

        # create column index
        top_header = [
            item["dimensionValues"]
            for item in response["reports"][0]["columnHeader"]["metricHeader"][
                "pivotHeaders"
            ][0]["pivotHeaderEntries"]
        ]
        column_metrics = [
            item["metric"]["name"]
            for item in response["reports"][0]["columnHeader"]["metricHeader"][
                "pivotHeaders"
            ][0]["pivotHeaderEntries"]
        ]
        array = np.concatenate(
            (
                np.array(top_header),
                np.array(column_metrics).reshape((len(column_metrics), 1)),
            ),
            axis=1,
        )
        column_index = pd.MultiIndex.from_arrays(np.transpose(array))

        # create row index
        try:
            row_index_names = response["reports"][0]["columnHeader"]["dimensions"]
            row_index = [
                element["dimensions"]
                for element in response["reports"][0]["data"]["rows"]
            ]
            row_index_named = pd.MultiIndex.from_arrays(
                np.transpose(np.array(row_index)), names=np.array(row_index_names)
            )
        except:
            row_index_named = None
        # combine into a dataframe
        df = pd.DataFrame(
            data=np.array(pivot_values), index=row_index_named, columns=column_index
        ).astype("float")
    except:
        df = pd.DataFrame()
    return df


def format_report(response):
    summary = format_summary(response)
    pivot = format_pivot(response)
    if pivot.columns.nlevels == 2:
        summary.columns = [[""] * len(summary.columns), summary.columns]

    return pd.concat([summary, pivot], axis=1)


def run_report(body, view_id, credentials_file, page_size=100000):

    def create_service(credentials_file):
        """Create a Google Analytics service object with given credentials."""
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        service = build("analyticsreporting", "v4", credentials=credentials)
        return service

    def get_response(service, body, view_id, page_size, page_token):
        """Fetch data from Google Analytics API."""
        response = (
            service.reports()
            .batchGet(body=create_body(body, view_id, page_size, page_token))
            .execute()
        )
        return response

    def collect_all_data(service, body, view_id, page_size):
        """Collect all pages of data and concatenate them into a single DataFrame."""
        page_token = None
        df_list = []

        while True:
            response = get_response(service, body, view_id, page_size, page_token)
            df_list.append(format_report(response))

            page_token = response["reports"][0].get("nextPageToken")
            if not page_token:
                break

        return pd.concat(df_list, ignore_index=True)

    # Create a service object
    service = create_service(credentials_file)
    print("Service creation complete!\nFetching data")

    # Collect all data and create DataFrame
    df = collect_all_data(service, body, view_id, page_size)
    print("Dataframe creation complete!")

    return df


def read_json_to_dict(file_path):
    """
    Reads a JSON file and returns its contents as a Python dictionary.

    Parameters:
    file_path (str): The path to the JSON file.

    Returns:
    dict: The contents of the JSON file as a dictionary.
    """
    with open(file_path, "r") as file:
        data_dict = json.load(file)
    return data_dict


if __name__ == "__main__":
    # Constants
    VIEWS = read_json_to_dict("./config/views.json")
    PERIOD = "yearMonth"

    # Reporting Variables
    END_DATE = datetime.today().strftime("%Y-%m-%d")

    # Run Your Report and Save
    for view_id, view_details in VIEWS.items():
        for report in Reports:
            subReports = Reports[report]
            for sub_report in subReports:
                subReport = subReports[sub_report]

                # Dimensions
                output_dimensions = [
                    # Date
                    {"name": f"ga:{PERIOD}"},
                    *subReport["Dims"],
                ]

                # Construct your Request
                report_request = {
                    "reportRequests": [
                        {
                            "dateRanges": [
                                {
                                    "startDate": view_details["startDate"],
                                    "endDate": END_DATE,
                                }
                            ],
                            "metrics": subReport["metrics"],
                            "dimensions": output_dimensions,
                        }
                    ]
                }

                report_name = f"./temp_reports/{view_details['name']}/{PERIOD}_{report}_{sub_report}.csv"

                try:
                    print(
                        f"fetching data for '{view_details['name']} {report} {sub_report}'"
                    )
                    ga_report = run_report(report_request, view_id, GA_API_KEYS)
                    ga_report.to_csv(report_name, index=True)

                    print(
                        f"'{view_details['name']} {report} {sub_report}' Report saved successfully!! :tada:\n"
                    )
                except Exception as exp:
                    print(f"Error occured: {exp}")
