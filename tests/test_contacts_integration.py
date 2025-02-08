import pytest


@pytest.mark.asyncio
async def test_read_contacts(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/api/contacts/", headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()

    # We expect 4 contacts seeded in the test database
    assert len(data) == 4
    assert data[0]["first_name"] in ["Alice", "Bob", "Charlie", "Dana"]


@pytest.mark.asyncio
async def test_read_contact(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/api/contacts/1", headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["first_name"] == "Alice"
    assert data["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_read_contacts_with_birthdays(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.get("/api/contacts/birthdays", headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()

    # Only Alice and Dana have birthdays within the next 7 days
    assert len(data) == 2
    assert data[0]["first_name"] in ["Alice", "Dana"]
    assert data[1]["first_name"] in ["Alice", "Dana"]


@pytest.mark.asyncio
async def test_create_contact(client, get_token):
    new_contact = {
        "first_name": "Eve",
        "last_name": "Williams",
        "email": "eve@example.com",
        "phone": "+380671234568",
        "birth_date": "2000-01-01",
    }

    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.post("/api/contacts/", json=new_contact, headers=headers)

    assert response.status_code == 201, response.text
    data = response.json()

    assert data["first_name"] == "Eve"
    assert data["email"] == "eve@example.com"


@pytest.mark.asyncio
async def test_update_contact(client, get_token):
    updated_contact = {
        "first_name": "Allison",
        "last_name": "Smith",
        "email": "allison@example.com",
        "phone": "+380671234567",
    }

    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.put("/api/contacts/1", json=updated_contact, headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["first_name"] == "Allison"
    assert data["email"] == "allison@example.com"


@pytest.mark.asyncio
async def test_remove_contact(client, get_token):
    headers = {"Authorization": f"Bearer {get_token}"}
    response = client.delete("/api/contacts/1", headers=headers)

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["first_name"] == "Allison"
    assert data["email"] == "allison@example.com"

    # Verify that the contact no longer exists
    response = client.get("/api/contacts/1", headers=headers)
    assert response.status_code == 404, response.text
