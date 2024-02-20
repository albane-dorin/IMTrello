import TrelloClass

trello = TrelloClass.Trello([])

trello.create_account()

print(trello.can_connect_user("albane", "pass"))
print(trello.can_connect_user("albane", "pass2"))