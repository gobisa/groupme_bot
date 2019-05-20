import requests
r = requests.post("http://localhost:5000/incoming_message", data={
  "attachments": [],
  "avatar_url": "https://i.groupme.com/123456789",
  "created_at": 1302623328,
  "group_id": "1234567890",
  "id": "1234567890",
  "name": "John",
  "sender_id": "12345",
  "sender_type": "user",
  "source_guid": "GUID",
  "system": False,
  "text": "@bot patriotify",
  "user_id": "1234567890"
})
# And done.
print(r.text) # displays the result body.
