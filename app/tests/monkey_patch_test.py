import unittest
from tests.base import BaseTest
from unittest.mock import patch
import tests.bootstrap as _

from langchain_core.output_parsers.json import JsonOutputParser
from langchain_core.runnables.base import RunnableSequence

from ddtrace.tracer import Tracer
from langchain_core.prompts import ChatPromptTemplate
from src.monkey_patch import TimeTracker
import time

class TestMonkeyPatch(BaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        pass

    @patch.object(TimeTracker, "track")
    @patch.object(Tracer, "trace")
    @patch.object(RunnableSequence, "invoke_original")
    def test_invoke_track(self, invoke_original, trace, track):
        chain = (ChatPromptTemplate.from_template("") | {})

        chain.invoke({"test": "test"}, track="test")

        trace.assert_called()
        invoke_original.assert_called()
        trace().finish.assert_called()
        track.assert_called()

    @patch.object(Tracer, "trace")
    @patch.object(RunnableSequence, "invoke_original")
    def test_invoke_not_track(self, invoke_original, trace):
        chain = (ChatPromptTemplate.from_template("") | {})

        chain.invoke({"test": "test"})

        trace.assert_not_called()
        invoke_original.assert_called()
        trace().finish.assert_not_called()

    def test_json_output_parse(self):
        results = map(lambda x: JsonOutputParser().parse(x), [
            '{"key": "value"',
            '```{"key": "value"}```',
            '```{"key": "value"}',
            '```{"key": "value"',
            '```{"key": "value"```',
            '```json{"key": "value"}```',
            '```json{"key": "value"}',
            '```json{"key": "value"',
            '```json{"key": "value"```',
            '```{"key": "value", "key2": "value2"```',
            '{"key": "value"}```', # ----> monkeypatch for langchain
        ])

        for result in results:
            self.assertEqual("value", result["key"])

    @patch.object(TimeTracker, "log")
    def test_time_tracker_not_timeout(self, log):
        tracker = TimeTracker().track("tag", 1)
        time.sleep(0.1)
        tracker.finish("message")

        log.assert_not_called()
        
        
    @patch.object(TimeTracker, "log")
    def test_time_tracker_timeout(self, log):
        tracker = TimeTracker().track("tag", 0.1)
        time.sleep(0.2)
        tracker.finish("message")

        log.assert_called()
        
        