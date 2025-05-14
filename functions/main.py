import firebase_admin
from firebase_admin import credentials, firestore

# Path to your service account key JSON file
cred = credentials.Certificate('C:/Users/Kased/Binance_Trading_AI_Bot_Working/Binance_Trading_AI_Bot/Functions/c:\Users\kased\Binance_Trading_AI_Bot_Working\Binance_Trading_AI_Bot\staging-binance-trading-ai-bot-firebase-adminsdk-fbsvc-6f0c5df377.json)
firebase_admin.initialize_app(cred)

db = firestore.client()

# Create or update a document in the 'locations' collection with the id 'nam5'
doc_ref = db.collection('locations').document('nam5')
doc_ref.set({
    'name': 'nam5',
    'description': 'Test location data for nam5',
    'latitude': 0.0,
    'longitude': 0.0
})
print("Document 'nam5' successfully added to Firestore.")