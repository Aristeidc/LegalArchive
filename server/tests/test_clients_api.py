import pytest

#-------------------------functions used-----------------------------
def post_client(client, **overrides):
    payload = {
        "full_name": " ΠΑτρικιός  ",
        "phone":"6900000000",
        "email":"old@example.com",
        "afm":"120120120",
        "address":"Random St 5, Random City",
        "notes":"random notes for you",
    }
    unknown = set(overrides) - set(payload)
    assert not unknown, f"unknown fields: {unknown}"

    payload = {**payload,**overrides}

    response = client.post("/clients",json=payload)
    assert response.is_success
    return response.json()

def without_updated_at(body):
    return {k: v for k, v in body.items() if k != "updated_at"}

#-------------------------get all test-------------------------------
def test_list_starts_empty(client):
    response = client.get("/clients")
    assert response.status_code ==200
    assert response.json()== []

def test_root_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "it works"}

#-------------------------post tests---------------------------------
def test_create_client(client):
    response = client.post("/clients",json={"full_name": " ΠΑτρικιός  ","phone":"6900000000"})
    assert response.is_success
    body =response.json()
    assert body["full_name"] == "ΠΑτρικιός"
    assert body["phone"] == "6900000000"
    assert body["email"] is None
    assert body["is_favorite"] is False
    assert "full_name_normalized" not in body
    assert isinstance(body["client_id"],int)

def test_create_returns_201(client):
    response =client.post("/clients", json={"full_name": "Νίκος Παπάς"})
    assert response.status_code ==201

#-------------------------post error tests--------------------------
@pytest.mark.parametrize("name", [
    "",
    "  ",
    "^^%",
])
def test_create_client_rejects(client,name):
    response = client.post("/clients",json={"full_name":name})
    assert response.status_code == 400

def test_create_client_no_name(client):
    response = client.post("/clients", json={})
    assert response.status_code == 422

def test_create_client_null_name(client):
    response = client.post("/clients", json={"full_name":None})
    assert response.status_code == 422

#--------------------------get by id tests------------------------------
def test_get_client_by_id(client):
    response_post = client.post("/clients",json={"full_name": " ΠΑτρικιός  ","phone":"6900000000"})
    assert response_post.is_success
    body = response_post.json()
    client_id= body["client_id"]
    response_get = client.get(f"/clients/{client_id}")
    assert response_get.status_code== 200
    assert response_get.json() == body

def test_get_client_missing_id(client):
    response = client.get("/clients/999")
    assert response.status_code== 404

def test_get_client_non_numeric_id(client):
    response = client.get("/clients/abc")
    assert response.status_code== 422

#-----------------------patch client tests-----------------------------
def test_patch_client_partial_update(client):
    post_body = post_client(client)
    client_id= post_body["client_id"]
    
    changes = {"email":"new@example.com"}
    response_patch =client.patch(f"/clients/{client_id}",json=changes)
    assert response_patch.is_success
    patched_body = response_patch.json()

    expectation = {**post_body, **changes}
    assert without_updated_at(patched_body) == without_updated_at(expectation)
    assert patched_body["updated_at"] >= post_body["updated_at"]
    
def test_patch_clears_field(client):
    post_body = post_client(client)
    client_id= post_body["client_id"]

    changes = {"email":None}
    response_patch =client.patch(f"/clients/{client_id}",json=changes)
    assert response_patch.is_success
    patched_body = response_patch.json()

    expectation = {**post_body, **changes}
    assert without_updated_at(patched_body) == without_updated_at(expectation)
    assert patched_body["updated_at"] >= post_body["updated_at"]
    assert patched_body["email"] is None

def test_patch_rename_client(client):
    post_body = post_client(client)
    client_id= post_body["client_id"]

    changes = {"full_name":" Τομ ο Γάτος  "}
    name_striped =changes["full_name"].strip()
    changes_striped = {"full_name":name_striped}
    response_patch =client.patch(f"/clients/{client_id}",json=changes)
    assert response_patch.is_success
    patched_body = response_patch.json()

    expectation = {**post_body, **changes_striped}
    assert without_updated_at(patched_body) == without_updated_at(expectation)
    assert patched_body["updated_at"] >= post_body["updated_at"]

    old_name = "πατρικιος"
    new_name = "τομ ο γατος"
    response_get_new= client.get("/clients",params={"name":new_name})
    assert response_get_new.is_success
    found = response_get_new.json()
    assert len(found) == 1
    assert found[0]["client_id"]==client_id
    
    response_get_old= client.get("/clients",params={"name":old_name})
    assert response_get_old.is_success
    assert response_get_old.json()==[]

