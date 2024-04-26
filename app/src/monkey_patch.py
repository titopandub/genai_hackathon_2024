import langchain_core
from typing import Optional, Callable, Any
from ddtrace import tracer
from langchain_core.runnables.base import RunnableSequence
from langchain_core.runnables.config import RunnableConfig
from langchain_core.runnables.utils import Input, Output

from langchain_core.output_parsers.json import parse_partial_json
from langchain_core.utils.json import _parse_json
import langchain_core.output_parsers.json as lc_op_j
import json
import re

import time
import logging

from src.config import config

RunnableSequence.invoke_original = RunnableSequence.invoke

class TimeTracker:
    def track(self, tag, threshold=None):
        self.start = time.time()
        self.tag = tag
        self.threshold = config['slow_timeout']
        if threshold != None:
            self.threshold = threshold

        return self

    def finish(self, message=""):
        diff = time.time() - self.start
        if diff > self.threshold:
            self.log(message)

    def log(self, message):
        new_message = ""
        try:
            new_message = str(message)
        except:
            pass
        logging.warn(f"[SLOW][{self.tag}] {new_message}")


def invoke(self, input: Input, config: Optional[RunnableConfig] = None, track: str = None) -> Output:
    span = None
    if track is not None:
        span = tracer.trace(name="llm.query", resource=track)

    time_tracker = TimeTracker().track(f"llm.query {track}")

    invoke_result = self.invoke_original(input=input, config=config)

    time_tracker.finish(f"input: {str(input)} \n\n\n output: {str(invoke_result)}")


    if track is not None:
        span.finish()

    return invoke_result

RunnableSequence.invoke = invoke


def parse_json_markdown(
    json_string: str, *, parser: Callable[[str], Any] = parse_partial_json
) -> dict:
    """
    Parse a JSON string from a Markdown string.

    Args:
        json_string: The Markdown string.

    Returns:
        The parsed JSON object as a Python dictionary.
    """
    try:
        return _parse_json(json_string, parser=parser)
    except json.JSONDecodeError:
        # Try to find JSON string within triple backticks
        match = re.search(r"(?:```)?(json)?(.*)", json_string, re.DOTALL) # --------> patch

        # If no match found, assume the entire string is a JSON string
        if match is None:
            json_str = json_string
        else:
            # If match found, use the content within the backticks
            json_str = match.group(2)
    return _parse_json(json_str, parser=parser)

lc_op_j.parse_json_markdown = parse_json_markdown