"""
Unit tests for Diagnostic Error Explainer.
"""

import unittest
from qnx_sentinel.diagnostics.error_explainer import ErrorExplainer


class TestErrorExplainer(unittest.TestCase):

    def setUp(self):
        self.explainer = ErrorExplainer()

    def test_epoll_error_diagnosis(self):
        log = "src/main.c:12:24: fatal error: sys/epoll.h: No such file or directory\ncompilation terminated."
        res = self.explainer.explain_log(log)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].category, "LINUX_SPECIFIC_SYSCALL")
        self.assertTrue(any("poll()" in step for step in res[0].remediation_steps))
        self.assertIsNotNone(res[0].suggested_diff)

    def test_timerfd_error_diagnosis(self):
        log = "undefined reference to `timerfd_create'"
        res = self.explainer.explain_log(log)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].category, "LINUX_SPECIFIC_SYSCALL")
        self.assertTrue(any("timer_create" in step for step in res[0].remediation_steps))

    def test_lpthread_link_diagnosis(self):
        log = "nto-ld: cannot find -lpthread\ncollect2: error: ld returned 1 exit status"
        res = self.explainer.explain_log(log)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].category, "COMPILER_TOOLCHAIN")
        self.assertTrue(any("libc.so" in step for step in res[0].remediation_steps))

    def test_pthread_yield_diagnosis(self):
        log = "worker.cpp: error: 'pthread_yield' was not declared in this scope"
        res = self.explainer.explain_log(log)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].category, "GNU_EXTENSION")
        self.assertTrue(any("sched_yield" in step for step in res[0].remediation_steps))


if __name__ == "__main__":
    unittest.main()
