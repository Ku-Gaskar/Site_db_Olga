from flask import Blueprint, render_template, url_for, g, request,redirect,flash


scopus=Blueprint('scopus',__name__,template_folder='templates',static_folder='static')

@scopus.route('/', methods=['GET', 'POST'])
def index():
    return 'scopus'