def test_patch_favorite(client):
    post_body = post_client(client)
    client_id= post_body["client_id"]

    changes = {"is_favorite":True}
    response_patch =client.patch(f"/clients/{client_id}",json=changes)
    assert response_patch.is_success
    patched_body = response_patch.json()

    expectation = {**post_body, **changes}
    assert without_updated_at(patched_body) == without_updated_at(expectation)
    assert patched_body["updated_at"] >= post_body["updated_at"]

@pytest.mark.parametrize("changes",[
    {},
    {"full_name": None},
    {"full_name": ""},
    {"full_name": "   "},
    {"full_name": "^&&^"},
])
def test_patch_rejections(client, changes):
    post_body = post_client(client)
    client_id = post_body["client_id"]

    response_patch =client.patch(f"/clients/{client_id}",json=changes)
    assert response_patch.status_code == 400

    response_get = client.get(f"/clients/{client_id}")
    assert post_body == response_get.json()

def test_patch_client_missing_id(client):
    post_client(client)

    changes = {"is_favorite":True}
    response_patch =client.patch("/clients/999",json=changes)
    assert response_patch.status_code == 404

#--------------------Injections & Wildcard tests------------------------
def test_sql_inj_in_post(client):
    post_body = post_client(client, full_name="Robert'); DROP TABLE clients;--")
    client_id = post_body["client_id"]

    response_get = client.get(f"/clients/{client_id}")
    assert response_get.status_code== 200
    assert post_body == response_get.json()
    assert post_body["full_name"] == "Robert'); DROP TABLE clients;--"

@pytest.mark.parametrize("term",[
    "' OR '1'='1",
    "'1'='1",
    "%",
    "π_π"
])
def test_wildcard_injection_searches(client, term):
    post_client(client, full_name="Παπάς")
    
    response_get = client.get("/clients", params={"name":term})
    assert response_get.status_code== 200
    assert response_get.json()==[]

def test_patch_internal_column_write(client):
    post_body = post_client(client, full_name = " ΠΑτρικιος ")
    client_id = post_body["client_id"]

    changes = {"full_name_normalized": "hacked", "email":"new@example.com"}
    response_patch =client.patch(f"/clients/{client_id}",json=changes)
    assert response_patch.is_success
    patched_body = response_patch.json()

    expectation = {**post_body,"email":"new@example.com"}
    response_get_old = client.get("/clients", params={"name":"πατρικιος"})
    assert response_get_old.is_success
    found = response_get_old.json()
    assert len(found) == 1
    assert found[0]["client_id"]==client_id
    assert without_updated_at(patched_body) == without_updated_at(expectation)
    
    response_get_new = client.get("/clients", params={"name":"hacked"})
    assert response_get_new.is_success
    assert response_get_new.json()==[]

def test_sql_inj_in_patch(client):
    post_body = post_client(client)
    client_id = post_body["client_id"]

    changes = {"full_name; DROP TABLE clients": "x"}
    response_patch =client.patch(f"/clients/{client_id}",json=changes)
    assert response_patch.status_code == 400

    response_get = client.get(f"/clients/{client_id}")
    assert response_get.status_code== 200
    assert post_body == response_get.json()

#-----------------List ordering & Search behaviour---------------------
def test_alphabetical_order(client):
    post_client(client, full_name= "Ωμέγα")
    post_client(client, full_name= "αλφα")
    post_client(client, full_name= "Βητα")
    post_client(client, full_name= "δέλτα")

    response = client.get("/clients")
    assert response.status_code ==200
    found = response.json()

    assert [c["full_name"] for c in found] == ["αλφα", "Βητα", "δέλτα", "Ωμέγα"]

