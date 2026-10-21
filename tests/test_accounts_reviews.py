"""Contas, revisões, coautores e convites."""


def test_signup_login_refresh_logout_and_profile(client, signup):
    headers = signup("ana", "Ana@Example.com")
    assert client.get("/me", headers=headers).json()["email"] == "ana@example.com"

    assert client.post("/auth/signup", json={"username": "ANA", "email": "x@example.com",
                                             "password": "senha-segura"}).status_code == 409
    assert client.post("/auth/signup", json={"username": "outra", "email": "ana@example.com",
                                             "password": "senha-segura"}).status_code == 409
    assert client.post("/auth/login", json={"login": "ana", "password": "errada"}).status_code == 401

    by_email = client.post("/auth/login", json={"login": "ANA@example.com", "password": "senha-segura"})
    assert by_email.status_code == 200
    refreshed = client.post("/auth/refresh", json={"refresh_token": by_email.json()["refresh_token"]})
    assert refreshed.status_code == 200
    assert client.post("/auth/refresh", json={"refresh_token": by_email.json()["refresh_token"]}).status_code == 401

    session = {"Authorization": f"Bearer {refreshed.json()['access_token']}"}
    updated = client.patch("/me", headers=session, json={"first_name": "Ana", "last_name": "Souza"})
    assert updated.json()["full_name"] == "Ana Souza"
    assert client.post("/me/password", headers=session,
                       json={"current_password": "errada", "new_password": "nova-senha-1"}).status_code == 422
    assert client.post("/me/password", headers=session,
                       json={"current_password": "senha-segura", "new_password": "nova-senha-1"}).status_code == 204
    assert client.post("/auth/logout", headers=session).status_code == 204
    assert client.get("/me", headers=session).status_code == 401
    assert client.post("/auth/login", json={"login": "ana", "password": "nova-senha-1"}).status_code == 200


def test_review_crud_and_slug(client, signup):
    headers = signup("ana")
    first = client.post("/reviews", headers=headers, json={"title": "Explicabilidade em Agentes"}).json()
    second = client.post("/reviews", headers=headers, json={"title": "Explicabilidade em agentes!"}).json()
    assert (first["name"], second["name"]) == ("explicabilidade-em-agentes", "explicabilidade-em-agentes-2")
    assert first["is_owner"] is True

    updated = client.patch(f"/reviews/{first['id']}", headers=headers, json={"description": "Nova descrição"})
    assert updated.json()["description"] == "Nova descrição"
    assert [item["id"] for item in client.get("/reviews", headers=headers).json()] == [first["id"], second["id"]]
    assert client.delete(f"/reviews/{second['id']}", headers=headers).status_code == 204
    assert client.get(f"/reviews/{second['id']}", headers=headers).status_code == 404


def test_non_members_cannot_see_review(client, review, signup):
    review_id, _ = review
    stranger = signup("estranho")
    assert client.get(f"/reviews/{review_id}", headers=stranger).status_code == 404
    assert client.patch(f"/reviews/{review_id}", headers=stranger, json={"title": "x"}).status_code == 404
    assert client.get("/reviews", headers=stranger).json() == []


def test_invite_by_email_for_person_without_account_then_accept(client, review, signup):
    review_id, owner = review
    invite = client.post(f"/reviews/{review_id}/invites", headers=owner, json={"email": "Bruno@Example.com"})
    assert invite.status_code == 201, invite.text
    assert invite.json()["has_account"] is False
    assert client.post(f"/reviews/{review_id}/invites", headers=owner,
                       json={"email": "bruno@example.com"}).status_code == 409

    bruno = signup("bruno", "bruno@example.com")
    pending = client.get("/invites", headers=bruno).json()
    assert [item["review"]["id"] for item in pending] == [review_id]
    assert client.get(f"/reviews/{review_id}", headers=bruno).status_code == 404

    accepted = client.post(f"/invites/{pending[0]['code']}/accept", headers=bruno)
    assert accepted.status_code == 200
    assert accepted.json()["is_owner"] is False
    assert [user["username"] for user in accepted.json()["co_authors"]] == ["bruno"]
    assert client.patch(f"/reviews/{review_id}", headers=bruno, json={"description": "editado"}).status_code == 200
    assert client.get("/invites", headers=bruno).json() == []
    assert client.post(f"/invites/{pending[0]['code']}/accept", headers=bruno).status_code == 409


def test_only_owner_manages_coauthors_and_coauthor_can_leave(client, review, signup):
    review_id, owner = review
    carla = signup("carla")
    code = client.post(f"/reviews/{review_id}/invites", headers=owner, json={"email": "carla@example.com"}).json()["code"]
    assert client.post(f"/invites/{code}/accept", headers=carla).status_code == 200

    assert client.post(f"/reviews/{review_id}/invites", headers=carla, json={"email": "x@example.com"}).status_code == 403
    assert client.delete(f"/reviews/{review_id}", headers=carla).status_code == 403
    assert client.get(f"/reviews/{review_id}/invites", headers=carla).status_code == 403
    assert client.post(f"/reviews/{review_id}/leave", headers=owner).status_code == 422

    assert client.post(f"/reviews/{review_id}/leave", headers=carla).status_code == 204
    assert client.get(f"/reviews/{review_id}", headers=carla).status_code == 404

    code = client.post(f"/reviews/{review_id}/invites", headers=owner, json={"email": "carla@example.com"}).json()["code"]
    client.post(f"/invites/{code}/accept", headers=carla)
    carla_id = client.get("/me", headers=carla).json()["id"]
    assert client.delete(f"/reviews/{review_id}/coauthors/{carla_id}", headers=owner).status_code == 204
    assert client.get(f"/reviews/{review_id}", headers=carla).status_code == 404


def test_reject_and_cancel_invites(client, review, signup):
    review_id, owner = review
    diego = signup("diego")
    first = client.post(f"/reviews/{review_id}/invites", headers=owner, json={"email": "diego@example.com"}).json()
    assert client.post(f"/invites/{first['code']}/accept", headers=signup("intruso")).status_code == 404
    assert client.post(f"/invites/{first['code']}/reject", headers=diego).json()["status"] == "rejected"
    assert client.get(f"/reviews/{review_id}", headers=diego).status_code == 404

    second = client.post(f"/reviews/{review_id}/invites", headers=owner, json={"email": "diego@example.com"}).json()
    assert client.delete(f"/reviews/{review_id}/invites/{second['id']}", headers=owner).status_code == 204
    assert client.get("/invites", headers=diego).json() == []
    statuses = [item["status"] for item in client.get(f"/reviews/{review_id}/invites", headers=owner).json()]
    assert statuses == ["rejected"]
