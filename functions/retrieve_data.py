# Retrieve data from Firestore
doc_ref = db.collection("trading_data").document("example_trade")
doc = doc_ref.get()

if doc.exists:
    print("Trade Data:", doc.to_dict())
else:
    print("No such document found.")