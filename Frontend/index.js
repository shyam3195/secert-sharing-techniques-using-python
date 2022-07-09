const express = require('express');
const app = express();
const path = require('path');
const router = express.Router();

router.get('/', function(req, res) {
    res.sendFile(path.join(__dirname + '/index.html'));
});

router.get('/login', function(req, res) {
    res.sendFile(path.join(__dirname + '/signin.html'));
})

router.get('/register', function(req, res) {
    res.sendFile(path.join(__dirname + '/signup.html'));
})


//add the router
app.use('/', router);
app.use('/scripts', express.static(__dirname + '/scripts/'));
app.listen(process.env.port || 3000);

console.log('Running at Port 3000');