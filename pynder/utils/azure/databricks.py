import requests


def start_databricks_job(
    id_job, dict_params, instance_databricks, token_databricks, additional_headers={}
):
    """Function to trigger a databricks job using the API

    Parameters
    ----------
    id_job : int
        -> id of the job to be run
    dict_params : dict
        -> Optional parameters to be used in the notebook, use: dbutils.widgets.get('my_param')
    instance_databricks : str
        -> found in the workspace url, example: adb-7319820186586419.19.azuredatabricks.net
    token_databricks : str
        -> Private access token created in databricks workspace user settings

    Returns
    -------
    int, str, str
        -> status code, reason and content
    """
    headers = {"Authorization": f"Bearer {token_databricks}"}
    headers.update(additional_headers)

    url = f"https://{instance_databricks}/api/2.0/jobs/run-now/"
    payload = {"job_id": id_job, "notebook_params": dict_params}

    res = requests.post(url, headers=headers, json=payload)
    result = res.status_code, res.reason, res.content
    res.close()
    return result
