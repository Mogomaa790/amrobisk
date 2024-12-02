const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

// Example HTTP function
exports.helloWorld = functions.https.onRequest((req, res) => {
    res.send("Hello, world!");
});

// Example Firestore function (triggered when a new document is added)
exports.addedProduct = functions.firestore
    .document('products/{productId}')
    .onCreate((snap, context) => {
        const newValue = snap.data();
        console.log('Product added:', newValue);
        return null;
    });

