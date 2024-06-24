# Set Metrics you want
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


# Set reports to download
Reports = {
    "Audience": {
        # "Geo_Location": {
        #     "Dims": [
        #         {"name": "ga:continent"},
        #         # {"name": "ga:subContinent"},
        #         {"name": "ga:country"},
        #         {"name": "ga:city"},
        #     ],
        #     "metrics": output_metrics["Audience"],
        # },
        "Geo_Language": {
            "Dims": [
                {"name": "ga:language"},
            ],
            "metrics": output_metrics["Audience"],
        },
        # "Behavior_NewVsReturning": {
        #     "Dims": [
        #         {"name": "ga:userType"},
        #     ],
        #     "metrics": output_metrics["Audience"],
        # },
        # "Behavior_Frequency": {
        #     "Dims": [
        #         {"name": "ga:sessionCount"},
        #         {"name": "ga:daysSinceLastSession"},
        #     ],
        #     "metrics": output_metrics["Audience_Behavior"],
        # },
        # "Behavior_Engagement": {
        #     "Dims": [
        #         {"name": "ga:sessionDurationBucket"},
        #         {"name": "ga:pageDepth"},
        #     ],
        #     "metrics": output_metrics["Audience_Behavior"],
        # },
        # "Technology_Browser_OS": {
        #     "Dims": [
        #         {"name": "ga:browser"},
        #         {"name": "ga:operatingSystem"},
        #     ],
        #     "metrics": output_metrics["Audience"],
        # },
        # # needs change
        # "Technology_Network": {
        #     "Dims": [
        #         {"name": "ga:networkLocation"},
        #         # {"name": "ga:hostname"},
        #     ],
        #     "metrics": output_metrics["Audience"],
        # },
        # "Mobile": {
        #     "Dims": [{"name": "ga:mobileDeviceInfo"}],
        #     "metrics": output_metrics["Audience"],
        # },
    },
    # "Acquisition": {
    #     "Channels": {
    #         "Dims": [
    #             {"name": "ga:source"},
    #             {"name": "ga:medium"},
    #         ],
    #         "metrics": output_metrics["Audience"],
    #     },
    #     "Treemaps": {
    #         "Dims": [
    #             {"name": "ga:channelGrouping"},
    #         ],
    #         "metrics": output_metrics["Audience"],
    #     },
    #     "Campaigns": {
    #         "Dims": [
    #             {"name": "ga:campaign"},
    #         ],
    #         "metrics": output_metrics["Audience"],
    #     },
    # },
    # "Behavior": {
    #     "All_Pages": {
    #         "Dims": [
    #             {"name": "ga:pagePath"},
    #             {"name": "ga:pageTitle"},
    #         ],
    #         "metrics": output_metrics["Behavior"],
    #     },
    #     "Landing_Pages": {
    #         "Dims": [
    #             {"name": "ga:landingPagePath"},
    #             {"name": "ga:pageTitle"},
    #         ],
    #         "metrics": output_metrics["Audience"],
    #     },
    #     "Exit_Pages": {
    #         "Dims": [
    #             {"name": "ga:exitPagePath"},
    #             {"name": "ga:pageTitle"},
    #         ],
    #         "metrics": output_metrics["Exits"],
    #     },
    #     "Top_Events": {
    #         "Dims": [
    #             {"name": "ga:eventCategory"},
    #             {"name": "ga:eventAction"},
    #             {"name": "ga:eventLabel"},
    #         ],
    #         "metrics": output_metrics["Events"],
    #     },
    #     "Events_Pages": {
    #         "Dims": [
    #             {"name": "ga:exitPagePath"},
    #             {"name": "ga:pageTitle"},
    #         ],
    #         "metrics": output_metrics["Events"],
    #     },
    # },
    # "Conversions": {
    #     "Goals": {
    #         "Dims": [
    #             {"name": "ga:goalCompletionLocation"},
    #         ],
    #         "metrics": output_metrics["Goals"],
    #     },
    #     "Ecomm_Product_Performance": {
    #         "Dims": [
    #             {"name": "ga:productName"},
    #             {"name": "ga:productBrand"},
    #             {"name": "ga:productSku"},
    #         ],
    #         "metrics": output_metrics["Ecomm_Product"],
    #     },
    #     "Ecomm_Sales_Performance": {
    #         "Dims": [
    #             {"name": "ga:transactionId"},
    #         ],
    #         "metrics": output_metrics["Ecomm_Sales"],
    #     },
    # },
}
