from faker import Faker
import random
from routes import app, db
from datetime import datetime

from models import User, Comment, Reward, Item, Claim, Payment

fake = Faker()

with app.app_context():

    db.drop_all()
    db.create_all()

    def generate_fake_users(num_users):
        users = []
        for _ in range(num_users):
            username = fake.user_name()
            email = fake.email()
            password = fake.password()
            role = random.choice(['user', 'admin'])
            user = User(username=username, email=email, password=password, role=role)
            users.append(user)
        return users

    def generate_fake_items(users, num_items):
        items = []
        for _ in range(num_items):
            item_name = fake.word()
            item_description = fake.text()
            image_url = fake.image_url()
            reward = str(random.randint(1, 50))
            user_reported_id = random.choice(users).id
            status = random.choice(['lost', 'found'])
            item = Item(
                item_name=item_name,
                item_description=item_description,
                image_url=image_url,
                reward=reward,
                user_reported_id=user_reported_id,
                status=status
            )
            items.append(item)
        return items

    def generate_fake_rewards(items):
        rewards = []
        for item in items:
            rewardamount = str(random.randint(5, 30))
            reward = Reward(rewardamount=rewardamount, lostitem_id=item.id)
            rewards.append(reward)
        return rewards

    def generate_fake_claims(users, items):
        claims = []
        for _ in range(len(items) // 2):  # Generate claims for half of the items
            item = random.choice(items)
            user_id = random.choice(users).id
            status = random.choice(['claimed', 'notclaimed'])
            claim = Claim(
                item_description=fake.text(),
                image_url=fake.image_url(),
                item_name=fake.word(),
                user_id=user_id,
                status=status
            )
            claims.append(claim)
        return claims

    def generate_fake_comments(items, num_comments):
        comments = []
        for _ in range(num_comments):
            item = random.choice(items)
            comment = Comment(comment=fake.sentence(), lostitem_id=item.id)
            comments.append(comment)
        return comments

    def seed():
        num_fake_users = 10
        num_fake_items = 20
        num_fake_comments = 30

        fake_users = generate_fake_users(num_fake_users)
        db.session.add_all(fake_users)
        db.session.commit()

        fake_items = generate_fake_items(fake_users, num_fake_items)
        db.session.add_all(fake_items)
        db.session.commit()

        fake_rewards = generate_fake_rewards(fake_items)
        db.session.add_all(fake_rewards)
        db.session.commit()

        fake_claims = generate_fake_claims(fake_users, fake_items)
        db.session.add_all(fake_claims)
        db.session.commit()

        fake_comments = generate_fake_comments(fake_items, num_fake_comments)
        db.session.add_all(fake_comments)
        db.session.commit()

        print('Database seeded successfully!')

    if __name__ == '__main__':
        seed()
