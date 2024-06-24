import json
from datetime import datetime
import numpy as np
import pandas as pd
from google.oauth2 import service_account
from apiclient.discovery import build

# Constants
GA_API_KEYS = "config/api-keys.json"


"""### Define Procedures"""


def create_body(body, view_id, page_size=100000, page_token="0"):
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


def run_report(body, view_id, credentials_file, page_size=100000):
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
    print("Data fetch complete!\nCreating Dataframe")

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

    # Metrics
    output_metrics = {
        "Audience": [
            {"expression": "ga:users"},
            {"expression": "ga:newUsers"},
            {"expression": "ga:sessions"},
            {"expression": "ga:bounceRate"},
            {"expression": "ga:pageviewsPerSession"},
            {"expression": "ga:avgSessionDuration"},
            {"expression": "ga:transactions"},
            {"expression": "ga:transactionRevenue"},
            {"expression": "ga:transactionsPerSession"},
            {"expression": "ga:revenuePerTransaction"},
        ],
        "Audience_Behavior": [
            {"expression": "ga:sessions"},
            {"expression": "ga:pageviews"},
        ],
        "Behavior": [
            {"expression": "ga:pageviews"},
            {"expression": "ga:uniquePageviews"},
            {"expression": "ga:timeOnPage"},
            {"expression": "ga:entrances"},
            {"expression": "ga:bounceRate"},
            {"expression": "ga:exits"},
            {"expression": "ga:pageValue"},
        ],
        "Exits": [
            {"expression": "ga:exits"},
            {"expression": "ga:pageviews"},
        ],
        "Events": [
            {"expression": "ga:totalEvents"},
            {"expression": "ga:uniqueEvents"},
            {"expression": "ga:eventValue"},
            {"expression": "ga:avgEventValue"},
        ],
        "Goals": [
            {"expression": "ga:goalCompletionsAll"},
            {"expression": "ga:goalValueAll"},
        ],
        "Ecomm_Product": [
            {"expression": "ga:itemRevenue"},
            {"expression": "ga:uniquePurchases"},
            {"expression": "ga:itemQuantity"},
            {"expression": "ga:revenuePerItem"},
            {"expression": "ga:itemsPerPurchase"},
            {"expression": "ga:productRefunds"},
        ],
        "Ecomm_Sales": [
            {"expression": "ga:transactionRevenue"},
            {"expression": "ga:transactionTax"},
            {"expression": "ga:transactionShipping"},
            {"expression": "ga:refundAmount"},
            {"expression": "ga:itemQuantity"},
        ],
    }

    Reports = {
        "Audience": {
            "Geo_Language": {
                "Dims": [
                    {"name": "ga:language"},
                ],
                "metrics": output_metrics["Audience"],
            },
            "Behavior_NewVsReturning": {
                "Dims": [
                    {"name": "ga:userType"},
                ],
                "metrics": output_metrics["Audience"],
            },
            "Behavior_Frequency": {
                "Dims": [
                    {"name": "ga:sessionCount"},
                    {"name": "ga:daysSinceLastSession"},
                ],
                "metrics": output_metrics["Audience_Behavior"],
            },
            "Behavior_Engagement": {
                "Dims": [
                    {"name": "ga:sessionDurationBucket"},
                    {"name": "ga:pageDepth"},
                ],
                "metrics": output_metrics["Audience_Behavior"],
            },
            "Technology_Browser_OS": {
                "Dims": [
                    {"name": "ga:browser"},
                    {"name": "ga:operatingSystem"},
                ],
                "metrics": output_metrics["Audience"],
            },
            # needs change
            "Technology_Network": {
                "Dims": [
                    {"name": "ga:networkLocation"},
                    # {"name": "ga:hostname"},
                ],
                "metrics": output_metrics["Audience"],
            },
            "Mobile": {
                "Dims": [{"name": "ga:mobileDeviceInfo"}],
                "metrics": output_metrics["Audience"],
            },
            "Geo_Location": {
                "Dims": [
                    {"name": "ga:continent"},
                    # {"name": "ga:subContinent"},
                    {"name": "ga:country"},
                    {"name": "ga:city"},
                ],
                "metrics": output_metrics["Audience"],
            },
        },
        "Acquisition": {
            "Channels": {
                "Dims": [
                    {"name": "ga:source"},
                    {"name": "ga:medium"},
                ],
                "metrics": output_metrics["Audience"],
            },
            "Treemaps": {
                "Dims": [
                    {"name": "ga:channelGrouping"},
                ],
                "metrics": output_metrics["Audience"],
            },
            "Campaigns": {
                "Dims": [
                    {"name": "ga:campaign"},
                ],
                "metrics": output_metrics["Audience"],
            },
        },
        "Behavior": {
            "All_Pages": {
                "Dims": [
                    {"name": "ga:pagePath"},
                    {"name": "ga:pageTitle"},
                ],
                "metrics": output_metrics["Behavior"],
            },
            "Landing_Pages": {
                "Dims": [
                    {"name": "ga:landingPagePath"},
                    {"name": "ga:pageTitle"},
                ],
                "metrics": output_metrics["Audience"],
            },
            "Exit_Pages": {
                "Dims": [
                    {"name": "ga:exitPagePath"},
                    {"name": "ga:pageTitle"},
                ],
                "metrics": output_metrics["Exits"],
            },
            "Top_Events": {
                "Dims": [
                    {"name": "ga:eventCategory"},
                    {"name": "ga:eventAction"},
                    {"name": "ga:eventLabel"},
                ],
                "metrics": output_metrics["Events"],
            },
            "Events_Pages": {
                "Dims": [
                    {"name": "ga:exitPagePath"},
                    {"name": "ga:pageTitle"},
                ],
                "metrics": output_metrics["Events"],
            },
        },
        "Conversions": {
            "Goals": {
                "Dims": [
                    {"name": "ga:goalCompletionLocation"},
                ],
                "metrics": output_metrics["Goals"],
            },
            "Ecomm_Product_Performance": {
                "Dims": [
                    {"name": "ga:productName"},
                    {"name": "ga:productBrand"},
                    {"name": "ga:productSku"},
                ],
                "metrics": output_metrics["Ecomm_Product"],
            },
            "Ecomm_Sales_Performance": {
                "Dims": [
                    {"name": "ga:transactionId"},
                ],
                "metrics": output_metrics["Ecomm_Sales"],
            },
        },
    }

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

                report_name = f"./reports/{view_details['name']}/{PERIOD}_{report}_{sub_report}.csv"

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
