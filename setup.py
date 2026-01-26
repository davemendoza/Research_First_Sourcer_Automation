#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Talent Engine - Signal Intelligence
Research_First_Sourcer_Automation

All code, scripts, GitHub repositories, documentation, data, and GPT-integrated
components of the AI Talent Engine - Signal Intelligence and
Research_First_Sourcer_Automation Python Automation Sourcing Framework are
strictly proprietary.

All intellectual property rights, copyrights, trademarks, and related rights
are exclusively owned by Dave Mendoza, DBA AI Craft, Inc.

Unauthorized copying, modification, distribution, or use of this software,
in whole or in part, is strictly prohibited.
"""

from setuptools import setup, find_packages

setup(
    name="research_first_sourcer_automation",
    version="0.0.0",
    description="AI Talent Engine - Signal Intelligence",
    author="Dave Mendoza",
    author_email="",
    license="Proprietary",
    packages=find_packages(
        include=[
            "claude_runtime",
            "claude_runtime.*",
            "EXECUTION_CORE",
            "EXECUTION_CORE.*",
        ]
    ),
    include_package_data=True,
    python_requires=">=3.10",
)
