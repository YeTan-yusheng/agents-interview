async def test_register_login_me_flow(client):
    resp = await client.post("/users", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"
    assert "password_hash" not in body

    resp = await client.post("/users/login", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 200
    token = resp.json()["access_token"]

    resp = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "alice"


async def test_duplicate_username_conflict(client):
    await client.post("/users", json={"username": "bob", "password": "password123"})
    resp = await client.post("/users", json={"username": "bob", "password": "passw0rd123"})
    assert resp.status_code == 409


async def test_invalid_username_rejected(client):
    resp = await  client.post("/users", json={"username": "a", "password": "password123"})
    assert resp.status_code == 422


async def test_me_requires_valid_token(client):
    assert (await client.get("/users/me")).status_code == 401
    assert (await client.get("/users/me", headers={"Authorization": "Bearer fake-token"})).status_code == 401


async def test_overlong_username_rejected(client):
    resp = await client.post("/users", json={"username": "a" * 26, "password": "password123"})
    assert resp.status_code == 422


async def test_login_wrong_password(client):
    resp = await client.post("/users", json={"username": "alice", "password": "password123"})
    assert resp.status_code == 201

    resp = await client.post("/users/login", json={"username": "alice", "password": "wrong-password"})
    assert resp.status_code == 401
    password_error = resp.json()["detail"]

    resp = await client.post("/users/login", json={"username": "bob", "password": "password123"})
    assert resp.status_code == 401

    # 测试用户名不存在和密码错误返回相同错误信息
    assert resp.json()["detail"] == password_error
