# Copyright 2021 Vectorized, Inc.
#
# Use of this software is governed by the Business Source License
# included in the file licenses/BSL.md
#
# As of the Change Date specified in that file, in accordance with
# the Business Source License, use of this software will be governed
# by the Apache License, Version 2.0

from ducktape.mark.resource import cluster
from rptest.clients.types import TopicSpec
from rptest.wasm.topic import construct_materialized_topic
from rptest.wasm.topics_result_set import materialized_result_set_compare
from rptest.wasm.wasm_build_tool import WasmTemplateRepository
from rptest.wasm.wasm_test import WasmScript, WasmTest


class WasmIdentityTest(WasmTest):
    topics = (TopicSpec(partition_count=3,
                        replication_factor=3,
                        cleanup_policy=TopicSpec.CLEANUP_DELETE), )

    def __init__(self, test_context, num_records=1024, record_size=1024):
        super(WasmIdentityTest, self).__init__(test_context, extra_rp_conf={})
        self._num_records = num_records
        self._record_size = record_size
        assert len(self.topics) >= 1

    def input_topics(self):
        """
        Default behavior is for all scripts to have all topics as input topics
        """
        return [x.name for x in self.topics]

    def wasm_test_outputs(self):
        """
        The materialized log:
        [
          itopic.$script_a_output$,
        ]
        Should exist by tests end and be identical to its respective input log
        """
        itopic = self.topics[0].name
        return [[(itopic, "script_a_output")]]

    def wasm_xfactor(self):
        """
        Multiply with self._num_records to obtain expected record count
        """
        return 1

    def wasm_test_input(self):
        """
        Topics that will be produced onto, number of records and record_size
        """
        return [(x, self._num_records, self._record_size) for x in self.topics]

    def wasm_test_plan(self):
        """
        List of scripts to deploy, built from the results of wasm_test_outputs().
        By default inputs to all scripts will be self.input_topics()
        """
        itopics = self.input_topics()
        return [
            WasmScript(inputs=itopics,
                       outputs=[(construct_materialized_topic(it, ot),
                                 self._num_records * self.wasm_xfactor())
                                for it, ot in opts],
                       script=WasmTemplateRepository.IDENTITY_TRANSFORM)
            for opts in self.wasm_test_outputs()
        ]

    @cluster(num_nodes=3)
    def verify_materialized_topics_test(self):
        """
        Entry point for all tests, asynchronously we perform the following tasks:
        1. Scripts are built & deployed
        2. Consumers are set-up listening for expected num records on output topics
        3. Producers set-up and begin producing onto input topics
        4. When finished, perform assertions in this method
        """
        input_results, output_results = self._start(self.wasm_test_input(),
                                                    self.wasm_test_plan())
        for opts in self.wasm_test_outputs():
            outputs = set([
                construct_materialized_topic(src, dest) for src, dest in opts
            ])
            output_stems = set([src for src, _ in opts])
            tresults = output_results.filter(lambda x: x.topic in outputs)
            iresults = input_results.filter(lambda x: x.topic in output_stems)
            if not materialized_result_set_compare(iresults, tresults):
                raise Exception(f"Set {opts} results weren't as expected")
