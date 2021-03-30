# Copyright 2021 Vectorized, Inc.
#
# Use of this software is governed by the Business Source License
# included in the file licenses/BSL.md
#
# As of the Change Date specified in that file, in accordance with
# the Business Source License, use of this software will be governed
# by the Apache License, Version 2.0

import random

from rptest.tests.wasm_identity_test import WasmIdentityTest, WasmMultiScriptIdentityTest
from rptest.wasm.topics_result_set import materialized_at_least_once_compare


class WasmFailureRecoveryTest(WasmIdentityTest):
    def __init__(self, test_context, num_records=10000, record_size=1024):
        conf = {'coproc_offset_flush_interval_ms': 1000}
        super(WasmFailureRecoveryTest, self).__init__(test_context,
                                                      extra_rp_conf=conf,
                                                      num_records=num_records,
                                                      record_size=record_size)
        self._one_traunch_observed = False

    def records_recieved(self, output_recieved):
        if self._one_traunch_observed is False:
            self.restart_wasm_engine(
                random.sample(self.redpanda.nodes, 1)[0], 3)
            self._one_traunch_observed = True

    def verify_results(self):
        return materialized_at_least_once_compare

    def wasm_test_timeout(self):
        """
        2-tuple representing timeout(0) and backoff interval(1)
        """
        return (120, 1)


class WasmFailureMultiScriptTest(WasmMultiScriptIdentityTest):
    def __init__(self, test_context, num_records=10000, record_size=1024):
        conf = {'coproc_offset_flush_interval_ms': 1000}
        super(WasmFailureMultiScriptTest,
              self).__init__(test_context,
                             extra_rp_conf=conf,
                             num_records=num_records,
                             record_size=record_size)
        self._one_traunch_observed = False

    def records_recieved(self, output_recieved):
        if self._one_traunch_observed is False:
            self.restart_wasm_engine(
                random.sample(self.redpanda.nodes, 1)[0], 3)
            self._one_traunch_observed = True

    def verify_results(self):
        return materialized_at_least_once_compare

    def wasm_test_timeout(self):
        """
        2-tuple representing timeout(0) and backoff interval(1)
        """
        return (120, 1)


class WasmRedpandaFailureRecoveryTest(WasmIdentityTest):
    def __init__(self, test_context, num_records=10000, record_size=1024):
        conf = {'coproc_offset_flush_interval_ms': 1000}
        super(WasmRedpandaFailureRecoveryTest,
              self).__init__(test_context,
                             extra_rp_conf=conf,
                             num_records=num_records,
                             record_size=record_size)
        self._one_traunch_observed = False

    def records_recieved(self, output_recieved):
        if self._one_traunch_observed is False:
            self.restart_redpanda(random.sample(self.redpanda.nodes, 1)[0], 3)
            self._one_traunch_observed = True

    def verify_results(self):
        return materialized_at_least_once_compare

    def wasm_test_timeout(self):
        """
        2-tuple representing timeout(0) and backoff interval(1)
        """
        return (120, 1)


class WasmRedpandaFailureMultiScriptTest(WasmMultiScriptIdentityTest):
    def __init__(self, test_context, num_records=10000, record_size=1024):
        conf = {'coproc_offset_flush_interval_ms': 1000}
        super(WasmRedpandaFailureMultiScriptTest,
              self).__init__(test_context,
                             extra_rp_conf=conf,
                             num_records=num_records,
                             record_size=record_size)
        self._one_traunch_observed = 0

    def records_recieved(self, output_recieved):
        self._one_traunch_observed += 1
        if self._one_traunch_observed == 1:
            self.restart_redpanda(random.sample(self.redpanda.nodes, 1)[0], 3)

    def verify_results(self):
        return materialized_at_least_once_compare

    def wasm_test_timeout(self):
        """
        2-tuple representing timeout(0) and backoff interval(1)
        """
        return (2000, 1)
