from flask import Flask ,request
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Namespace, Resource, fields
from models import User, db , Item , Reward,Claim,Comment
from flask_migrate import Migrate
import secrets
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={'/*': {'origins': '*'}})

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
    'id':fields.Integer,
    "username": fields.String,
    "password": fields.String,
    "email": fields.String,
    "role" : fields.String,
})

lost_item_schema = api.model('item', {
    'id':fields.Integer,
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
claim_item_schema = ns.model('claimeditem',{
    'id':fields.Integer,
    'item_description':fields.String,
    'image_url': fields.String,
    'item_name': fields.String ,
    'user_id': fields.Integer,
    'status': fields.String,
    'category': fields.String      
})



# ------------------------------------------------------------END OF ROUTES---------------------------------------

# Define API routes
@ns.route('/users')
class Users(Resource):
    @ns.marshal_list_with(users_schema)
    def get(self):
        users = User.query.all()
        return users, 200
    
\
# Signup endpoint
@ns.route('/signup')
class Signup(Resource):
    @ns.expect(user_input_schema)
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        role = data.get('role')

        if not (username and password and email and role):
            return {'message': 'Missing required details'}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'message': 'Email already exists'}, 400

        new_user = User(username=username, password=password, email=email, role=role)
        db.session.add(new_user)
        db.session.commit()

        access_token = create_access_token(identity={'id': new_user.id, 'role': new_user.role})

        return {
            'access_token': access_token,
            'username': new_user.username,
            'role': new_user.role
        }, 201

# Login endpoint
@ns.route('/login')
class Login(Resource):
    @ns.expect(user_input_schema)
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')
        if not (username and password):
            return {'message': 'Missing username or password'}, 400

        user = User.query.filter_by(username=username).first()
        if not user or user.password != password:  # Use secure password hashing in production
            return {'message': 'Invalid username or password'}, 401

        access_token = create_access_token(identity={'id': user.id, 'role': user.role})

        return {
            'access_token': access_token,
            'username': user.username,
            'role': user.role
        }, 200
    

@ns.route('/itemlost/<int:item_id>')  # Use the item_id as a parameter in the URL
class UpdateItemlost(Resource):

    @ns.expect(lost_item_schema)
    def put(self, item_id):
        try:
            # Attempt to retrieve the item with the given item_id
            lost_item = Item.query.get(item_id)

            if lost_item:
                data = request.json  # Get the JSON data from the request

                # Update the item fields with the new data
                lost_item.item_name = data.get('item_name')
                lost_item.item_description = data.get('item_description')
                lost_item.image_url = data.get('image_url')
                lost_item.reward = data.get('reward')
                # You can update other fields as needed

                db.session.commit()

                return {
                    "message": f"Lost item with ID {item_id} updated successfully",
                    "lostitem": {
                        "item_name": lost_item.item_name,
                        "item_description": lost_item.item_description,
                        'image_url': lost_item.image_url,
                        'reward': lost_item.reward,
                        'status': lost_item.status
                    }
                }, 200
            else:
                return {
                    "error": f"Lost item with ID {item_id} not found"
                }, 404
        except Exception as e:
            db.session.rollback()
            return {
                "message": "Failed to update the lost item",
                 "error": str(e)
            }, 500
@ns.route('/itemlost')
class PostItemlost(Resource):
    @ns.expect(lost_item_schema)
    def post(self):
        try:
            data = request.get_json() 
              # Get the JSON data from the request
            
            
            new_lostitem = Item(
                item_name=data.get('item_name'),
                item_description=data.get('item_description'),
                image_url=data.get('image_url'),
                reward=data.get('reward'),
                status= 'lost',
                
                user_reported_id=data.get('user_reported_id')
            )

            db.session.add(new_lostitem)
            db.session.commit()

           

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
                status='pending_found_items',
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
     pending_items = Item.query.filter_by(status='pending_found_items').all()
     if pending_items:
        return pending_items
     else:
        return {'message': 'No pending found items'}, 200
     
@ns.route('/approve_found_item/<int:item_id>')
class ApproveFoundItem(Resource):
    def put(self, item_id):
        found_item = Item.query.get(item_id)

        if found_item and found_item.status == 'pending_found_items':
            found_item.status = 'found'
            found_item.admin_approved = True
            db.session.commit()
            return {"message": "Found item approved by admin"}, 200
        else:
            return {"error": "Item not found or not in 'pending' status"}, 404
        
        
@ns.route('/found_items')
class ListFoundItems(Resource):
    def get(self):
        found_items = Item.query.filter_by(status='found').all()
        if found_items:
            items = [
                {
                    'id': item.id,
                    'item_name': item.item_name,
                    'item_description': item.item_description,
                    'image_url': item.image_url,
                    'categories': item.categories,
                } for item in found_items
            ]
            return {'found_items': items}, 200
        else:
            return {'message': 'No found items found'}, 200
  
@ns.route('/lostitems/<int:id>')
class Deletetransaction(Resource):   
    def delete(self ,id):
        transaction = Item.query.filter_by(id=id).first()
        db.session.delete(transaction)
        db.session.commit()

        response_dict = {
            "message" : "record succefully deleted"
        }
        return response_dict, 200
    

    
# -----------------------------------------------------claim logic---------------------------------------------------------------
@ns.route('/claimitem')
class Claimfounditem(Resource):
    @ns.expect(claim_item_schema)
    def post(self):
        try:
            data = request.json  # Get the JSON data from the request

            new_claimeditem = Claim(
                image_url = data.get('image_url'),
                item_description = data.get('item_description'),
                item_name=data.get('item_name'),
                user_id=data.get('user_id'),
                status= 'notclaimed',
            )

            db.session.add(new_claimeditem)
            db.session.commit()

            return {
                "message": "Item claimed. Awaiting admin approval.",
                "founditem": {
                    "item_iname": new_claimeditem.item_name,
                    "user_id": new_claimeditem.user_id,
                    'status': new_claimeditem.status
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                "message": "Failed to claim item",
                "error": str(e)
            }, 500
        

@ns.route('/claimItem')
class ClaimFounditem(Resource):
    @ns.expect(claim_item_schema)
    def post(self):
        try:
            data = request.json  # Get the JSON data from the request

            new_claimeditem = Claim(
                image_url = data.get('image_url'),
                item_description = data.get('item_description'),
                item_name=data.get('item_name'),
                user_id=data.get('user_id'),
                status= data.get('status')
            )

            db.session.add(new_claimeditem)
            db.session.commit()

            return {
                "message": "Item claimed. Awaiting admin approval.",
                "founditem": {
                    "item_iname": new_claimeditem.item_name,
                    "user_id": new_claimeditem.user_id,
                    'status': new_claimeditem.status
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                "message": "Failed to claim item",
                "error": str(e)
            }, 500
        
@ns.route('/approve_claimed_item/<int:item_id>')
class ApproveClaimedItem(Resource):
    def put(self, item_id):
        claim_item = Claim.query.get(item_id)

        if claim_item and claim_item.status == 'notclaimed' :
            claim_item.status = 'claimed'
            db.session.commit()
            return {"message": "Claimed item approved by admin"}, 200
        else:
            return {"error": "Item not claimed "}, 404
        
@ns.route('/pendingclaim_items')
class get_pending_items(Resource):
    @ns.marshal_list_with(claim_item_schema)
    def get(self):
        pending_claims = Claim.query.filter_by(status='notclaimed').all()
        pending_items = Item.query.filter_by(status='pending_found_items').all()

        if pending_claims or pending_items:
            return pending_claims + pending_items  # Merge the results and return
        else:
            return {'message': 'No pending items'}, 200

     
@ns.route('/returned_items')
class get_returned_items(Resource):
    @ns.marshal_list_with(claim_item_schema )
    def get(self):
     pending_items = Claim.query.filter_by(status='claimed').all()
     if pending_items:
        return pending_items
     else:
        return {'message': 'No pending items'}, 200
     
@ns.route('/comments')
class CommentResource(Resource):
    @ns.marshal_list_with(comment_model)
    def get(self):
        comments = Comment.query.all()
        return comments, 200

    @ns.expect(comment_model)
    def post(self):
        try:
            data = request.json
            new_comment = Comment(
                comment=data.get('comment'),
                lostitem_id=data.get('lostitem_id')
            )
            db.session.add(new_comment)
            db.session.commit()

            return {
                "message": "Comment added successfully",
                "comment": {
                    "id": new_comment.id,
                    "comment": new_comment.comment,
                    "lostitem_id": new_comment.lostitem_id
                }
            }, 201

        except Exception as e:
            db.session.rollback()
            return {
                "message": "Failed to add a comment",
                "error": str(e)
            }, 500

     



# Main entry point
if __name__ == '__main__':
    app.run(port=5555, debug=True)