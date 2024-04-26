import dotenv
dotenv.load_dotenv()
import os
from fluent.handler import FluentHandler, FluentRecordFormatter
import logging
from ddtrace import tracer, patch
from datadog import initialize
from src.config import config

if os.environ.get("ENVIRONMENT", "development") in ["production", "staging"]:
    DD_AGENT_HOST = os.environ.get("DD_AGENT_HOST", "localhost")
    FLUENTD_HOST = os.environ.get("FLUENTD_HOST", "localhost")

    if os.environ.get("KUBERNETES_IMAGE_VERSION", "") == "":
        logging.basicConfig(level=logging.INFO)
        custom_format = {
            # 'host': '%(hostname)s',
            'where': '%(module)s.%(funcName)s',
            'type': 'streamlit',
            'programname': 'vidibot',
            'component': 'vidibot',
            'level': '%(levelname)s',
            'stack_trace': '%(exc_text)s',
            'messages': '%(message)s'
        }
        handler = FluentHandler('rubyapp-json.vidibot', host=FLUENTD_HOST, port=5241)
        formatter = FluentRecordFormatter(custom_format)
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)


        # FORMAT = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
        #     '[dd.service=%(dd.service)s dd.env=%(dd.env)s '
        #     'dd.version=%(dd.version)s '
        #     'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
        #     '- %(message)s')
        # logging.basicConfig(format=FORMAT)
        # ddtrace_logger = logging.getLogger("ddtrace")
        # ddtrace_logger.level = logging.INFO
    else:
        pass
        # custom_format = {
        #     'host': '%(hostname)s',
        #     'where': '%(module)s.%(funcName)s',
        #     'type': 'streamlit',
        #     'programname': 'vidibot',
        #     'component': 'vidibot',
        #     'level': '%(levelname)s',
        #     'stack_trace': '%(exc_text)s',
        #     'messages': '%(message)s'
        # }
        # custom_format = '{"host": "%(hostname)s","where": "%(module)s.%(funcName)s","type": "streamlit","programname": "vidibot","component": "vidibot","level": "%(levelname)s","stack_trace": "%(exc_text)s","messages": "%(message)s"}'
        # logging.basicConfig(level=logging.INFO, format=custom_format)

        # ddtrace_format = ('%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] '
        #     '[dd.service=%(dd.service)s dd.env=%(dd.env)s '
        #     'dd.version=%(dd.version)s '
        #     'dd.trace_id=%(dd.trace_id)s dd.span_id=%(dd.span_id)s] '
        #     '- %(message)s')
        # ddtrace_logger = logging.getLogger("ddtrace")
        # ddtrace_logger.level = logging.INFO
        # ddtrace_handler = logging.StreamHandler()
        # ddtrace_logger.addHandler(ddtrace_handler)
        # ddtrace_handler.setFormatter(logging.Formatter(ddtrace_format))

    logging.info("starting vidibot streamlit")
    tracer.configure(
        dogstatsd_url=f"udp://{DD_AGENT_HOST}:8125",
    )
    patch(langchain=True, requests=True)

    options = {
        'statsd_host': DD_AGENT_HOST,
        'statsd_port': 8125
    }

    initialize(**options)

else:
    tracer.enabled = False

import src.model.vector
import src.monkey_patch

import vertexai
vertexai.init(project=config['vertexai']['project'], location=config['vertexai']['location'])

logging.info("vidibot streamlit started")