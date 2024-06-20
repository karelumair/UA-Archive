import json
import numpy as np
import pandas as pd
from google.oauth2 import service_account
from apiclient.discovery import build

# Constants
GA_API_KEYS = "config/api-keys.json"


"""### Define Procedures"""


def create_body(body, view_id, page_size=10000, page_token="0"):
    body["reportRequests"][0]["viewId"] = view_id
    body["reportRequests"][0]["pageSize"] = page_size
    body["reportRequests"][0]["pageToken"] = page_token

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
            item["name"].split(":")[-1]
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


def run_report(body, view_id, credentials_file, page_size=10000):
    # Create service credentials
    credentials = service_account.Credentials.from_service_account_file(
        credentials_file, scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    # Create a service object
    service = build("analyticsreporting", "v4", credentials=credentials)

    # Get GA data
    page_token = "0"
    response = (
        service.reports()
        .batchGet(body=create_body(body, view_id, page_size, page_token))
        .execute()
    )
    df = format_report(response)

    # If the response has nextPageToken, continue
    while "nextPageToken" in response["reports"][0].keys():
        page_token = response["reports"][0]["nextPageToken"]
        response = (
            service.reports()
            .batchGet(body=create_body(body, view_id, page_size, page_token))
            .execute()
        )
        df = pd.concat([df, format_report(response)])

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
    REPORT_CODE = "Acquisition"

    # Reporting Variables
    END_DATE = "2023-06-20"

    # Metrics
    output_metrics = [
        {"expression": "ga:sessions"},
        {"expression": "ga:users"},
        {"expression": "ga:newUsers"},
        {"expression": "ga:bounces"},
        {"expression": "ga:bounceRate"},
        {"expression": "ga:avgSessionDuration"},
        {"expression": "ga:pageviews"},
        {"expression": "ga:uniquePageviews"},
        {"expression": "ga:pageviewsPerSession"},
    ]

    DIMS = {
        "Audience": [
            {"name": "ga:language"},
            {"name": "ga:country"},
            {"name": "ga:city"},
            {"name": "ga:deviceCategory"},
            {"name": "ga:mobileDeviceInfo"},
            {"name": "ga:browser"},
            {"name": "ga:operatingSystem"},
            {"name": "ga:networkLocation"},
            # {"name": "ga:userAgeBracket"},
            # {"name": "ga:userGender"},
        ],
        "Acquisition": [
            {"name": "ga:source"},
            {"name": "ga:medium"},
            {"name": "ga:campaign"},
            {"name": "ga:sourceMedium"},
            {"name": "ga:referralPath"},
            {"name": "ga:channelGrouping"},
            # {"name": ""},
        ],
    }

    # Dimensions
    output_dimensions = [{"name": "ga:yearMonth"}, *DIMS[REPORT_CODE]]

    # Run Your Report and Save
    for view_id, view_details in VIEWS.items():
        # Construct your Request
        report_request = {
            "reportRequests": [
                {
                    "dateRanges": [
                        {"startDate": view_details["startDate"], "endDate": END_DATE}
                    ],
                    "metrics": output_metrics,
                    "dimensions": output_dimensions,
                }
            ]
        }

        report_name = f"./reports/{view_details['name']}/{PERIOD}_{REPORT_CODE}.csv"

        try:
            print(f"fetching data for '{view_details['name']} {REPORT_CODE}'")
            ga_report = run_report(report_request, view_id, GA_API_KEYS)
            ga_report.to_csv(report_name, index=True)

            print(
                f"'{view_details['name']} {REPORT_CODE}' Report saved successfully!! :tada:\n"
            )
        except Exception as exp:
            print(f"Error occured: {exp}")
