from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


# Mock User Class (Replace this with your actual User model)
class User(db.Document):   
    name = db.StringField()
    password = db.StringField()
    email = db.StringField()                                                                                                 
    def to_json(self):        
        return {"name": self.name,
                "email": self.email}

    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id)

# Mock User Database (Replace this with your actual user database)
users = {'user_id': {'password': 'password'}}

# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Login Route
@app.route('/login', methods=['POST'])
def login():
    info = json.loads(request.data)
    username = info.get('username', 'guest')
    password = info.get('password', '') 
    user = User.objects(name=username,
                        password=password).first()
    if user:
        login_user(user)
        return jsonify(user.to_json())
    else:
        return jsonify({"status": 401,
                        "reason": "Username or Password Error"})
# Dashboard Route (Protected)
@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.id}! This is the dashboard.'

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/new_account")
def create_account():
    return 1