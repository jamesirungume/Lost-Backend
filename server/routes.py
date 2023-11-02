from flask import Flask ,request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Namespace, Resource, fields
from models import User, db , Item , Reward
from flask_migrate import Migrate
import secrets
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

# Initialize Flask app
app = Flask(__name__)



secret_key = secrets.token_hex(16)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-RESTx
api = Api()
api.init_app(app)

# Define API namespace
ns = Namespace('lost&found')
api.add_namespace(ns)
#
jwt = JWTManager(app)
# ---------------------------------------------------------API ROUTES_SCHEMAS----------------------------------------

# Define API models
users_schema = api.model('users',{
    "username": fields.String,
    "email": fields.String,
    "role": fields.String
})

user_input_schema = api.model('user_input',{
    "username": fields.String,
    "password": fields.String,
    "email": fields.String,
    "role" : fields.String,
})

lost_item_schema = api.model('item', {
    'item_name': fields.String(required=True, description='Name of the item'),
    'item_description': fields.String(description='Description of the item'),
    'image_url': fields.String(description='URL of the item image'),
    'user_reported_id': fields.Integer(description='User ID reporting the item') ,
    'status' : fields.String,
    'reward' : fields.String 
})

get_lostitems_schema = api.model('lostitem' ,{
   'item_name': fields.String(required=True, description='Name of the item'),
    'item_description': fields.String(description='Description of the item'),
    'image_url': fields.String(description='URL of the item image'),
    'user_reported_id': fields.Integer(description='User ID reporting the item') ,
    'reward' : fields.String 
})

user_login_schema =api.model('login' , {
   'username' : fields.String(),
   'password' : fields.String(),
})

reward_model = ns.model('Reward', {
    'id': fields.Integer,
    'rewardamount': fields.String,
    'lostitem_id': fields.Integer,
})

comment_model = ns.model('Comment', {
    'id': fields.Integer,
    'comment': fields.String,
    'lostitem_id': fields.Integer,
})
reportfound_item_schema = api.model('lostitem' ,{
   'item_name': fields.String(required=True, description='Name of the item'),
    'item_description': fields.String(description='Description of the item'),
    'image_url': fields.String(description='URL of the item image'),
    'user_reported_id': fields.Integer(description='User ID reporting the item') ,
    'status' : fields.String ,
})
pending_item_schema = api.model('lostitem' ,{
   'item_name': fields.String(required=True, description='Name of the item'),
    'item_description': fields.String(description='Description of the item'),
    'status' : fields.String ,
})




# ------------------------------------------------------------END OF ROUTES---------------------------------------

# Define API routes
@ns.route('/users')
class Users(Resource):
    @ns.marshal_list_with(users_schema)
    def get(self):
        users = User.query.all()
        return users, 200
    
@ns.route('/signup')
class Signup(Resource):
    @ns.expect(user_input_schema)
    def post(self):
        data = request.get_json() 

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')

        if not (username and password and email):
            return {'message': 'Missing username, password, or email'}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'message': 'Email already exists'}, 400

        new_user = User(username=username,
                         password=password, 
                         email=email,
                         role = role
                         )

        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201
    
@ns.route('/login')
class Login(Resource):
    @ns.expect(user_login_schema)
    def post(self):
        data = request.get_json()
        # check whether data is missing or if the username or 'password' are missing
        username = data.get('username')
        password = data.get('password')
        if not(username and password):
            return{
                'message': 'Missing username , password'
            } , 400
        
        # query to database to find the user with the provided username
        user = User.query.filter_by(username = username).first()
        if not user:
            return {
                'message' : 'could Not Verify'
            } , 401
        
        access_token = create_access_token(identity=user.id)
        return {
            'access_token': access_token ,
            'username' : user.username
        } , 201
        
@ns.route('/itemlost')
class PostItemlost(Resource):
    @ns.expect(lost_item_schema)
    def post(self):
        try:
            data = request.json  # Get the JSON data from the request

            new_lostitem = Item(
                item_name=data.get('item_name'),
                item_description=data.get('item_description'),
                image_url=data.get('image_url'),
                reward=data.get('reward'),
                status='lost',
                user_reported_id=data.get('user_reported_id')
            )

            db.session.add(new_lostitem)
            db.session.commit()

            return {
                "message": "Transaction created successfully",
                "lostitem": {
                    "item_name": new_lostitem.item_name,
                    "item_description": new_lostitem.item_description,
                    'image_url': new_lostitem.image_url,
                    'reward': new_lostitem.reward,
                    'status': new_lostitem.status
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                "message": "Failed to create a lostitem",
                "error": str(e)
            }, 500


@ns.route('/lostitems')
class Users(Resource):
    @ns.marshal_list_with(lost_item_schema)  # Assuming get_lostitems_schema is used for marshaling individual items
    def get(self):
        lost_items = Item.query.filter_by(status='lost').all()
        if not lost_items:
            # You can customize the response if no lost items are found
            return {"message": "No lost items found"}, 404
        return lost_items, 200
    
@ns.route('/rewards')
class RewardsResource(Resource):
    @ns.marshal_list_with(reward_model)
    def get(self):
        rewards = Reward.query.all()
        return rewards , 201
    
@ns.route('/reportfounditem')
class Reportfounditem(Resource):
    @ns.expect(reportfound_item_schema)
    def post(self):
        try:
            data = request.json  # Get the JSON data from the request

            new_founditem = Item(
                item_name=data.get('item_name'),
                item_description=data.get('item_description'),
                image_url=data.get('image_url'),
                status='pending',
                user_reported_id=data.get('user_reported_id')
            )

            db.session.add(new_founditem)
            db.session.commit()

            return {
                "message": "Found item reported. Awaiting admin approval.",
                "founditem": {
                    "item_name": new_founditem.item_name,
                    "item_description": new_founditem.item_description,
                    'image_url': new_founditem.image_url,
                    'reward': new_founditem.reward,
                    'status': new_founditem.status
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                "message": "Failed to report a found item",
                "error": str(e)
            }, 500

@ns.route('/pending_items')
class get_pending_items(Resource):
    @ns.marshal_list_with(pending_item_schema)
    def get(self):
     pending_items = Item.query.filter_by(status='pending').all()
     if pending_items:
        return pending_items
     else:
        return {'message': 'No pending found items'}, 200
     
@ns.route('/approve_found_item/<int:item_id>')
class ApproveFoundItem(Resource):
    def put(self, item_id):
        found_item = Item.query.get(item_id)

        if found_item and found_item.status == 'pending':
            found_item.status = 'found'
            found_item.admin_approved = True
            db.session.commit()
            return {"message": "Found item approved by admin"}, 200
        else:
            return {"error": "Item not found or not in 'pending' status"}, 404

# Main entry point
if __name__ == '__main__':
    app.run(port=5555, debug=True)
