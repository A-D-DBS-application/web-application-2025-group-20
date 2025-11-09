from flask import Blueprint, request, redirect, url_for, render_template, session
from .models import db, User, Debtor

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')