const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const app = express();
admin.initializeApp();

const db = admin.firestore();

// Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Admin Login route
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const ADMIN_USERNAME = 'admin';
    const ADMIN_PASSWORD = 'admin123';

    if (username === ADMIN_USERNAME && password === ADMIN_PASSWORD) {
        res.status(200).send('Login Successful');
    } else {
        res.status(401).send('Unauthorized');
    }
});

// Get list of products
app.get('/admin/products', async (req, res) => {
    const productsRef = db.collection('products');
    const snapshot = await productsRef.get();
    const products = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
    }));
    res.status(200).json(products);
});

// Add product route
app.post('/admin/add-product', async (req, res) => {
    const { name, description, price, image_url } = req.body;

    if (!name || !description || !price) {
        return res.status(400).send("Missing required fields");
    }

    try {
        await db.collection('products').add({
            name, description, price: parseFloat(price), image_url
        });
        res.status(201).send('Product added successfully');
    } catch (error) {
        res.status(500).send('Error adding product');
    }
});

// Serve the app using Firebase Functions
exports.app = functions.https.onRequest(app);
