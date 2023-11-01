from flask import Flask ,request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Namespace, Resource, fields
from models import User, db , Item , Reward
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)

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
# ---------------------------------------------------------API ROUTES----------------------------------------

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

        if not (username and password and email):
            return {'message': 'Missing username, password, or email'}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'message': 'Email already exists'}, 400

        new_user = User(username=username,
                         password=password, 
                         email=email)

        db.session.add(new_user)
        db.session.commit()

        return {'message': 'User created successfully'}, 201


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
# Main entry point
if __name__ == '__main__':
    app.run(port=5555, debug=True)