def test_favorite_order(client):
    post_client(client, full_name= "Ωμέγα")
    post_client(client, full_name= "αλφα") 
    post_client(client, full_name= "Βητα") 
    body_delta = post_client(client, full_name= "δέλτα")
    client_id = body_delta["client_id"]

    response_patch = client.patch(f"/clients/{client_id}",json={"is_favorite":True})
    assert response_patch.is_success

    response = client.get("/clients")
    assert response.status_code ==200
    found = response.json()

    assert [c["full_name"] for c in found] == ["δέλτα", "αλφα", "Βητα", "Ωμέγα"]


@pytest.mark.parametrize("term",[
    "Παπαδόπουλος Πάνος",
    pytest.param("Πάνος Παπαδόπουλος", marks=pytest.mark.xfail(strict=True, reason="order-independent search not built yet; planned post-v1.0")),
    "παπαδόπουλος πάνοσ",
    "Παπαδ",
    "Παπαδόπουλος",
    "Πάνος",
    "πα",
    "πουλ",
    "ΠΑΠΑΔΟΠΟΥΛΟΣ",
    "παπαδοπουλος    πανος",
])
def test_search_matching(client,term):
    body=post_client(client, full_name= "Παπαδόπουλος Πάνος")
    post_client(client, full_name= "Ιωάννου Μαρία")
    client_id = body["client_id"]

    response =  client.get("/clients", params={"name":term})
    assert response.is_success
    found = response.json()
    assert len(found) == 1
    assert found[0]["client_id"]==client_id

@pytest.mark.parametrize("term",[
    "por",
    "παπαδακης",
    "αρης",
    "Παπαδιπουλος",
    "Πάναγιώτης",
    "papadopoulos",
    "παπαδοπουλοσπανος",
])
def test_search_non_matching(client,term):
    post_client(client, full_name= "Παπαδόπουλος Πάνος")

    response =  client.get("/clients", params={"name":term})
    assert response.is_success
    assert response.json() == []

#-------------------------Delete tests-------------------------------
def test_delete_right_client(client):
    body=post_client(client, full_name= "Παπαδόπουλος Πάνος")
    remain = post_client(client, full_name= "Ιωάννου Μαρία")
    client_id = body["client_id"]

    response_del = client.delete(f"/clients/{client_id}")
    assert response_del.status_code == 204

    response_get = client.get(f"/clients/{client_id}")
    assert response_get.status_code == 404

    search = client.get("/clients", params={"name":"Παπαδόπουλος Πάνος"})
    assert search.is_success
    assert search.json() == []

    response_get_all = client.get("/clients")
    assert response_get_all.is_success
    found = response_get_all.json()
    assert len(found) == 1
    assert found[0]["client_id"]==remain["client_id"]

def test_double_delete(client):
    body=post_client(client, full_name= "Παπαδόπουλος Πάνος")
    remain = post_client(client, full_name= "Ιωάννου Μαρία")
    client_id = body["client_id"]

    response_del = client.delete(f"/clients/{client_id}")
    assert response_del.status_code == 204

    response_second_delete = client.delete(f"/clients/{client_id}")
    assert response_second_delete.status_code == 404

    response_get_all = client.get("/clients")
    assert response_get_all.is_success
    found = response_get_all.json()
    assert len(found) == 1
    assert found[0]["client_id"]==remain["client_id"]

def test_delete_missing_id(client):
    post_client(client, full_name= "Παπαδόπουλος Πάνος")
    post_client(client, full_name= "Ιωάννου Μαρία")

    response_del = client.delete("/clients/999")
    assert response_del.status_code == 404

    response_get_all = client.get("/clients")
    assert response_get_all.is_success
    found = response_get_all.json()
    assert [c["full_name"] for c in found] == ["Ιωάννου Μαρία", "Παπαδόπουλος Πάνος"]

def test_delete_non_numeric(client):
    post_client(client, full_name= "Παπαδόπουλος Πάνος")
    post_client(client, full_name= "Ιωάννου Μαρία")

    response_del = client.delete("/clients/abc")
    assert response_del.status_code == 422

    response_get_all = client.get("/clients")
    assert response_get_all.is_success
    found = response_get_all.json()
    assert len(found) == 2
    assert [c["full_name"] for c in found] == ["Ιωάννου Μαρία", "Παπαδόπουλος Πάνος"]

