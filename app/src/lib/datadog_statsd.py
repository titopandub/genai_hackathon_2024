
from datadog import statsd
from typing import Optional, List, Text, Union
import os

def increment(
    metric,  # type: Text
    value=1,  # type: float
    tags=None,  # type: Optional[List[str]]
    sample_rate=None,  # type: Optional[float]
):
    if os.environ.get("ENVIRONMENT", "development") in ["production", "staging"]:
        statsd.increment(metric=metric, value=value, tags=tags, sample_rate=sample_rate)