from iinfer.app.injections import after_det_filter_injection
from typing import Tuple, Dict, Any
import logging


class AfterDetFilterInjection2(after_det_filter_injection.AfterDetFilterInjection):
    def __init__(self, config:Dict[str,Any], logger:logging.Logger):
        super().__init__(config, logger)