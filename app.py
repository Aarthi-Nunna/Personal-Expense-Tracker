# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 10:25:07 2022

@author: 91900
"""

from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import re

app = Flask(__name__);
