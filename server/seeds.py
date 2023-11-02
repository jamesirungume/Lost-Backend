from faker import Faker
import random
from routes import app
from datetime import datetime

from models import db , User , Comment, Reward  , Item , Claim ,Payment

fake = Faker()

with app.app_context():

    itemstatus = ['lost' , 'found' , 'delivered']
    passwordarray =['kej' , 'jek' , 'lam' , 'vedit' ,'duds']
    adminapproved = [True ,False]
    claimsstatus = [ True , False]
    categories = ['electronic ', 'wearable']
    Role = ['Admin' , 'User']
    lostitems = [ 'laptop' , 'Earphone' , 'Airpod ', 'Charger' , 'Phone' , 'Mouse','Flashdisks']
    image_url =['https://www.lenovo.com/medias/lenovo-laptop-ideapad-3-14-intel-subseries-hero.png?context=bWFzdGVyfHJvb3R8MjY5MjEzfGltYWdlL3BuZ3xoODYvaDUzLzE0MTg2OTE5NTkxOTY2LnBuZ3w2ODgwOTdhZDhlODAwNTYzZmVlNDcwNzE5MGI3MzEzMWNiMTIxYmY5NWE3MzcxZDA1NzM2MzkwNWRlYzQ0MDU3'
                , 'https://rukminim2.flixcart.com/image/850/1000/l4a7pu80/battery-charger/c/j/a/33w-vooc-dart-flash-dh593-with-type-c-cable-charging-adapter-original-imagf7mgjty9z8sg.jpeg?q=90'
                , 'https://marvelafrica.co.ke/wp-content/uploads/2023/04/Apple-Airpods-Pro-2nd-gen-3.jpeg' ,
                'https://www.costco.co.uk/medias/sys_master/images/h37/hc3/119433914056734.jpg' ,
                'https://www.bigw.com.au/medias/sys_master/images/images/h05/h67/35171080798238.jpg' ,
                'https://oneplus.co.ke/wp-content/uploads/2022/09/OnePlus-Nord-Wired-Earphones.png' ,
                'https://www.techyshop.co.ke/wp-content/uploads/2015/11/8GB-TRANSCEND-HP-SANDISK-FLASH-DISK-1.jpg'
                ]
    print(len(image_url))

    User.query.delete()
    Item.query.delete()
    Comment.query.delete()
    Reward.query.delete()
    Claim.query.delete()
    Payment.query.delete()

    print("🦸‍♀️ Seeding users...")
    users_ids = []
    users = []
    for i in range(20):
        userobject = User(
            username = fake.name() ,
            email = fake.email() ,
            password = random.choice(passwordarray) ,
            role = random.choice(Role)
        )
        users.append(userobject)
        db.session.add_all(users)
        print(users)
        db.session.commit()
        users_ids.append(userobject.id)

    print("🦸‍♀️ seeding items...")
    
    itemsid = []
    itemss =[]
    for i in range(20):
        lostitemobject = Item(
            item_name = random.choice(lostitems) ,
            item_description = fake.sentence() ,
            user_reported_id = random.choice(users_ids) ,
            image_url = random.choice(image_url) ,
            status =random.choice(itemstatus) ,
            admin_approved = random.choice(adminapproved) ,
            categories = random.choice(categories)
        )

        itemss.append(lostitemobject)
        print(itemss)
        db.session.add_all(itemss)
        db.session.commit()
        itemsid.append(lostitemobject.id)
    
    print ("🦸‍♀️ seeding comment..")

    comments = []
    for i in range(20):
        commentobject = Comment(
            comment = fake.paragraph() ,
            lostitem_id = random.choice(itemsid)
            )
        comments.append(commentobject)
        db.session.add_all(comments)
        db.session.commit()

    print ("🦸‍♀️ seeding rewards..")
    rewards = []
    for i in range(20):
        rewardsobject = Reward(
            rewardamount = round(random.uniform(100.00, 100.00), 2) ,
            lostitem_id = random.choice(itemsid)
        )
        rewards.append(rewardsobject)
        db.session.add_all(rewards)
        db.session.commit()

    print ("🦸‍♀️ seeding claims..")
    claims = []
    for i in range(20):
        claimssobject = Claim(
            item_id = random.choice(itemsid) ,
            user_id = random.choice(users_ids) ,
            status = random.choice(claimsstatus)
        )
        claims.append(claimssobject)
        db.session.add_all(claims)
        db.session.commit()

    print ("🦸‍♀️ seeding payment..")
    payments = []
    for i in range(20):
        paymentsobject = Payment(
            reward_id = random.choice(itemsid),
            payer_user_id =  random.choice(users_ids) ,
            amount = round(random.uniform(100.00, 100.00), 2) ,
            payment_date =  datetime.now().date()
        )
        payments.append(paymentsobject)
        db.session.add_all(payments)
        db.session.commit()