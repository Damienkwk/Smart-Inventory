/**
 * Server side code.
 */
"use strict";
console.log("Starting...");
var express = require("express");
var bodyParser = require("body-parser");
var request = require("request");


var app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

const NODE_PORT = process.env.PORT || 3000;

app.use(express.static(__dirname + "/../client/"));

var api_key = 'key-f25acb40c99b4c98d5257b649087748a';
var domain = 'sandboxc2ebf44c040b4829b756fac08d658118.mailgun.org';
var mailgun = require('mailgun-js')({apiKey: api_key, domain: domain});

var list = [];

app.get('/api/getList', function(req,res){
    res.status(200).send(list)
});

app.get('/api/onClear', function(req,res){
    list = [];
    res.status(200).send(list)
});

app.post('/api/setList', function(req,res){
    console.log(req.body)
    list.push(req.body)
    console.log(list)
    res.status(200).send(list)
})

app.post('/api/email', function(req,res){

    var data = {
        from: 'Weight Scale App <weight@scale.com>',
        to: req.body.email,
        subject: 'Alert',
        text: req.body.selectedItem+' value has dropped below 3, Purchase order has been sent'
      };

      mailgun.messages().send(data, function (error, body) {
        console.log(body);
        res.status(200).send("Email Sent")
      });
    
})

app.get('/api/getData', function(req,res){

    request('http://localhost:4000/getVal', function (error, response, body) {
        if(error){
            res.status(500)
        }
        else{
            res.status(200).send(body)
            
        }
    });

});


app.get('/api/onTare', function(req,res){

    request('http://localhost:4000/setTare', function (error, response, body) {
        if(error){
            res.status(500)
        }
        else{
            res.status(200).send(body)
        }
    });

});


app.post('/api/onCount', function(req,res){

    console.log(req.body)

    request('http://localhost:4000/count='+JSON.stringify(req.body), function (error, response, body) {
        if(error){
            console.log(error)
        }
        else{
            res.status(200).send(body)
        }
    });


})


app.use(function (req, res) {
    res.send("<h1>Page not found</h1>");
});

app.listen(NODE_PORT, function () {
    console.log("Web App started at " + NODE_PORT);
});

module.exports = app



