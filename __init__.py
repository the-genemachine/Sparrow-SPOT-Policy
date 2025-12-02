"""
Sparrow SPOT Scale™ - Policy & Journalism Analysis Framework

A comprehensive evaluation system for policy documents and journalism,
featuring AI transparency detection, citation quality scoring, and
ethical compliance checking.

Version: 8.3
"""

__version__ = "8.3.3"
__author__ = "The Gene Machine"

from .sparrow_grader_v8 import SPARROWGrader, SPOTPolicy

__all__ = ['SPARROWGrader', 'SPOTPolicy']
