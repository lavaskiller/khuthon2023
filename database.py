from deta import Deta

deta = Deta("c0s6CpFN39n_3kGRmJCADFYJLkCndrWpsz6z2woBaJaY")

db = deta.Base("users_db")


def insert_user(username, name, password):
    return db.put({"key": username, "name": name, "password": password})


def fetch_all_users():
    res = db.fetch()
    return res.items


def get_user(username):
    return db.get(username)


def update_user(username, updates):
    return db.update(updates, username)


def delete_user(username):
    return db.delete(username)


insert_user("dsf", "sss", "1234")
print(fetch_all_users())
print(get_user("dsf"))
update_user("dsf", updates={"name": "owen"})
print(fetch_all_users())
