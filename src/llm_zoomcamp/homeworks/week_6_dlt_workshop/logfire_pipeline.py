from typing import Any

import dlt
from dlt.common.pendulum import pendulum
from dlt.sources.rest_api import RESTAPIConfig, rest_api_resources


@dlt.source(name="logfire")
def logfire_source(
    read_token: str = dlt.secrets.value,
    min_timestamp: str = None,
) -> Any:
    """Load trace records from the Pydantic Logfire Query API.

    Args:
        read_token: Logfire read token. Auto-loaded from secrets.toml.
        min_timestamp: Start of the query range (ISO8601). Defaults to 7 days ago.
    """
    if min_timestamp is None:
        min_timestamp = pendulum.now("UTC").subtract(days=7).to_iso8601_string()

    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://logfire-eu.pydantic.dev/",
            "auth": {
                "type": "bearer",
                "token": read_token,
            },
        },
        "resources": [
            {
                "name": "records",
                "endpoint": {
                    "path": "v2/query",
                    "method": "POST",
                    "json": {
                        "sql": "SELECT * FROM records ORDER BY start_timestamp",
                        "min_timestamp": min_timestamp,
                        "limit": 10000,
                    },
                    "data_selector": "data",
                },
                "primary_key": "span_id",
            },
        ],
    }
    yield from rest_api_resources(config)


def load_traces() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="logfire_pipeline",
        destination="duckdb",
        dataset_name="agent_traces",
    )
    load_info = pipeline.run(logfire_source(), write_disposition="replace")
    print(load_info)
    print(pipeline.last_trace.last_normalize_info)


if __name__ == "__main__":
    load_traces()
